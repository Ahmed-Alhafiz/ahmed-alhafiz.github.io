# HANDOFF — الحالة الحية للموقع

آخر تحديث: 2026-09-22 20:23 Europe/Vienna

## الحالة الحالية
- المستودع: `Ahmed-Alhafiz/ahmed-alhafiz.github.io`.
- الفرع الرسمي والمنشور: `main`.
- HEAD المصدر المتحقق بعد دمج PR #54: `3bc0518aa677e3f8c6251ae714fdb098734494fe`.
- GitHub هو مصدر الحقيقة؛ اقرأ HEAD البعيد الحالي قبل أي عمل جديد.
- Ruleset `Protect main` فعّال، بلا bypass، ويتطلب Pull Request وستة status checks.
- فرع العمل الحالي: `seo/custom-domain-canonical-migration`.
- المهمة الحالية: نقل كل canonical/hreflang/schema/sitemap/feed/IndexNow والهوية الآلية إلى `https://ahmedalhafiz.com`.

## ما تم فعليًا
- انتهت جولة UX الرئيسية حتى PR #51 ونُشرت على `main`.
- أُغلق تعارض الحوكمة في PR #52: استُعيد `PROJECT_STATE.json` و`HANDOFF.md`، ورُبطا بـ`PROJECT_OS.json`.
- أُضيف `validate_live_state.py` إلى Governance integrity للتحقق من وجود ملفي الحالة وترابطهما.
- PR #52 اندمج بنجاح وأصبح `main` على `71348b952456bbe11e823fe4585bbbfb42b409f6`.
- أُعدّ checkpoint بعد الدمج لتسجيل الحالة المستقرة دون تغيير صفحات الموقع.

## ما يجري العمل عليه الآن
- اكتملت دفعة الهجرة محليًا، وتشمل 43 صفحة عامة و43 canonical و43 رابط Sitemap، إضافة إلى الخلاصات وبيانات الهوية والاستشهاد وIndexNow وأدوات الفحص.
- لم تتغير النصوص المرئية أو التصميم أو حالة المؤلفات.
- يلزم الآن Commit/Push ثم Pull Request والفحوص الستة والدمج والتحقق الحي.

## التحقق المنجز
- PR #52 اجتاز الستة required checks على HEAD النهائي قبل الدمج.
- Governance integrity بعد الدمج نجح على `main@71348b952456bbe11e823fe4585bbbfb42b409f6`.
- Site integrity وCitation metadata integrity وContent research architecture بعد الدمج نجحت على نفس HEAD.
- GitHub Pages deployment run 299 نجح على نفس HEAD.
- `Protect main` ما زال Active، يستهدف default branch، بلا bypass actors، ويتطلب الفحوص الستة المعتمدة.
- لا توجد Pull Requests مفتوحة بعد دمج PR #52 وقبل checkpoint sync.
- البنية الحية للدومين الجديد وHTTPS وتحويل `www` والرابط القديم تحققت قبل بدء الهجرة.
- نجحت محليًا: Governance، Site Integrity، Public Hygiene، Editorial، Discovery، Dossier، Entity، Visibility، IndexNow dry-run، UX، Arabic UI، Citation Metadata، Content Research Architecture، و`git diff --check`.

## ما لم يُفحص / حدود الدليل
- لم تمر الدفعة بعد بفحوص Pull Request البعيدة ولم تُنشر على `main`.
- لم يُفحص canonical الذي اختاره Google أو ترتيب الاسم بعد الهجرة.
- لا يوجد ادعاء جديد عن ranking أو AI citation أو traffic.

## المخاطر أو الـblockers
- لا توجد blockers معروفة حاليًا.
- لا يوجد Laptop-only blocker معروف.

## الخطوة التالية الدقيقة
1. Commit وPush للفرع ثم فتح Pull Request.
2. انتظار الفحوص الستة ودمج الدفعة دون bypass.
3. التحقق من الصفحة الحية وcanonical/hreflang/sitemap/robots/author.json/IndexNow.
4. إضافة ملكية الدومين الجديد في Search Console، إرسال Sitemap، وطلب فهرسة الصفحات ذات الأولوية.

## ملفات أو بيانات محلية لا تنتقل عبر Git
- نسخة العمل المؤقتة: `C:\Users\xxx\Ahmed-Projects\work\site-seo-migration-2026-09-22`.

## فحص الاستلام على الجهاز الآخر
1. اقرأ HEAD الفعلي من GitHub قبل أي عمل.
2. اقرأ `PROJECT_CONSTITUTION.md`, `PRODUCT_SPEC.md`, `DECISIONS.md`, `QUALITY_GATES.md`, `AGENTS.md`, `PROJECT_STATE.json`, ثم هذا الملف.
3. على اللابتوب اقرأ أيضًا `LAPTOP_CREDIT_POLICY.md`.
4. لا تكرر فحصًا بقيت مدخلاته كما هي؛ نفّذ أقصر preflight مناسب للمهمة الجديدة.
