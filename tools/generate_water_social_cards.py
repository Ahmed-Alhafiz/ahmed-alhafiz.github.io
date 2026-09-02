#!/usr/bin/env python3
"""Generate dedicated 1200×630 social cards for the water dossier.

The output is deterministic at the layout/content level and uses only Pillow,
DejaVu Sans, and libraqm for Arabic shaping. It is retained as source so the
binary assets can be regenerated and audited rather than treated as opaque art.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

WIDTH, HEIGHT = 1200, 630
NAVY = "#0b1724"
PAPER = "#f3f0e8"
INK = "#17202a"
COPPER = "#bd704e"
BLUE = "#2b6076"
WHITE = "#fffdf8"
MUTED = "#bac7d0"
SOFT = "#9eabb5"
LINE = "#356377"
BORDER = "#d8d0c4"

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/social"
REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = BOLD if bold else REGULAR
    if not path.exists():
        raise FileNotFoundError(f"Required reproducible font is missing: {path}")
    return ImageFont.truetype(str(path), size)


def arabic(
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
        font=load_font(size, bold=bold),
        fill=fill,
        anchor=anchor,
        direction="rtl",
        language="ar",
    )


def rings(draw: ImageDraw.ImageDraw, circles: list[tuple[int, int, int]]) -> None:
    for cx, cy, radius in circles:
        draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            outline=LINE,
            width=1,
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


def draw_arabic_card() -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(image)
    rings(draw, [(-20, 650, 225), (-20, 650, 335), (-20, 650, 445), (525, 540, 220), (525, 540, 330)])

    arabic(draw, (1130, 82), "أحمد الحافظ", size=25, fill=WHITE, bold=True)
    draw.text((1130, 116), "Ahmed Alhafiz", font=load_font(15), fill=MUTED, anchor="ra")

    rounded(draw, (69, 54, 301, 94), 20, COPPER)
    arabic(draw, (185, 74), "ملف بحثي موثّق", size=18, fill=WHITE, anchor="mm", bold=True)

    rounded(draw, (65, 138, 512, 556), 27, PAPER, outline=BORDER, width=2)
    arabic(draw, (471, 188), "سلسلة الماء والسلطة والعدل", size=25, fill=INK, bold=True)
    draw.line((106, 228, 471, 228), fill=COPPER, width=3)

    labels = [
        "المورد والتقلب",
        "البنية التحتية",
        "البيانات والقياس",
        "التخصيص والقواعد",
        "السلطة والمساءلة",
        "الصيانة والصمود",
    ]
    y = 259
    for number, label in enumerate(labels, 1):
        color = COPPER if number % 3 == 1 else BLUE
        draw.ellipse((105, y - 20, 146, y + 20), fill=color)
        draw.text((126, y), str(number), font=load_font(18, bold=True), fill=WHITE, anchor="mm")
        arabic(draw, (470, y), label, size=20, fill=INK, bold=True)
        y += 47

    arabic(draw, (1130, 220), "الماء والحضارة", size=50, fill=WHITE, bold=True)
    arabic(draw, (1130, 308), "والسلطة", size=50, fill=WHITE, bold=True)
    arabic(draw, (1130, 385), "متى تصبح إدارة المورد عدلًا؟", size=29, fill="#f0b894", bold=True)
    arabic(draw, (1130, 438), "ومتى تتحول إلى أداة سيطرة؟", size=29, fill="#f0b894", bold=True)
    draw.line((560, 520, 1130, 520), fill=LINE, width=2)
    arabic(draw, (1130, 572), "نسخة عربية وإنجليزية", size=18, fill=MUTED, bold=True)
    arabic(draw, (1130, 606), "أدلة قابلة للفحص وحدود معلنة", size=16, fill=SOFT)

    path = OUTPUT / "water-civilization-power-ar.png"
    image.save(path, format="PNG", optimize=True)
    return path


def draw_english_card() -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(image)
    rings(draw, [(610, 650, 225), (610, 650, 335), (610, 650, 445), (1110, 610, 170), (1110, 610, 280)])

    rounded(draw, (69, 55, 366, 94), 20, COPPER)
    draw.text((217, 75), "EVIDENCE-LED DOSSIER", font=load_font(18, bold=True), fill=WHITE, anchor="mm")
    draw.text((1130, 80), "Ahmed Alhafiz", font=load_font(25, bold=True), fill=WHITE, anchor="ra")
    arabic(draw, (1130, 119), "أحمد الحافظ", size=17, fill=MUTED)

    draw.text((69, 190), "WATER,", font=load_font(60, bold=True), fill=WHITE)
    draw.text((69, 257), "CIVILIZATION", font=load_font(60, bold=True), fill=WHITE)
    draw.text((69, 324), "AND POWER", font=load_font(60, bold=True), fill=WHITE)
    draw.multiline_text(
        (70, 405),
        "When does resource governance\nproduce justice—and when does it\nbecome control?",
        font=load_font(29, bold=True),
        fill="#f0b894",
        spacing=7,
    )
    draw.line((70, 550, 650, 550), fill=LINE, width=2)
    draw.text(
        (70, 592),
        "Arabic & English · inspectable evidence · explicit limits",
        font=load_font(18),
        fill=MUTED,
    )

    rounded(draw, (690, 136, 1135, 551), 26, PAPER, outline=BORDER, width=2)
    draw.text((730, 171), "THE WATER–POWER–JUSTICE CHAIN", font=load_font(20, bold=True), fill=INK)
    draw.line((730, 205, 1095, 205), fill=COPPER, width=3)
    labels = [
        "Resource & variability",
        "Infrastructure",
        "Data & measurement",
        "Allocation & rules",
        "Authority & accountability",
        "Maintenance & resilience",
    ]
    y = 238
    for number, label in enumerate(labels, 1):
        color = COPPER if number % 3 == 1 else BLUE
        draw.ellipse((730, y - 22, 774, y + 22), fill=color)
        draw.text((752, y), str(number), font=load_font(17, bold=True), fill=WHITE, anchor="mm")
        draw.text((792, y), label, font=load_font(17, bold=True), fill=INK, anchor="lm")
        y += 51
    draw.text(
        (730, 530),
        "Analytical framework · 10 claims · 21 sources",
        font=load_font(13),
        fill="#6d7984",
    )

    path = OUTPUT / "water-civilization-power-en.png"
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
        raise RuntimeError("Pillow was built without libraqm; correct Arabic shaping cannot be guaranteed")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    cards = [draw_arabic_card(), draw_english_card()]
    for path in cards:
        validate(path)
        print(f"generated: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
