#!/usr/bin/env python3
"""One-time semantic corrections for the global editorial rebuild.

The patch preserves the visible research text while:
- replacing an incorrect evidentiary relationship to forthcoming books with
  a thematic `mentions` relationship;
- making the absence of external specialist review explicit;
- adding a clear emergency boundary to the sleep-paralysis explainer.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    "articles/teaching-names-ai-understanding/index.html",
    "articles/spiritual-healing-exploitation-safeguarding/index.html",
    "articles/six-days-creation-cosmic-time/index.html",
    "articles/sleep-paralysis-jathoom/index.html",
    "articles/functional-seizures-vs-epilepsy/index.html",
]
SCRIPT_RE = re.compile(
    r"(<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>)(.*?)(</script>)",
    re.IGNORECASE | re.DOTALL,
)
CITATION_RE = re.compile(
    r"<[^>]+class=[\"'][^\"']*\bcitation-box\b[^\"']*[\"'][^>]*>",
    re.IGNORECASE,
)

REVIEW_BLOCK = """
<section class="notice-box review-status" id="external-review-status" aria-labelledby="external-review-title">
  <h2 id="external-review-title">حالة المراجعة الخارجية</h2>
  <p><strong>لم تتم بعد مراجعة خارجية مستقلة أو مراجعة اختصاصية لهذه النسخة.</strong> نُشرت المادة مع مصادرها وحدودها المنهجية لإتاحة الفحص والتصحيح، ولا يجوز تقديمها بوصفها بحثًا أكاديميًا محكّمًا. تُسجَّل أي مراجعة لاحقة أو تصحيح جوهري في تاريخ التحديث.</p>
</section>
""".strip()

EMERGENCY_BLOCK = """
<section class="notice-box warning medical-boundary" id="emergency-boundary" aria-labelledby="emergency-boundary-title">
  <h2 id="emergency-boundary-title">متى تصبح الطوارئ ضرورية؟</h2>
  <p>شلل النوم المعتاد قصير وعابر، لكن اطلب الإسعاف أو الطوارئ المحلية فورًا إذا ترافق الحدث مع ألم صدري جديد أو شديد، صعوبة تنفس مستمرة بعد الاستيقاظ، إصابة، ضعف أو خدر مفاجئ، فقدان وعي مطوّل، تشنج مستمر، أو خطر مباشر على الشخص. لا توقف دواءً موصوفًا ولا تغيّر خطة علاج من دون الطبيب المعالج.</p>
</section>
""".strip()


def promote_to_mentions(node: object) -> object:
    if isinstance(node, dict):
        if "isBasedOn" in node:
            relationship = node.pop("isBasedOn")
            existing = node.get("mentions")
            if existing is None:
                node["mentions"] = relationship
            elif isinstance(existing, list):
                if relationship not in existing:
                    existing.append(relationship)
            elif existing != relationship:
                node["mentions"] = [existing, relationship]
        for value in list(node.values()):
            promote_to_mentions(value)
    elif isinstance(node, list):
        for value in node:
            promote_to_mentions(value)
    return node


def rewrite_jsonld(html: str) -> str:
    def replace(match: re.Match[str]) -> str:
        data = json.loads(match.group(2))
        promote_to_mentions(data)
        rendered = json.dumps(data, ensure_ascii=False, indent=2)
        return f"{match.group(1)}\n{rendered}\n{match.group(3)}"

    return SCRIPT_RE.sub(replace, html)


def insert_before_citation(html: str, block: str) -> str:
    match = CITATION_RE.search(html)
    if not match:
        raise RuntimeError("citation-box insertion point not found")
    return html[: match.start()] + block + "\n\n" + html[match.start() :]


def main() -> None:
    changed = []
    for rel in TARGETS:
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(rel)
        html = path.read_text(encoding="utf-8")
        revised = rewrite_jsonld(html)

        lower = revised.lower()
        if not any(token in lower for token in ("مراجعة خارجية", "مراجعة اختصاص", "لم تتم بعد")):
            revised = insert_before_citation(revised, REVIEW_BLOCK)

        if rel.endswith("sleep-paralysis-jathoom/index.html"):
            lower = revised.lower()
            if not any(token in lower for token in ("الطوارئ", "الإسعاف", "emergency")):
                revised = insert_before_citation(revised, EMERGENCY_BLOCK)

        if '"isBasedOn"' in revised:
            raise RuntimeError(f"{rel}: isBasedOn remained after semantic correction")
        if "مراجعة خارجية" not in revised and "لم تتم بعد" not in revised:
            raise RuntimeError(f"{rel}: external-review disclosure missing")
        if rel.endswith("sleep-paralysis-jathoom/index.html") and not any(
            token in revised for token in ("الطوارئ", "الإسعاف", "emergency")
        ):
            raise RuntimeError(f"{rel}: emergency boundary missing")

        if revised != html:
            path.write_text(revised, encoding="utf-8")
            changed.append(rel)

    print(f"Applied semantic and safety corrections to {len(changed)} pages")
    for rel in changed:
        print(f"- {rel}")


if __name__ == "__main__":
    main()
