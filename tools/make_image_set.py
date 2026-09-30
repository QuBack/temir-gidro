"""Turn one source image into the AVIF + WebP set that {% picture %} expects.

    python tools/make_image_set.py SOURCE static/img/<dir>/<name> 768 1280 1920

writes static/img/<dir>/<name>-<width>.avif and .webp for every width (never
upscaled) and prints the img(...) line for apps/core/catalog.py.
"""

import sys
from pathlib import Path

from PIL import Image

AVIF_QUALITY = 55
WEBP_QUALITY = 78


def main(source: str, target: str, widths: list[int]) -> None:
    image = Image.open(source)
    image = image.convert("RGBA" if image.mode in ("RGBA", "LA", "P") else "RGB")
    out = Path(target)
    out.parent.mkdir(parents=True, exist_ok=True)
    made = []
    for width in sorted(widths):
        width = min(width, image.width)
        if made and made[-1][0] == width:
            continue
        height = round(image.height * width / image.width)
        resized = image.resize((width, height), Image.LANCZOS)
        resized.save(f"{out}-{width}.avif", quality=AVIF_QUALITY)
        resized.save(f"{out}-{width}.webp", quality=WEBP_QUALITY, method=6)
        made.append((width, height))
    for width, _ in made:
        sizes = [Path(f"{out}-{width}.{ext}").stat().st_size // 1024 for ext in ("avif", "webp")]
        print(f"{out}-{width}: avif {sizes[0]} KB, webp {sizes[1]} KB")
    src = out.relative_to("static/img").as_posix() if out.is_relative_to("static/img") else out.as_posix()
    widths_py = ", ".join(str(w) for w, _ in made)
    print(f'img("{src}", ({made[-1][0]}, {made[-1][1]}), widths=({widths_py}{"," if len(made) == 1 else ""}))')


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], [int(w) for w in sys.argv[3:]])
