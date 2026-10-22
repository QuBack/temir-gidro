from pathlib import Path
import re
import json

root = Path(__file__).resolve().parent
reference = Path(r"C:\Users\user\Downloads\Подъемники для окрасочных камер 2D - ТЕМИР ГИДРО.html").read_text(encoding="utf-8-sig")
reference = reference[reference.index('id="tg-paint-lift-2d"'):]
faces = []
seen = set()
for face in re.findall(r"@font-face\s*\{.*?\}", reference, re.S):
    if "font-family: 'Manrope'" not in face:
        continue
    source_match = re.search(r"url\((data:[^)]+)\)", face)
    if not source_match or source_match.group(1) in seen:
        continue
    seen.add(source_match.group(1))
    face = face.replace("font-family: 'Manrope'", "font-family: 'TG Paint Lift Manrope'")
    face = re.sub(r"font-weight:\s*\d+;", "font-weight: 500 800;", face)
    faces.append(face)
assert len(faces) == 6

original = (root / "wordpress-webp-inline.html").read_text(encoding="utf-8")
font_css = "\n    /* Manrope embedded from the supplied 2D reference; no external font requests. */\n" + "\n".join(faces) + "\n"
fixed = original.replace("<style>", "<style>" + font_css, 1)
fixed = fixed.replace("font-family: 'Manrope', 'IBM Plex Sans', sans-serif;",
                      "font-family: 'TG Paint Lift Manrope', 'Manrope', 'IBM Plex Sans', sans-serif;")
fixed = fixed.replace("font-family: 'IBM Plex Sans', 'Manrope', -apple-system",
                      "font-family: 'IBM Plex Sans', 'TG Paint Lift Manrope', 'Manrope', -apple-system")
fixed = fixed.replace("font-size: 16px;\n      line-height: 1.6;",
                      "font-size: 16px;\n      font-weight: 400;\n      line-height: 1.6;", 1)
fixed = fixed.replace("</style>", """
    /* Match the heading spacing in the supplied 2D page. */
    #tg-paint-lift-3d .tg-section-title { line-height: 1.2; }
  </style>""", 1)
# Verify that all supplied images and their thumbnails remain byte-for-byte unchanged.
pattern = r"data:image/webp;base64,[A-Za-z0-9+/=]+"
assert re.findall(pattern, original) == re.findall(pattern, fixed)
output = root / "wordpress-webp-inline-fonts-fixed.html"
output.write_text(fixed, encoding="utf-8")
preview = (root / "preview-webp-inline.html").read_text(encoding="utf-8")
start, end = preview.index("<!--"), preview.rindex("</main>")
(root / "preview-webp-inline-fonts-fixed.html").write_text(preview[:start] + fixed + preview[end:], encoding="utf-8")
print(json.dumps(dict(file=str(output),font_subsets=len(faces),bytes=output.stat().st_size,images_unchanged=True),ensure_ascii=False))

