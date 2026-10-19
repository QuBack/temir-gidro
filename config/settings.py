"""Temir-Gidro settings. All environment-specific values come from env / .env."""

from pathlib import Path

import environ
from django.utils.csp import CSP
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

DEBUG = env.bool("DEBUG", default=False)
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Canonical origin of the site, without trailing slash. Used for canonical,
# hreflang, Open Graph, sitemap and robots.txt — never derived from the request
# Host header so that mirrors and IP access can't produce foreign canonicals.
SITE_URL = env("SITE_URL", default="http://localhost:8000").rstrip("/")
CSRF_TRUSTED_ORIGINS = [SITE_URL]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "apps.core",
    "apps.leads",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    # ETag → 304 for unchanged pages (Yandex recommends If-Modified-Since support).
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.leads.middleware.UtmCaptureMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site",
            ],
        },
    },
]

# Local dev without Docker falls back to SQLite; compose and production use PostgreSQL.
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n -------------------------------------------------------------------
# Russian lives at the root (/), other languages under a prefix (/en/, /kk/ …).
# A language is published only when listed in SITE_LANGUAGES: half-translated
# versions would be indexed as thin/duplicate content, so they stay off until ready.
AVAILABLE_LANGUAGES = {
    "ru": _("Русский"),
    "kk": _("Қазақша"),
    "ky": _("Кыргызча"),
    "uz": _("Oʻzbekcha"),
    "en": _("English"),
}
LANGUAGE_CODE = "ru"
LANGUAGES = [
    (code, AVAILABLE_LANGUAGES[code])
    for code in env.list("SITE_LANGUAGES", default=["ru"])
    if code in AVAILABLE_LANGUAGES
]
LOCALE_PATHS = [BASE_DIR / "locale"]
USE_I18N = True
USE_TZ = True
TIME_ZONE = env("TIME_ZONE", default="Europe/Moscow")

# --- Static & media -----------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = env.path("MEDIA_ROOT", default=BASE_DIR / "media")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Hashed file names + gzip/brotli → static can be cached "forever".
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
# In development the names aren't hashed, so a year-long cache would keep stale JS and CSS.
WHITENOISE_MAX_AGE = 0 if DEBUG else 31536000
WHITENOISE_MIMETYPES = {".glb": "model/gltf-binary"}  # 3D models of the lifts

# --- Security -------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

# HTTPS=False only for a demo server reached by IP over plain HTTP (deploy/install.sh
# without a domain): no HTTPS redirect, no HSTS, cookies work without TLS.
HTTPS = env.bool("HTTPS", default=True)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=HTTPS)
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 365 if HTTPS else 0)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = HTTPS
    SESSION_COOKIE_SECURE = HTTPS
    CSRF_COOKIE_SECURE = HTTPS

# Yandex.Metrika needs its script host, its pixel/collect endpoints and webvisor
# frames; everything else is first-party. No inline scripts at all.
# The 3D viewer (static/vendor/model-viewer) decodes Draco meshes with WebAssembly in a
# worker started from a blob: URL, hands the model's textures over as blob: URLs and
# styles its shadow DOM with one fixed <style> block, allowed by its hash
# (tests/test_models.py recomputes it from the vendored file: update both on upgrade).
_METRIKA = ["https://mc.yandex.ru", "https://mc.yandex.com", "https://yastatic.net"]
MODEL_VIEWER_STYLE_HASH = "'sha256-F7kvx28zBT3UUQL/hTOYst+55RSmqyCY3muSCYmt6A4='"
SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF, CSP.WASM_UNSAFE_EVAL, *_METRIKA],
    "worker-src": [CSP.SELF, "blob:"],
    "style-src": [CSP.SELF, MODEL_VIEWER_STYLE_HASH],
    "img-src": [CSP.SELF, "data:", "blob:", *_METRIKA],
    "connect-src": [CSP.SELF, "blob:", *_METRIKA],
    "frame-src": [*_METRIKA, "https://yandex.ru"],  # Yandex Maps widget on the contacts page
    "font-src": [CSP.SELF],
    "form-action": [CSP.SELF],
    "frame-ancestors": [CSP.NONE],
    "base-uri": [CSP.SELF],
    "object-src": [CSP.NONE],
}

# Admin lives on a non-guessable path.
ADMIN_URL = env("ADMIN_URL", default="admin/")

# --- Cache (rate limiting of the lead form) ------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}

# --- SEO / integrations ------------------------------------------------------
# False on staging/test servers: robots.txt closes the whole site and every page
# gets <meta name="robots" content="noindex">.
SEO_INDEXING = env.bool("SEO_INDEXING", default=True)
YANDEX_VERIFICATION = env("YANDEX_VERIFICATION", default="")
GOOGLE_VERIFICATION = env("GOOGLE_VERIFICATION", default="")
YANDEX_METRIKA_ID = env("YANDEX_METRIKA_ID", default="")
# IndexNow (Yandex, Bing): 8–128 letters/digits/dashes; empty — no key file, no pings.
INDEXNOW_KEY = env("INDEXNOW_KEY", default="")

# --- Leads -------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID", default="")
# Behind Caddy/nginx the client IP comes from X-Forwarded-For.
USE_X_FORWARDED_FOR = env.bool("USE_X_FORWARDED_FOR", default=False)
LEAD_MIN_FILL_SECONDS = env.int("LEAD_MIN_FILL_SECONDS", default=3)
LEAD_RATE_LIMIT = env.int("LEAD_RATE_LIMIT", default=5)  # submissions per IP per window
LEAD_RATE_WINDOW = env.int("LEAD_RATE_WINDOW", default=600)  # seconds

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}
