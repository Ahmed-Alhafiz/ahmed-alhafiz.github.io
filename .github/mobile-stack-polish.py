#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_MARKER = "/* UX10 mobile stacking correction */"
CSS = r'''

/* UX10 mobile stacking correction */
@media(max-width:960px){
  .home-hero-grid,.profile-grid{
    grid-template-columns:minmax(0,1fr);
    min-height:0;
    padding:54px 0 62px;
    gap:30px;
    align-items:start;
  }
  .home-hero-grid>div:first-child,.profile-grid>div:first-child{
    grid-column:1;
    min-width:0;
  }
  .hero-portrait,.profile-portrait{
    grid-column:1;
    grid-row:auto;
    order:-1;
    justify-self:center;
    margin-inline:auto;
    max-width:100%;
  }
}
@media(max-width:620px){
  .home-hero-grid,.profile-grid{padding:25px 0 42px;gap:23px}
  .hero-portrait,.profile-portrait{width:min(47vw,174px)}
}
'''

REPLACEMENTS = {
    "index.html": {
        "Featured research dossier": "الملف البحثي المحوري",
        "New extended dossiers": "ملفات بحثية موسعة",
        "Why a source becomes usable": "متى يصبح المصدر صالحًا للاستخدام؟",
        "Forthcoming works": "مؤلفات قيد الإصدار",
        "COSMOS": "الكون",
        "MIND": "المعرفة",
        "NARRATIVE": "السرد",
    },
    "about/index.html": {
        "Research architecture": "بنية البحث",
        "Flagship dossier": "الملف البحثي المحوري",
        "Forthcoming works": "مؤلفات قيد الإصدار",
        "English edition": "النسخة الإنجليزية",
    },
}

GLOBAL_REPLACEMENTS = {
    "للتواصل المباشر أو متابعة النشر، استخدم القنوات الرسمية التالية فقط. لا تُعرض هنا حسابات تقنية أو روابط مكررة للغات.":
        "للتواصل المباشر ومتابعة جديد المقالات والمؤلفات، هذه هي القنوات الرسمية المعتمدة.",
    "Use these verified channels for direct contact and publication updates. Technical profiles and duplicate language links are intentionally excluded.":
        "For direct enquiries and publication updates, use these verified official channels.",
    "Für direkte Anfragen und Veröffentlichungsneuigkeiten gelten ausschließlich diese offiziellen Kanäle. Technische Profile und doppelte Sprachlinks werden nicht angezeigt.":
        "Für direkte Anfragen und Veröffentlichungsneuigkeiten gelten diese verifizierten offiziellen Kanäle.",
    'aria-label="Medium، Instagram، Email"': 'aria-label="Medium, Instagram, Email"',
    'aria-label="Medium، Instagram، E-Mail"': 'aria-label="Medium, Instagram, E-Mail"',
}


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path.relative_to(ROOT)}: expected one {old!r}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    css_path = ROOT / "assets/site-v2.css"
    css = css_path.read_text(encoding="utf-8")
    if CSS_MARKER in css:
        raise RuntimeError("mobile stacking correction already exists")
    css_path.write_text(css.rstrip() + CSS + "\n", encoding="utf-8")

    for rel, changes in REPLACEMENTS.items():
        path = ROOT / rel
        for old, new in changes.items():
            replace_once(path, old, new)

    changed_global = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        revised = text
        for old, new in GLOBAL_REPLACEMENTS.items():
            revised = revised.replace(old, new)
        if revised != text:
            path.write_text(revised, encoding="utf-8")
            changed_global += 1

    for path in list(ROOT.rglob("*.html")) + [css_path]:
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        normalized = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
        path.write_text(normalized, encoding="utf-8")

    css = css_path.read_text(encoding="utf-8")
    for token in (
        CSS_MARKER,
        ".home-hero-grid,.profile-grid{\n    grid-template-columns:minmax(0,1fr);",
        "grid-column:1;\n    grid-row:auto;\n    order:-1;",
        "width:min(47vw,174px)",
    ):
        if token not in css:
            raise RuntimeError(f"CSS correction missing token: {token}")

    for rel in ("index.html", "about/index.html"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        if any(english in text for english in ("Featured research dossier", "New extended dossiers", "Research architecture", "Flagship dossier", "Forthcoming works", "English edition")):
            raise RuntimeError(f"{rel}: avoidable English interface wording remained")

    print(f"Applied mobile single-column stacking and polished {changed_global} contact surfaces")


if __name__ == "__main__":
    main()
