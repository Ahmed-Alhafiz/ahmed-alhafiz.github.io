#!/usr/bin/env python3
"""Generate 1200×630 Arabic and English social cards for dossier 11.

The cards use only Pillow, DejaVu Sans and libraqm. Their design mirrors the
published analytical contribution rather than the forthcoming novel cover:
a seven-stage fear–certainty–authority chain interrupted by a green safety
route. This keeps the share image informative, reproducible and non-spoiling.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

WIDTH, HEIGHT = 1200, 630
NAVY = "#0b1724"
NAVY_2 = "#142c3c"
PAPER = "#f4f0e7"
INK = "#17202a"
COPPER = "#bd704e"
COPPER_LIGHT = "#f0ad85"
BLUE = "#2b6076"
GREEN = "#23634b"
WHITE = "#fffdf8"
MUTED = "#bdcbd4"
SOFT = "#8fa2ae"
LINE = "#356377"
BORDER = "#d8d0c4"
RED = "#6d3942"

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/social"
REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = BOLD if bold else REGULAR
    if not path.exists():
        raise FileNotFoundError(f"Required reproducible font is missing: {path}")
    return ImageFont.truetype(str(path), size)


def ar(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    *,
    size: int,
    fill: str,
    anchor: str = "ra",
    bold: bool = False,
) -> None:
    draw.text(
        xy,
        text,
        font=font(size, bold=bold),
        fill=fill,
        anchor=anchor,
        direction="rtl",
        language="ar",
    )


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: str,
    *,
    outline: str | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def chain_panel(draw: ImageDraw.ImageDraw, *, arabic: bool) -> None:
    rounded(draw, (65, 145, 515, 555), 27, PAPER, outline=BORDER, width=2)
    if arabic:
        ar(draw, (474, 186), "سلسلة الخوف–اليقين–السلطة", size=22, fill=INK, bold=True)
        labels = ["إشارة ملتبسة", "فراغ تفسيري", "خوف عائلي", "يقين مبكر", "نقل السلطة", "تآكل الموافقة", "تأخر أو ضرر"]
    else:
        draw.text((105, 174), "FEAR–CERTAINTY–AUTHORITY", font=font(18, bold=True), fill=INK)
        labels = ["Ambiguous signal", "Interpretive vacuum", "Family threat", "Premature closure", "Authority transfer", "Consent erosion", "Delay or harm"]
    draw.line((105, 211, 474, 211), fill=COPPER, width=3)

    y = 246
    for number, label in enumerate(labels, 1):
        color = RED if number == 7 else (COPPER if number % 2 else BLUE)
        draw.ellipse((105, y - 18, 141, y + 18), fill=color)
        draw.text((123, y), str(number), font=font(15, bold=True), fill=WHITE, anchor="mm")
        if arabic:
            ar(draw, (470, y), label, size=17, fill=INK, bold=True)
        else:
            draw.text((158, y), label, font=font(16, bold=True), fill=INK, anchor="lm")
        if number < 7:
            draw.line((123, y + 20, 123, y + 31), fill=LINE, width=2)
        y += 43

    rounded(draw, (100, 522, 480, 551), 14, GREEN)
    if arabic:
        ar(draw, (290, 537), "يمكن قطع السلسلة في كل مرحلة", size=14, fill=WHITE, anchor="mm", bold=True)
    else:
        draw.text((290, 537), "Interrupt the cascade at every stage", font=font(13, bold=True), fill=WHITE, anchor="mm")


def draw_arabic() -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(image)
    draw.ellipse((740, -250, 1340, 350), outline=LINE, width=1)
    draw.ellipse((830, -160, 1250, 260), outline=LINE, width=1)
    draw.polygon([(545, 0), (1200, 0), (1200, 630), (815, 630)], fill=NAVY_2)

    ar(draw, (1132, 67), "أحمد الحافظ", size=25, fill=WHITE, bold=True)
    draw.text((1132, 104), "Ahmed Alhafiz", font=font(15), fill=MUTED, anchor="ra")
    rounded(draw, (65, 55, 328, 96), 21, COPPER)
    ar(draw, (196, 76), "ملف بحثي ثنائي اللغة", size=17, fill=WHITE, anchor="mm", bold=True)

    chain_panel(draw, arabic=True)

    ar(draw, (1130, 195), "حين يحكم الخوف", size=47, fill=WHITE, bold=True)
    ar(draw, (1130, 270), "قبل التشخيص", size=47, fill=WHITE, bold=True)
    ar(draw, (1130, 342), "كيف يتحول الغموض إلى", size=27, fill=COPPER_LIGHT, bold=True)
    ar(draw, (1130, 390), "سلطة وإكراه داخل الأسرة؟", size=27, fill=COPPER_LIGHT, bold=True)
    draw.line((565, 465, 1130, 465), fill=LINE, width=2)
    ar(draw, (1130, 512), "14 ادعاءً · 19 مصدرًا · ملحق أدلة مفتوح", size=18, fill=MUTED, bold=True)
    ar(draw, (1130, 551), "السلامة التشخيصية · الموافقة · الدعم الطوعي", size=16, fill=SOFT)
    ar(draw, (1130, 597), "مراجعة اختصاصية خارجية: لم تتم بعد", size=14, fill="#d9a9b1")

    path = OUTPUT / "diagnostic-uncertainty-family-fear-ar.png"
    image.save(path, format="PNG", optimize=True)
    return path


def draw_english() -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(image)
    draw.ellipse((-140, -250, 460, 350), outline=LINE, width=1)
    draw.ellipse((-50, -160, 370, 260), outline=LINE, width=1)
    draw.polygon([(0, 0), (655, 0), (385, 630), (0, 630)], fill=NAVY_2)

    rounded(draw, (65, 55, 390, 96), 21, COPPER)
    draw.text((227, 76), "BILINGUAL EVIDENCE DOSSIER", font=font(16, bold=True), fill=WHITE, anchor="mm")
    draw.text((1132, 67), "Ahmed Alhafiz", font=font(25, bold=True), fill=WHITE, anchor="ra")
    ar(draw, (1132, 106), "أحمد الحافظ", size=16, fill=MUTED)

    chain_panel(draw, arabic=False)

    draw.text((560, 184), "WHEN FEAR", font=font(45, bold=True), fill=WHITE)
    draw.text((560, 242), "DECIDES BEFORE", font=font(45, bold=True), fill=WHITE)
    draw.text((560, 300), "DIAGNOSIS", font=font(45, bold=True), fill=WHITE)
    draw.multiline_text((562, 350), "How uncertainty becomes authority\nand coercion inside families", font=font(25, bold=True), fill=COPPER_LIGHT, spacing=8)
    draw.line((560, 465, 1130, 465), fill=LINE, width=2)
    draw.text((560, 505), "14 claims · 19 sources · open evidence appendix", font=font(17, bold=True), fill=MUTED)
    draw.text((560, 540), "diagnostic safety · consent · voluntary support", font=font(15), fill=SOFT)
    draw.text((560, 592), "Independent specialist review: not yet completed", font=font(13), fill="#d9a9b1")

    path = OUTPUT / "diagnostic-uncertainty-family-fear-en.png"
    image.save(path, format="PNG", optimize=True)
    return path


def validate(path: Path) -> None:
    with Image.open(path) as image:
        if image.format != "PNG" or image.size != (WIDTH, HEIGHT) or image.mode != "RGB":
            raise RuntimeError(f"Invalid social card: {path} ({image.format}, {image.size}, {image.mode})")
    if path.stat().st_size < 10_000:
        raise RuntimeError(f"Suspiciously small social card: {path} ({path.stat().st_size} bytes)")


def main() -> None:
    if not features.check("raqm"):
        raise RuntimeError("Pillow lacks libraqm; correct Arabic shaping cannot be guaranteed")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    cards = [draw_arabic(), draw_english()]
    for path in cards:
        validate(path)
        print(f"generated: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
