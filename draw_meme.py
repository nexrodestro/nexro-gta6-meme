#!/usr/bin/env python3
"""Rebuild the MISSION PASSED meme (meme.png) from the base scene.

Provenance script: this is how the entry image was made. It takes the
Vice City ghost scene, adds the GTA-style title, the punchline subtitle,
and the bottom bar with the 13-year wait line plus the make.fun pitch
with the real ghost mark. Run from the repo root; the scene and the
press mark live one level up, outside the repo.

Requires Pillow (PIL) and DejaVu Sans Bold, both present on the build box.
Output is a 1080x1080 PNG, palette-quantized to stay under 1 MB.
"""
from PIL import Image, ImageDraw, ImageFont

SCENE_PATH = "../scenes/media-generation-gta6-mission-scene-0-b7fafacb-22ae-49f5-a1f7-8272f01ed439.png"
MARK_PATH = "../press/mark-1024.png"
OUTPUT_PATH = "meme.png"
CANVAS = 1080
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
GOLD = (255, 233, 168)
MAGENTA = (255, 0, 168)


def fitted(draw, text, start_px, max_width, stroke):
    """Largest bold size at which `text` fits inside max_width."""
    size = start_px
    while size > 20:
        face = ImageFont.truetype(FONT_PATH, size)
        width = draw.textbbox((0, 0), text, font=face, stroke_width=stroke)[2]
        if width <= max_width:
            return face
        size -= 2
    return ImageFont.truetype(FONT_PATH, 20)


def centered(draw, cx, y, text, face, fill, stroke):
    box = draw.textbbox((0, 0), text, font=face, stroke_width=stroke)
    draw.text((cx - (box[2] - box[0]) / 2, y), text, font=face, fill=fill,
              stroke_width=stroke, stroke_fill=(0, 0, 0))


def build():
    base = Image.open(SCENE_PATH).convert("RGB")
    base = base.resize((CANVAS, CANVAS), Image.LANCZOS)
    pen = ImageDraw.Draw(base)

    title = fitted(pen, "MISSION PASSED", 128, CANVAS - 60, 10)
    centered(pen, CANVAS // 2, 30, "MISSION PASSED", title, GOLD, 10)

    sub = fitted(pen, "THE WAIT WAS THE HARDEST MISSION", 52, CANVAS - 80, 6)
    centered(pen, CANVAS // 2, 178, "THE WAIT WAS THE HARDEST MISSION",
             sub, (255, 255, 255), 6)

    pen.rectangle([0, 898, CANVAS, CANVAS], fill=(0, 0, 0))
    pen.rectangle([0, 898, CANVAS, 904], fill=MAGENTA)

    mid = fitted(pen, "WAITED 13 YEARS FOR GTA 6", 62, CANVAS - 60, 5)
    centered(pen, CANVAS // 2, 916, "WAITED 13 YEARS FOR GTA 6", mid,
             (255, 255, 255), 5)

    mark = Image.open(MARK_PATH).convert("RGBA").resize((72, 72), Image.LANCZOS)
    base.paste(mark, (52, 992), mark)
    pen.text((140, 1000), "MY AGENT GOT PAID ON make.fun",
             font=ImageFont.truetype(FONT_PATH, 44), fill=MAGENTA)

    # Palette-quantize: photographic PNGs are ~1.3 MB at 1080px; 256 colours
    # with dithering keeps the text crisp and the file under 1 MB.
    small = base.convert("RGB").quantize(
        colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG
    ).convert("RGB")
    small.save(OUTPUT_PATH, optimize=True, compress_level=9)
    print(f"wrote {OUTPUT_PATH} ({CANVAS}x{CANVAS})")


if __name__ == "__main__":
    build()
