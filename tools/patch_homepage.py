#!/usr/bin/env python3
"""One-time exact patch for homepage article discovery and book-page access."""
from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        '      <a href="#home">الرئيسية</a><a href="#works">المؤلفات</a><a href="/about/">عن الكاتب</a><a href="#links">تواصل</a>',
        '      <a href="#home">الرئيسية</a><a href="/articles/">المقالات</a><a href="#works">المؤلفات</a><a href="/about/">عن الكاتب</a><a href="#links">تواصل</a>',
    ),
    (
        '<div class="drawer-panel"><nav aria-label="قائمة الهاتف"><a href="#home">الرئيسية</a><a href="#works">المؤلفات</a><a href="/about/">عن الكاتب</a><a href="#links">تواصل</a></nav></div>',
        '<div class="drawer-panel"><nav aria-label="قائمة الهاتف"><a href="#home">الرئيسية</a><a href="/articles/">المقالات</a><a href="#works">المؤلفات</a><a href="/about/">عن الكاتب</a><a href="#links">تواصل</a></nav></div>',
    ),
    (
        '<span class="book-cover"><img src="juhayman-cover.webp" alt="الغلاف الأمامي لرواية جهيمان — القيامة بين الركن والمقام" loading="lazy"></span>',
        '<span class="book-cover"><img src="juhayman-cover.webp" width="800" height="1200" alt="الغلاف الأمامي لرواية جهيمان — القيامة بين الركن والمقام" loading="lazy"></span>',
    ),
    (
        '<span class="book-cover"><img src="umm-abbas-cover.webp" alt="الغلاف الأمامي لرواية أم عباس لجلب الحبيب ورد المطلقة" loading="lazy"></span>',
        '<span class="book-cover"><img src="umm-abbas-cover.webp" width="800" height="1200" alt="الغلاف الأمامي لرواية أم عباس لجلب الحبيب ورد المطلقة" loading="lazy"></span>',
    ),
    (
        '<span class="book-cover"><img src="sirou-fi-alard-cover.webp" alt="الغلاف الأمامي لكتاب قل سيروا في الأرض فانظروا كيف بدأ الخلق" loading="lazy"></span>',
        '<span class="book-cover"><img src="sirou-fi-alard-cover.webp" width="800" height="1200" alt="الغلاف الأمامي لكتاب قل سيروا في الأرض فانظروا كيف بدأ الخلق" loading="lazy"></span>',
    ),
    (
        '<span class="book-cover"><img src="kitab-al-kutub-cover.webp" alt="الغلاف الأمامي لرواية كتاب الكتب" loading="lazy"></span>',
        '<span class="book-cover"><img src="kitab-al-kutub-cover.webp" width="800" height="1200" alt="الغلاف الأمامي لرواية كتاب الكتب" loading="lazy"></span>',
    ),
    (
        '<div class="sheet-visual"><img id="sheetImage" src="" alt=""></div>',
        '<div class="sheet-visual"><img id="sheetImage" src="" width="800" height="1200" alt="غلاف المؤلَّف المحدد"></div>',
    ),
    (
        '        <div class="sheet-blurb" id="sheetBlurb"></div>',
        '        <div class="sheet-blurb" id="sheetBlurb"></div>\n        <a class="sheet-page-link" id="sheetPageLink" href="/">الانتقال إلى صفحة المؤلَّف الكاملة ←</a>',
    ),
    (
        "const sheetBlurb = document.getElementById('sheetBlurb');",
        "const sheetBlurb = document.getElementById('sheetBlurb');\nconst sheetPageLink = document.getElementById('sheetPageLink');",
    ),
    (
        "  const key=card.dataset.book; activeCard=card; populateBook(key);",
        "  const key=card.dataset.book; activeCard=card; populateBook(key); sheetPageLink.href=card.getAttribute('href');",
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one homepage match, found {count}: {old[:100]}")
    text = text.replace(old, new, 1)

css = """
/* Homepage research discovery */
.articles-intro{max-width:760px;margin:20px 0 0;color:#b7afa4;font-size:18px;line-height:1.95}
.articles-preview{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-top:30px}
.article-preview{display:flex;flex-direction:column;min-height:290px;border:1px solid var(--line-soft);border-radius:17px;padding:23px;background:linear-gradient(180deg,rgba(255,255,255,.018),rgba(255,255,255,.005));transition:transform .24s ease,border-color .24s ease,box-shadow .24s ease}
.article-preview:hover,.article-preview:focus-visible{transform:translateY(-4px);border-color:rgba(208,168,101,.5);box-shadow:0 20px 44px rgba(0,0,0,.25)}
.article-preview-tag{color:var(--gold);font-size:12px;letter-spacing:.04em;margin-bottom:14px}
.article-preview h3{font-size:24px;line-height:1.55;color:#e5c28d;margin:0 0 12px;font-weight:600}
.article-preview p{color:#aaa198;line-height:1.8;margin:0 0 20px}
.article-preview-more{margin-top:auto;color:#d6b27a;font-size:14px}
.sheet-page-link{display:inline-flex;align-items:center;justify-content:center;min-height:46px;margin-top:20px;padding:0 18px;border:1px solid rgba(181,138,80,.52);border-radius:12px;color:#e0bb80;background:rgba(181,138,80,.05);transition:.2s}
.sheet-page-link:hover,.sheet-page-link:focus-visible{border-color:var(--gold-2);background:rgba(181,138,80,.1);transform:translateY(-1px)}
@media(max-width:900px){.articles-preview{grid-template-columns:1fr}.article-preview{min-height:auto}}
"""
css_marker = "\n@media (prefers-reduced-motion:reduce){"
if text.count(css_marker) != 1:
    raise SystemExit("Could not locate the homepage CSS insertion point")
text = text.replace(css_marker, "\n" + css + css_marker, 1)

articles = """
<section class="section homepage-articles" id="articles">
  <div class="wrap">
    <div class="section-kicker">Research &amp; essays</div>
    <h2 class="section-title">المقالات والدراسات</h2><div class="section-rule"></div>
    <p class="articles-intro">دراسات عربية أصلية تقوم على فصل النصوص عن النماذج والتفسيرات، وتوثيق الادعاءات بمصادر أولية أو رسمية، مع بيان حدود اليقين وما يبقى محل بحث.</p>
    <div class="articles-preview">
      <a class="article-preview" href="/articles/ratq-fatq-big-bang/">
        <span class="article-preview-tag">الكون والوحي · دراسة مرجعية</span>
        <h3>الرتق والفتق والانفجار العظيم: ما الذي يقوله القرآن وما الذي يثبته العلم؟</h3>
        <p>مقارنة منضبطة بين الدلالة القرآنية، والتفسير، والنموذج الكوني الحار، وأدلته الرصدية وحدوده.</p>
        <span class="article-preview-more">قراءة الدراسة ←</span>
      </a>
      <a class="article-preview" href="/articles/sleep-paralysis-jathoom/">
        <span class="article-preview-tag">النوم والثقافة · تقرير موثق</span>
        <h3>شلل النوم والجاثوم: لماذا نشعر بوجود كائن في الغرفة؟</h3>
        <p>شرح طبي وثقافي للهلاوس المرتبطة بالنوم، ولماذا تعطي ثقافات مختلفة للتجربة أسماء وصورًا متباينة.</p>
        <span class="article-preview-more">قراءة التقرير ←</span>
      </a>
      <a class="article-preview" href="/guides/arabic-psychological-horror/">
        <span class="article-preview-tag">الأدب والرعب · دليل تحليلي</span>
        <h3>الرعب النفسي العربي: كيف يعمل الخوف حين لا نعرف مصدره؟</h3>
        <p>إطار عملي لتمييز مركز الخوف، ودرجة اليقين، وعلاقة البيت والجسد والتفسير بتجربة الرعب.</p>
        <span class="article-preview-more">قراءة الدليل ←</span>
      </a>
    </div>
    <a class="about-link" href="/articles/">جميع المقالات والدراسات ←</a>
  </div>
</section>
"""
section_marker = '\n<section class="section works" id="works">'
if text.count(section_marker) != 1:
    raise SystemExit("Could not locate the homepage article-section insertion point")
text = text.replace(section_marker, "\n" + articles + section_marker, 1)

path.write_text(text, encoding="utf-8")
print("Homepage patch applied and exact-match assertions passed.")
