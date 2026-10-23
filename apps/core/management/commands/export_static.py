"""Export the site as plain HTML files for hosting without Python (Timeweb shared hosting).

    DEBUG=False SITE_URL=https://temir-gidro.ru python manage.py export_static dist

Every page from the sitemap, plus the request form, the thank-you page, the privacy policy,
robots.txt, sitemap.xml, favicon.ico and the 404 page, is rendered by Django and saved as
<path>/index.html; collected static files go to static/. The lead form posts to
zayavka/send.php (deploy/static/send.php), which mails the lead; .htaccess turns on HTTPS,
the 301 redirects from apps/core/redirects.py and the 404 page. Lost on such hosting: the
admin, the leads in a database and Telegram — leads come by email only.
"""

import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command
from django.test import Client
from django.test.utils import override_settings

from apps.core.redirects import OLD_TO_NEW

DEPLOY = Path(settings.BASE_DIR) / "deploy" / "static"
EXTRA = ["/", "/zayavka/", "/zayavka/spasibo/", "/politika-konfidencialnosti/"]
FILES = ["/robots.txt", "/sitemap.xml", "/favicon.ico"]


class Command(BaseCommand):
    help = "Render the whole site into static HTML files (see the module docstring)."

    def add_arguments(self, parser):
        parser.add_argument("out", help="output folder, emptied first")

    def handle(self, out, **options):
        if settings.DEBUG:
            raise CommandError("Run with DEBUG=False: only then the static files get hashed names.")
        out = Path(out).resolve()
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)

        call_command("collectstatic", interactive=False, clear=True, verbosity=0)
        self._copy_static(Path(settings.STATIC_ROOT), out / "static")

        host = urlsplit(settings.SITE_URL).hostname
        with override_settings(ALLOWED_HOSTS=[host, "testserver"], SECURE_SSL_REDIRECT=False):
            client = Client(HTTP_HOST=host)
            sitemap = self._get(client, "/sitemap.xml").decode()
            pages = {urlsplit(u).path for u in re.findall(r"<loc>([^<]+)</loc>", sitemap)}
            pages = sorted(pages | set(EXTRA))
            for path in pages:
                self._write(out / path.lstrip("/") / "index.html", self._get(client, path))
            for path in FILES:
                self._write(out / path.lstrip("/"), self._get(client, path, follow=True))
            missing = client.get("/__no-such-page__/", secure=True)
            if missing.status_code != 404:
                raise CommandError(f"404 page answered {missing.status_code}")
            self._write(out / "404.html", missing.content)

        (out / "zayavka").mkdir(exist_ok=True)
        shutil.copy(DEPLOY / "send.php", out / "zayavka" / "send.php")
        (out / ".htaccess").write_text(self._htaccess(host), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"{len(pages)} pages, {len(FILES)} files, 404 -> {out}"))

    def _copy_static(self, src, dst):
        """Only what pages use: the hashed copies from the manifest, without the admin and the
        .gz/.br twins (Apache compresses itself); the 3D viewer's Draco decoder is loaded by its
        plain name at runtime, so vendor/ is kept whole."""
        import json

        hashed = set(json.loads((src / "staticfiles.json").read_text(encoding="utf-8"))["paths"].values())
        for f in src.rglob("*"):
            rel = f.relative_to(src).as_posix()
            if f.is_dir() or f.suffix in (".gz", ".br") or rel.startswith("admin/"):
                continue
            if rel in hashed or rel.startswith("vendor/"):
                (dst / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst / rel)

    def _get(self, client, path, follow=False):
        response = client.get(path, secure=True, follow=follow)
        if response.status_code != 200:
            raise CommandError(f"{path} answered {response.status_code}")
        if getattr(response, "streaming", False):
            return b"".join(response.streaming_content)
        return response.content

    def _write(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def _htaccess(self, host):
        rules = []
        for old, new in OLD_TO_NEW.items():
            # Anchored, with or without the trailing slash; old paths may be Cyrillic.
            rules.append(f'RewriteRule "^{re.escape(old.lstrip("/"))}/?$" "{new}" [R=301,L,NE,NC]')
        template = (DEPLOY / "htaccess").read_text(encoding="utf-8")
        return template.replace("{{HOST}}", host).replace("{{REDIRECTS}}", "\n".join(rules))
