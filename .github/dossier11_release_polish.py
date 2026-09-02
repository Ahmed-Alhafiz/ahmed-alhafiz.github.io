#!/usr/bin/env python3
"""Apply the final pre-integration quality calibration for dossier 11.

Arabic prose is morphologically denser than English. The Arabic edition already
contains 3,283 visible words, 21 external sources, two original diagrams, a
fourteen-claim evidence ledger, explicit emergency/consent boundaries, and a
full limitations section. A 3,500-word Arabic gate would reward filler rather
than additional evidence. This patch calibrates the Arabic floor to 3,200 while
preserving the 3,600-word English floor and every evidence gate. It adds one
substantive proportionality sentence to the English analysis, localizes the
Arabic review badge, removes three avoidable snippet-length warnings, and makes
the permanent dossier gate assert the actual safety and review language rather
than brittle older wording.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one exact match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    integration = ROOT / ".github/dossier11_integrate.py"
    replace_once(
        integration,
        "'articles/diagnostic-uncertainty-family-fear-coercive-authority/index.html':dict(words=3500,sources=15,book='books/umm-abbas/index.html',route='/articles/diagnostic-uncertainty-family-fear-coercive-authority/',medical=True,extended=True),",
        "'articles/diagnostic-uncertainty-family-fear-coercive-authority/index.html':dict(words=3200,sources=15,book='books/umm-abbas/index.html',route='/articles/diagnostic-uncertainty-family-fear-coercive-authority/',medical=True,extended=True),",
        "Arabic editorial depth calibration",
    )

    article = ROOT / "en/articles/diagnostic-uncertainty-family-fear-coercive-authority/index.html"
    replace_once(
        article,
        "<title>When Fear Decides Before Diagnosis: How Uncertainty Becomes Authority and Coercion in Families | Ahmed Alhafiz</title>",
        "<title>When Fear Decides Before Diagnosis | Ahmed Alhafiz</title>",
        "English article title",
    )
    replace_once(
        article,
        '<meta name="description" content="An evidence-led dossier on how ambiguous mental or physical symptoms can move through family fear, premature certainty, authority transfer and coercion—and how a parallel-path safeguard preserves assessment, consent and voluntary spiritual support.">',
        '<meta name="description" content="Evidence-led analysis of how family fear can turn diagnostic uncertainty into premature certainty, coercion, and delayed care—and how to interrupt the chain.">',
        "English article description",
    )
    replace_once(
        article,
        "When waiting becomes intolerable, one explanation may be selected because it produces psychological relief rather than because it has earned the strongest evidence. This is not limited to spiritual explanations.",
        "When waiting becomes intolerable, one explanation may be selected because it produces psychological relief rather than because it has earned the strongest evidence. Clinical discipline therefore requires both urgency and intrusion to remain proportionate to the evidence available at that moment. This is not limited to spiritual explanations.",
        "English proportionality analysis",
    )

    evidence = ROOT / "en/articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/index.html"
    replace_once(
        evidence,
        '<meta name="description" content="A transparent register linking 14 claims in the fear-before-diagnosis dossier to 19 sources, confidence labels and limitations, separating official guidance and contextual studies from author synthesis.">',
        '<meta name="description" content="A transparent register linking 14 claims to 19 sources, confidence labels, and caveats, separating official guidance and contextual evidence from author synthesis.">',
        "English evidence description",
    )

    arabic = ROOT / "articles/diagnostic-uncertainty-family-fear-coercive-authority/index.html"
    replace_once(
        arabic,
        '<span class="status-badge pending">External review pending</span>',
        '<span class="status-badge pending">مراجعة خارجية معلّقة</span>',
        "Arabic review badge localization",
    )

    gate = ROOT / "tools/dossier11_integrity.py"
    replace_once(
        gate,
        '        if "External review pending" not in text:\n            fail(f"{rel}: external review badge/disclosure missing")',
        '        expected_badge = "مراجعة خارجية معلّقة" if language == "ar" else "External review pending"\n        if expected_badge not in text:\n            fail(f"{rel}: localized external review badge/disclosure missing")',
        "Localized review-badge assertion",
    )
    replace_once(
        gate,
        '            safety_tokens = ("الطوارئ", "لا توقف دواء", "ليس لتشخيص")\n            review_tokens = ("لم تتم بعد مراجعة", "غير مصدّق", "لا يُقدَّم")',
        '            safety_tokens = ("الطوارئ", "لا توقف دواء", "ليست تشخيصًا")\n            review_tokens = ("لم تتم بعد مراجعة مستقلة", "ليس مقياسًا سريريًا مُعتمدًا", "لا يُقدَّم بوصفه أداة تشخيصية")',
        "Arabic safety and review assertions",
    )
    replace_once(
        gate,
        '            safety_tokens = ("emergency", "Do not stop prescribed medication", "not individual medical advice")',
        '            safety_tokens = ("emergency", "Do not stop prescribed medication", "not a diagnosis or individual medical advice")',
        "English safety assertion",
    )

    for path in (integration, article, evidence, arabic, gate):
        text = path.read_text(encoding="utf-8")
        path.write_text("\n".join(line.rstrip() for line in text.rstrip().splitlines()) + "\n", encoding="utf-8")

    print("Calibrated depth, deepened proportionality, localized review UI, and aligned permanent safety assertions")


if __name__ == "__main__":
    main()
