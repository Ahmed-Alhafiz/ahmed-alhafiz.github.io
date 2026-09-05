from pathlib import Path
import re

TITLE = {
'de/books/umm-abbas/index.html': ('Umm Abbas — Den Geliebten zurückbringen und die Geschiedene zurückführen | Ahmed Alhafiz','Umm Abbas — Psychologischer Horrorroman | Ahmed Alhafiz'),
'articles/diagnostic-uncertainty-family-fear-coercive-authority/index.html': ('حين يحكم الخوف قبل التشخيص: كيف يتحول الغموض إلى سلطة وإكراه داخل الأسرة؟ | أحمد الحافظ','حين يحكم الخوف قبل التشخيص: الغموض والإكراه | أحمد الحافظ'),
'en/articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/index.html': ('Claim and Evidence Register: When Fear Decides Before Diagnosis | Ahmed Alhafiz','Fear Before Diagnosis: Claim & Evidence Register | Ahmed Alhafiz'),
'articles/teaching-names-ai-understanding/index.html': ('تعليم الأسماء والذكاء الاصطناعي: من الاسم إلى العالم والمسؤولية | أحمد الحافظ','تعليم الأسماء والذكاء الاصطناعي: الفهم والمسؤولية | أحمد الحافظ'),
'en/books/sirou-fi-alard/index.html': ('قل سيروا في الأرض فانظروا كيف بدأ الخلق | Forthcoming book by Ahmed Alhafiz','Sirou fi al-Ard — Forthcoming Book | Ahmed Alhafiz'),
'articles/spiritual-healing-exploitation-safeguarding/index.html': ('حين يتحول العلاج الروحي إلى استغلال: كيف تحمي الأسرة المريض؟ | أحمد الحافظ','استغلال العلاج الروحي وحماية الأسرة | أحمد الحافظ'),
'articles/water-civilization-power/index.html': ('الماء والحضارة والسلطة: من إدارة المورد إلى العدل أو السيطرة | أحمد الحافظ','الماء والحضارة والسلطة: العدل أم السيطرة؟ | أحمد الحافظ'),
'books/sirou-fi-alard/index.html': ('قل سيروا في الأرض فانظروا كيف بدأ الخلق | مؤلَّف قيد الإصدار — أحمد الحافظ','قل سيروا في الأرض فانظروا كيف بدأ الخلق | أحمد الحافظ'),
'en/articles/water-civilization-power/evidence/index.html': ('Claim and Evidence Appendix: Water, Civilization and Power | Ahmed Alhafiz','Water, Civilization & Power: Evidence Appendix | Ahmed Alhafiz'),
'en/articles/teaching-names-ai-understanding/index.html': ('Teaching the Names and AI: What Counts as Understanding? | Ahmed Alhafiz','Teaching the Names and AI: Understanding | Ahmed Alhafiz'),
'articles/six-days-creation-cosmic-time/index.html': ('أيام الخلق الستة والزمن الكوني: هل اليوم القرآني 24 ساعة؟ | أحمد الحافظ','أيام الخلق الستة والزمن الكوني | أحمد الحافظ'),
}

DESC = {
'articles/diagnostic-uncertainty-family-fear-coercive-authority/index.html': ('ملف بحثي موسع يشرح كيف ينتقل الغموض الصحي أو النفسي داخل الأسرة من الخوف إلى اليقين المبكر ثم نقل السلطة والإكراه، ويقترح مسار أمان موازيا يحفظ التقييم والموافقة والدعم الديني الطوعي.','ملف بحثي يشرح كيف يحول الخوف والغموض الصحي داخل الأسرة عدم اليقين إلى تشخيص مبكر وإكراه، ويقترح مسارًا يحفظ التقييم والموافقة والدعم الطوعي.'),
'en/articles/teaching-names-ai-understanding/index.html': ('A source-audited study of Qur’an 2:30–33, classical exegesis, language-model representations, grounding, causal tests, intention, and the limits of claims about machine understanding.','A source-based study of Qur’an 2:30–33, classical exegesis, language models, grounding, causal tests, intention, and limits of machine-understanding claims.'),
'de/about/index.html': ('Offizielles deutschsprachiges Autorenprofil von Ahmed Alhafiz — أحمد الحافظ: Schreibprojekt, Bücher in Vorbereitung und Forschungsarbeit mit Quellen und ausgewiesenem Prüfstatus.','Offizielles Profil von Ahmed Alhafiz — أحمد الحافظ: Schreibprojekt, Bücher in Vorbereitung sowie arabische und englische Forschung mit Quellen und Prüfstatus.'),
'en/books/kitab-al-kutub/index.html': ('The official page for Kitab al-Kutub — The Book of Books, a forthcoming historical philosophical novel by Ahmed Alhafiz about power, memory, writing, and internal transformation.','Official page for Kitab al-Kutub, a forthcoming historical-philosophical novel by Ahmed Alhafiz about power, memory, writing, and inner transformation.'),
'en/index.html': ('The official website of Ahmed Alhafiz — أحمد الحافظ: forthcoming books and open research essays on religion and science, human experience, history, and psychological horror.','Official website of Ahmed Alhafiz — أحمد الحافظ: forthcoming books and research on religion and science, human experience, history, and psychological horror.'),
'books/juhayman/index.html': ('الصفحة الرسمية لرواية جُهَيْمَان — خوارج بين الركن والمقام لأحمد الحافظ، وهي رواية تاريخية دينية قيد الإصدار عن حادثة الحرم 1979 ومسارات الغلو والتأويل واليقين المغلق.','الصفحة الرسمية لرواية جُهَيْمَان — خوارج بين الركن والمقام لأحمد الحافظ، رواية تاريخية دينية قيد الإصدار عن حادثة الحرم 1979 ومسارات الغلو والتأويل.'),
'de/index.html': ('Offizielle deutschsprachige Seite von Ahmed Alhafiz — أحمد الحافظ: Autorenprofil, Bücher in Vorbereitung und vollständige Forschungsdossiers auf Arabisch und Englisch.','Offizielle Seite von Ahmed Alhafiz — أحمد الحافظ: Autorenprofil, Bücher in Vorbereitung sowie vollständige Forschungsdossiers auf Arabisch und Englisch.'),
'en/articles/water-civilization-power/index.html': ('A bilingual evidence-led dossier on water, civilisation, and power: six layers connecting resource, infrastructure, data, allocation, accountability, and maintenance.','A bilingual research dossier on water, civilisation and power, linking resources, infrastructure, data, allocation, accountability, and maintenance.'),
'en/articles/diagnostic-uncertainty-family-fear-coercive-authority/evidence/index.html': ('A transparent register linking 14 claims to 19 sources, confidence labels, and caveats, separating official guidance and contextual evidence from author synthesis.','A register linking 14 claims to 19 sources, confidence labels, and caveats, distinguishing official guidance, contextual evidence, and author synthesis.'),
'en/research-status/index.html': ('The public register for Ahmed Alhafiz research pages: publication type, version, source review date, external review status, corrections, and book relationships.','Public register for Ahmed Alhafiz research: publication type, version, source-review date, external-review status, corrections, and book relationships.'),
}

paths=set(TITLE)|set(DESC)
for name in sorted(paths):
    p=Path(name); text=p.read_text(encoding='utf-8')
    if name in TITLE:
        old,new=TITLE[name]
        needle=f'<title>{old}</title>'
        repl=f'<title>{new}</title>'
        if text.count(needle)!=1: raise SystemExit(f'{name}: title anchor drift')
        if len(new)>70: raise SystemExit(f'{name}: new title still too long: {len(new)}')
        text=text.replace(needle,repl,1)
    if name in DESC:
        old,new=DESC[name]
        needle=f'<meta name="description" content="{old}">'
        if text.count(needle)!=1: raise SystemExit(f'{name}: description anchor drift')
        if len(new)>160: raise SystemExit(f'{name}: new description still too long: {len(new)}')
        text=text.replace(needle,f'<meta name="description" content="{new}">',1)
    p.write_text(text,encoding='utf-8')

# Align repository audit thresholds with the Ahrefs limits reproduced exactly in the latest crawl.
a=Path('tools/site_audit.py'); code=a.read_text(encoding='utf-8')
old1="elif not 20<=len(q.title)<=95:warnings.append(f'{rel}: title length {len(q.title)}')"
new1="elif not 20<=len(q.title)<=70:warnings.append(f'{rel}: title length {len(q.title)}')"
old2="elif not 65<=len(q.description)<=190:warnings.append(f'{rel}: description length {len(q.description)}')"
new2="elif not 65<=len(q.description)<=160:warnings.append(f'{rel}: description length {len(q.description)}')"
if code.count(old1)!=1 or code.count(old2)!=1: raise SystemExit('site_audit length-threshold anchor drift')
a.write_text(code.replace(old1,new1).replace(old2,new2),encoding='utf-8')
print(f'Updated {len(TITLE)} titles and {len(DESC)} descriptions across {len(paths)} pages.')
