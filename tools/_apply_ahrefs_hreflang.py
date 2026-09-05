# Temporary idempotent repair script; removed before merge.
from pathlib import Path

REPLACEMENTS = {
    "en/about/index.html": (
        '<link rel="alternate" hreflang="x-default" href="https://ahmed-alhafiz.github.io/en/about/">',
        '<link rel="alternate" hreflang="x-default" href="https://ahmed-alhafiz.github.io/about/">',
    ),
    "en/articles/index.html": (
        '<link rel="alternate" hreflang="x-default" href="https://ahmed-alhafiz.github.io/en/articles/">',
        '<link rel="alternate" hreflang="x-default" href="https://ahmed-alhafiz.github.io/articles/">',
    ),
}

for name, (old, new) in REPLACEMENTS.items():
    path = Path(name)
    text = path.read_text(encoding="utf-8")
    old_count = text.count(old)
    new_count = text.count(new)
    if old_count == 1 and new_count == 0:
        path.write_text(text.replace(old, new), encoding="utf-8")
    elif old_count == 0 and new_count == 1:
        pass
    else:
        raise SystemExit(
            f"{name}: unexpected x-default state old={old_count} new={new_count}"
        )

AUDIT = Path("tools/site_audit.py")
code = AUDIT.read_text(encoding="utf-8")
marker = "checked_hreflang_groups=set()"
if marker not in code:
    anchor = """    for p,q in pages.items():
        for h in q.hrefs:
            t=target(root,p,h)
            if t is not None and not t.exists():
                (warnings if args.partial else errors).append(f'{p.relative_to(root)}: broken local link {h} -> {t.relative_to(root) if t.is_relative_to(root) else t}')

    # Sitemap coverage, local validity, and lastmod truthfulness.
"""
    gate = """    for p,q in pages.items():
        for h in q.hrefs:
            t=target(root,p,h)
            if t is not None and not t.exists():
                (warnings if args.partial else errors).append(f'{p.relative_to(root)}: broken local link {h} -> {t.relative_to(root) if t.is_relative_to(root) else t}')

    # Every multilingual hreflang group must expose one identical mapping,
    # including the same x-default destination, on every member page.
    canonical_pages={q.canonical:(p,q) for p,q in pages.items() if q.canonical}
    checked_hreflang_groups=set()
    for p,q in pages.items():
        if not q.canonical or not q.alternates:continue
        language_alts={code:url for code,url in q.alternates.items() if code!='x-default'}
        if len(language_alts)<2:continue
        rel=p.relative_to(root)
        if q.lang and q.alternates.get(q.lang)!=q.canonical:
            errors.append(f'{rel}: self hreflang {q.lang!r} does not match canonical')
        member_urls=frozenset(language_alts.values())
        group_key=tuple(sorted(member_urls))
        if group_key in checked_hreflang_groups:continue
        checked_hreflang_groups.add(group_key)
        member_mappings=[]
        for member_url in sorted(member_urls):
            member=canonical_pages.get(member_url)
            if member is None:
                errors.append(f'{rel}: hreflang group target is not a public canonical page: {member_url}')
                continue
            member_path,member_page=member
            member_language_alts={code:url for code,url in member_page.alternates.items() if code!='x-default'}
            if frozenset(member_language_alts.values())!=member_urls:
                errors.append(f'{member_path.relative_to(root)}: hreflang group member set differs from {rel}')
            member_mappings.append((member_path,tuple(sorted(member_page.alternates.items()))))
        if member_mappings:
            reference_path,reference_mapping=member_mappings[0]
            for member_path,mapping in member_mappings[1:]:
                if mapping!=reference_mapping:
                    errors.append(
                        f'{member_path.relative_to(root)}: hreflang mapping differs from '
                        f'{reference_path.relative_to(root)}; all group members must share the same tags and x-default'
                    )

    # Sitemap coverage, local validity, and lastmod truthfulness.
"""
    if code.count(anchor) != 1:
        raise SystemExit("tools/site_audit.py: hreflang gate insertion anchor drift")
    AUDIT.write_text(code.replace(anchor, gate), encoding="utf-8")

print("Ahrefs hreflang repair script completed.")
