#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "articles/diagnostic-uncertainty-family-fear-coercive-authority"
EN_DOSSIER = ROOT / "en/articles/diagnostic-uncertainty-family-fear-coercive-authority"

REPLACEMENTS = {
    "؛ ال تثبت أن المعالج التقليدي سبب التأخر": "؛ لا تثبت أن المعالج التقليدي سبب التأخر",
    "الفاعلية القانونية": "الأهلية القانونية",
    "التطبيق القانوني والتفاصيل الإجرائية تختلف بين الدول": "التطبيق القانوني والتفاصيل الإجرائية يختلفان بين الدول",
    "https://nap.nationalacademies.org/resource/21794/interactive/": "https://nap.nationalacademies.org/catalog/21794/improving-diagnosis-in-health-care",
    "الأخطاء التشخيصية: سلسلة الرعاية الأولية الأكثر أمانًا": "الأخطاء التشخيصية: السلسلة التقنية للرعاية الأولية الأكثر أمانًا",
    "السؤال المباشر عن الخطر لا يصنع الفكرة؛ بل يساعد على كشف الحاجة العاجلة.": "اسأل مباشرةً وبهدوء عند وجود مؤشرات خطر، ثم اطلب مساعدة مؤهلة إذا كان الجواب نعم أو بقي الشك.",
}

TARGETS = [
    DOSSIER / "index.html",
    EN_DOSSIER / "index.html",
    DOSSIER / "evidence/index.html",
    EN_DOSSIER / "evidence/index.html",
    DOSSIER / "evidence/claims.json",
    DOSSIER / "evidence/references.bib",
    DOSSIER / "evidence/references.ris",
]


def main() -> None:
    changed: list[str] = []
    replacement_counts = {old: 0 for old in REPLACEMENTS}

    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        revised = text
        for old, new in REPLACEMENTS.items():
            count = revised.count(old)
            if count:
                replacement_counts[old] += count
                revised = revised.replace(old, new)
        if revised != text:
            path.write_text(revised.rstrip() + "\n", encoding="utf-8")
            changed.append(path.relative_to(ROOT).as_posix())

    required = (
        "؛ ال تثبت أن المعالج التقليدي سبب التأخر",
        "الفاعلية القانونية",
        "https://nap.nationalacademies.org/resource/21794/interactive/",
        "الأخطاء التشخيصية: سلسلة الرعاية الأولية الأكثر أمانًا",
    )
    missing = [token for token in required if replacement_counts[token] == 0]
    if missing:
        raise SystemExit(f"Expected source/language corrections were not found: {missing}")

    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        for obsolete in (
            "؛ ال تثبت أن المعالج التقليدي سبب التأخر",
            "الفاعلية القانونية",
            "https://nap.nationalacademies.org/resource/21794/interactive/",
            "الأخطاء التشخيصية: سلسلة الرعاية الأولية الأكثر أمانًا",
        ):
            if obsolete in text:
                raise SystemExit(f"{path.relative_to(ROOT)}: obsolete wording remained: {obsolete}")

    claims = (DOSSIER / "evidence/claims.json").read_text(encoding="utf-8")
    for required_text in (
        "؛ لا تثبت أن المعالج التقليدي سبب التأخر",
        "الأهلية القانونية",
        "التطبيق القانوني والتفاصيل الإجرائية يختلفان بين الدول",
        "https://nap.nationalacademies.org/catalog/21794/improving-diagnosis-in-health-care",
    ):
        if required_text not in claims:
            raise SystemExit(f"Corrected claims register is missing: {required_text}")

    print("Final source/language polish applied to:")
    for item in changed:
        print(f"- {item}")


if __name__ == "__main__":
    main()
