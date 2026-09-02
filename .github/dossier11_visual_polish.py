#!/usr/bin/env python3
"""Final visual polish after manual inspection of the dossier 11 artifact.

The first visual artifact passed all automated checks. Manual review found one
small presentational defect: the seventh Arabic cascade label sat too close to
the green interruption bar on the 1200×630 share card. This patch increases
panel breathing room and adds stable figure IDs plus targeted visual captures
for all four Arabic/English framework figures.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "diagnostic-uncertainty-family-fear-coercive-authority"
AR_ROUTE = f"/articles/{SLUG}/"
EN_ROUTE = f"/en/articles/{SLUG}/"


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one exact match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_generator() -> None:
    path = ROOT / "tools/generate_diagnostic_uncertainty_social_cards.py"
    changes = (
        ("rounded(draw, (65, 145, 515, 555), 27, PAPER, outline=BORDER, width=2)", "rounded(draw, (65, 145, 515, 570), 27, PAPER, outline=BORDER, width=2)", "share-card panel height"),
        ("    y = 246", "    y = 243", "share-card cascade start"),
        ("        y += 43", "        y += 42", "share-card cascade spacing"),
        ("    rounded(draw, (100, 522, 480, 551), 14, GREEN)", "    rounded(draw, (100, 531, 480, 561), 15, GREEN)", "share-card interruption bar"),
        ('        ar(draw, (290, 537), "يمكن قطع السلسلة في كل مرحلة", size=14, fill=WHITE, anchor="mm", bold=True)', '        ar(draw, (290, 546), "يمكن قطع السلسلة في كل مرحلة", size=14, fill=WHITE, anchor="mm", bold=True)', "Arabic interruption label"),
        ('        draw.text((290, 537), "Interrupt the cascade at every stage", font=font(13, bold=True), fill=WHITE, anchor="mm")', '        draw.text((290, 546), "Interrupt the cascade at every stage", font=font(13, bold=True), fill=WHITE, anchor="mm")', "English interruption label"),
    )
    for old, new, label in changes:
        replace_once(path, old, new, label)


def patch_article_figures() -> None:
    pages = (
        ROOT / f"articles/{SLUG}/index.html",
        ROOT / f"en/articles/{SLUG}/index.html",
    )
    for path in pages:
        replace_once(
            path,
            '<figure class="figure-card"><img src="/assets/figures/fear-certainty-authority-cascade-',
            '<figure class="figure-card" id="cascade-figure"><img src="/assets/figures/fear-certainty-authority-cascade-',
            f"{path.relative_to(ROOT)} cascade figure ID",
        )
        replace_once(
            path,
            '<figure class="figure-card"><img src="/assets/figures/parallel-path-safeguard-',
            '<figure class="figure-card" id="parallel-figure"><img src="/assets/figures/parallel-path-safeguard-',
            f"{path.relative_to(ROOT)} parallel figure ID",
        )


def patch_visual_runner() -> None:
    path = ROOT / ".github/visual-review/run_visual_review.py"
    marker = '    ("about-de-contact", "/de/about/", "#contact", "start"),\n'
    addition = (
        f'    ("fear-cascade-ar", "{AR_ROUTE}", "#cascade-figure", "start"),\n'
        f'    ("fear-parallel-ar", "{AR_ROUTE}", "#parallel-figure", "start"),\n'
        f'    ("fear-cascade-en", "{EN_ROUTE}", "#cascade-figure", "start"),\n'
        f'    ("fear-parallel-en", "{EN_ROUTE}", "#parallel-figure", "start"),\n'
    )
    text = path.read_text(encoding="utf-8")
    if "fear-cascade-ar" in text:
        raise RuntimeError("targeted framework captures already exist")
    if text.count(marker) != 1:
        raise RuntimeError(f"visual TARGET_PAGES marker: expected one, found {text.count(marker)}")
    path.write_text(text.replace(marker, marker + addition, 1), encoding="utf-8")


def patch_integrity_gate() -> None:
    path = ROOT / "tools/dossier11_integrity.py"
    old = '        if "claims.json" not in html or "/evidence/" not in html:\n            fail(f"{rel}: evidence surfaces missing")'
    new = (
        '        if "claims.json" not in html or "/evidence/" not in html:\n'
        '            fail(f"{rel}: evidence surfaces missing")\n'
        '        for figure_id in (\'id="cascade-figure"\', \'id="parallel-figure"\'):\n'
        '            if figure_id not in html:\n'
        '                fail(f"{rel}: stable framework figure target missing: {figure_id}")'
    )
    replace_once(path, old, new, "dossier figure-target invariant")


def normalize() -> None:
    for path in (
        ROOT / "tools/generate_diagnostic_uncertainty_social_cards.py",
        ROOT / f"articles/{SLUG}/index.html",
        ROOT / f"en/articles/{SLUG}/index.html",
        ROOT / ".github/visual-review/run_visual_review.py",
        ROOT / "tools/dossier11_integrity.py",
    ):
        text = path.read_text(encoding="utf-8")
        path.write_text("\n".join(line.rstrip() for line in text.rstrip().splitlines()) + "\n", encoding="utf-8")


def main() -> None:
    patch_generator()
    patch_article_figures()
    patch_visual_runner()
    patch_integrity_gate()
    normalize()
    print("Applied share-card spacing correction and targeted framework visual captures")


if __name__ == "__main__":
    main()
