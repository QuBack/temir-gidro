from pathlib import Path
import base64
import re

root = Path(__file__).resolve().parent
component = (root / "wordpress.html").read_text(encoding="utf-8")
# Embed full images for the stage and small derivatives for gallery buttons.
component = re.sub(r'\s+(?:srcset|data-srcset|sizes)="[^"]*"', "", component)
component = component.replace("        mainImage.srcset = button.dataset.srcset;\n", "")
cache = {}
def inline(match):
    filename = match.group(1)
    if filename.endswith("-1200.webp"):
        filename = filename.replace("-1200.webp", ".webp")
    if filename not in cache:
        data = (root / "images" / filename).read_bytes()
        assert data[:4] == b"RIFF" and data[8:12] == b"WEBP"
        cache[filename] = "data:image/webp;base64," + base64.b64encode(data).decode("ascii")
    return cache[filename]

component = re.sub(r'__TG_IMAGES_URL__/([a-z0-9-]+\.webp)', inline, component)
component = re.sub(
    r"Загрузите все WebP-файлы.*?реальным общим URL каталога загрузок без завершающего слеша\.",
    "Все изображения WebP встроены в HTML. Загрузка в медиатеку и замена URL не требуются.",
    component, count=1, flags=re.S)
assert "__TG_IMAGES_URL__" not in component
assert len(cache) == 7  # four originals and three small thumbnails, all from supplied images
assert len(re.findall(r'\ssrc="data:image/webp;base64,', component)) == 5
assert component.count('data-src="data:image/webp;base64,') == 3
assert "mainImage.srcset" not in component

output = root / "wordpress-webp-inline.html"
output.write_text(component, encoding="utf-8")
preview = (root / "preview.html").read_text(encoding="utf-8")
start = preview.index("<!--")
end = preview.rindex("</main>")
preview = preview[:start] + component + preview[end:]
(root / "preview-webp-inline.html").write_text(preview, encoding="utf-8")
print("Embedded WebP HTML: " + str(output))
print("File size: " + str(output.stat().st_size) + " bytes")
print("Four attached images embedded; no external image URLs.")

