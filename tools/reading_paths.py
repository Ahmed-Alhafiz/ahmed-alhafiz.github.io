"""Reading relationships already declared on the four Arabic book pages.

The manuscript is not evidence: this module only follows existing editorial
links. Translations inherit a relationship only when their edition exists.
"""
import re
from pathlib import Path
from urllib.parse import urlparse

BOOK_LABELS = {
    "sirou-fi-alard": {"ar": "قل سيروا في الأرض فانظروا كيف بدأ الخلق", "en": "Sirou fi al-Ard"},
    "umm-abbas": {"ar": "أم عباس لجلب الحبيب ورد المطلقة", "en": "Umm Abbas"},
    "kitab-al-kutub": {"ar": "كتاب الكتب", "en": "Kitab al-Kutub"},
    "juhayman": {"ar": "جُهَيْمَان — خوارج بين الركن والمقام", "en": "Juhayman"},
}


def book_assignments(root: Path) -> dict[str, str]:
    assignments = {}
    for book in BOOK_LABELS:
        source = (root / "books" / book / "index.html").read_text()
        main = re.search(r"<main\b[^>]*>(.*?)</main>", source, re.S)
        if main is None:
            raise ValueError(f"Missing main content: {book}")
        for href in re.findall(r'href=["\']([^"\']+)', main[1]):
            path = urlparse(href).path.strip("/").split("/")
            if len(path) != 2 or path[0] not in {"articles", "guides"}:
                continue
            slug = path[1]
            if slug in assignments and assignments[slug] != book:
                raise ValueError(f"Ambiguous book relationship: {slug}")
            assignments[slug] = book
    return assignments
