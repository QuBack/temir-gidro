"""Build a 4X render from the 3X one: one more scissor pair, longer cylinders.

The scissor stack repeats every 403 px (joint row to joint row), so pixels hidden
by the cylinders are restored from the same spot one pair above or below.
"""
import math
import sys

from PIL import Image, ImageDraw

SRC = r"C:\python-projects\temir-gidro\static\img\catalog\nozhnichnyj-podemnik-3x-800.webp"
OUT = sys.argv[1]

im = Image.open(SRC).convert("RGBA")
W, H = im.size
src = im.load()
clean = im.copy()
px = clean.load()

TOP, BOT = 437, 840  # two rows of joints
P = BOT - TOP
# Cylinder axes: (top x, top y, bottom x, bottom y).
CYLS = [(145, 370, 378, 915), (280, 365, 492, 920)]
HALF = 24


def near(x, y, c):
    x1, y1, x2, y2 = c
    dx, dy = x2 - x1, y2 - y1
    t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
    if not 0.05 < t < 0.95:  # keep the clevises at both ends
        return False
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy)) <= (HALF if x1 < 200 else HALF + 8)


for y in range(340, 940):
    for x in range(100, 540):
        if any(near(x, y, c) for c in CYLS):
            sy = y + P if y + P < 1110 else y - P  # avoid the base railing
            px[x, y] = src[x, sy]

out = Image.new("RGBA", (W, H + P), (0, 0, 0, 0))
out.paste(clean.crop((0, 0, W, BOT)), (0, 0))
out.paste(clean.crop((0, TOP, W, BOT)), (0, BOT))
out.paste(clean.crop((0, BOT, W, H)), (0, BOT + P))

# Longer cylinders, behind the arms.
layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
for x1, y1, x2, y2 in CYLS:
    y2 += P
    k = 0.48
    sx, sy = x1 + (x2 - x1) * k, y1 + (y2 - y1) * k
    d.line([(x1, y1), (sx, sy)], fill=(140, 146, 150, 255), width=11)
    d.line([(x1 - 2, y1), (sx - 2, sy)], fill=(222, 226, 228, 255), width=4)
    d.line([(sx, sy), (x2, y2)], fill=(26, 28, 30, 255), width=24)
    d.line([(sx - 6, sy), (x2 - 6, y2)], fill=(80, 85, 90, 255), width=4)
    d.line([(sx, sy - 5), (sx + 2, sy + 5)], fill=(55, 59, 63, 255), width=28)
result = Image.alpha_composite(layer, out)
result.save(OUT)
print(result.size)
