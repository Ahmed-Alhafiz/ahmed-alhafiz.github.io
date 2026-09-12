# نقطة تسليم آمنة للموقع

آخر تحديث: 12 سبتمبر 2026 — Europe/Vienna

## تحديث تدقيق 12 سبتمبر 2026

- مصدر الحقيقة الرسمي: GitHub.
- فرع التسليم الفعلي: `handoff/safe-transfer-2026-09-11`.
- آخر رأس بعيد تم التحقق منه قبل إنشاء checkpoint التوثيق الحالي: `1ea7582b70dd424f6036bee20e99288f3b15f576`.
- رأس `main` المنشور عند آخر تحقق: `c1a886f089be2e33c43bd69e56223ea795bd4bee`.
- نجحت بعد آخر دمج: `Governance integrity` و`Site integrity` و`Citation metadata integrity` و`Content research architecture`، كما نجح `Visual review` على نفس شجرة تغيير الحوكمة قبل الدمج.
- تم فحص القواعد الأساسية على فرع التسليم مقابل `main`: `AGENTS.md` و`PROJECT_OS.json` وباقي طبقة Project OS v2.1 متزامنة، وتمت مزامنة PR policy الأحدث ضمن checkpoint الحالي.
- `main` ما زال غير محمي فعليًا من GitHub (`protected: false`)؛ تفعيل Branch Protection/Ruleset هو أهم حاجز تقني متبقٍ.
- هذا checkpoint لا يغير محتوى الموقع المنشور أو صفحات المستخدم؛ يحدّث الحوكمة وحالة التسليم فقط.
- لأن تحديث هذه الوثيقة نفسه ينشئ commit جديدًا، اقرأ HEAD الفعلي من GitHub قبل بدء أي تعديل ولا تعامل SHA السابق كـHEAD نهائي.

## نظام الحوكمة

قبل أي تطوير أو نشر اقرأ بالترتيب:

1. `PROJECT_CONSTITUTION.md`
2. `PRODUCT_SPEC.md`
3. `DECISIONS.md`
4. `QUALITY_GATES.md`
5. `AGENTS.md`
6. `LAPTOP_CREDIT_POLICY.md` عند العمل من اللابتوب/Codex/Work أو أي رصيد محدود
7. `HANDOFF.md`

المراجع الجديدة تتقدم على المحادثات والتعليمات القديمة عند التعارض. دورة العمل الإلزامية: فهم → فحص → خطة قصيرة → تنفيذ → اختبارات → Red Team → إصلاح → إعادة اختبار → توثيق → Commit/Push/Handoff.

## حالة المشروع

- المستودع: `Ahmed-Alhafiz/ahmed-alhafiz.github.io`.
- فرع التسليم: `handoff/safe-transfer-2026-09-11`.
- الفرع المنشور: `main`.
- لا يوجد تطوير موقع جارٍ في checkpoint الحالي.
- المحتوى المنشور الحالي على `main` اجتاز بوابات السلامة المذكورة أعلاه بعد آخر تغيير حوكمة.
- المخطوطتان «سيروا في الأرض» و«أم عباس» لم تصلا بعد؛ ممنوع اختراع أحداث أو اقتباسات أو تفاصيل منهما.

## ما تم إنجازه

- تحسين الرئيسية العربية لإبراز «سيروا في الأرض» و«أم عباس» ومسار القراءة بين الموقع وMedium.
- تحسين صفحتي الكتابين والتنقل الداخلي والعرض على الهاتف والكمبيوتر.
- ربط مقالتي Medium بصفحة «سيروا» والأبحاث ومصادرها.
- بناء طبقة فحوص للموقع تشمل سلامة الصفحات، metadata، البحث والمصادر، والـvisual review.
- نظام حوكمة v2.1 يفرض سلامة المحتوى، دقة المصادر، UX، SEO غير مضلل، Red Team، انتقال الأجهزة، وسياسة توفير رصيد اللابتوب دون خفض الجودة.

## آخر الفحوصات المثبتة

- Governance integrity على `main`: ناجح.
- Site integrity على `main`: ناجح.
- Citation metadata integrity على `main`: ناجح.
- Content research architecture على `main`: ناجح.
- Visual review على شجرة تغيير الحوكمة نفسها قبل الدمج: ناجح، بما في ذلك الحالات متعددة اللغات والاستجابة للمقاسات.
- الفحوص المحلية السابقة شملت نظافة العرض العام، جودة الأدلة، هوية الكاتب، الواجهة العربية، الرؤية التقنية، وIndexNow بوضع dry-run دون إرسال.

نجاح الفحوص لا يسمح بادعاء ترتيب بحث أو ظهور في ChatGPT/Google دون بيانات فعلية. وأي محتوى جديد يجب أن يعاد فحصه وفق `QUALITY_GATES.md`.

## الخطوة التالية

1. فعّل Branch Protection/Ruleset لـ`main` وفق `BRANCH_PROTECTION.md`.
2. عند استلام المشروع على أي جهاز: اقرأ ملفات الحوكمة أولًا ثم تحقق من HEAD المحلي مقابل GitHub.
3. على اللابتوب: ابدأ بالفحوص والقراءة المستهدفة وادمج العمليات المتصلة لتقليل الرصيد، لكن لا تتخطَّ source/UX/integrity/visual checks اللازمة لتوفير الكلفة.
4. إذا كانت المهمة القادمة تعتمد على مخطوطتي «سيروا في الأرض» أو «أم عباس»، يجب استلامهما وقراءتهما قبل كتابة المحتوى أو نسبة حقائق إليهما.

## نقاط غير مكتملة ومحاذير

- Branch Protection/Ruleset على `main` غير مفعل بعد.
- أي نتائج SEO/ranking/AI citation مستقبلية غير مثبتة ما لم تُقاس ببيانات حديثة.
- لا تحذف مجلدي العمل المحليين `site-book-journey-2026-09-11` و`site-reference-upgrade-2026-09-10` قبل التأكد من فتح فرع التسليم والتحقق منه على الجهاز الآخر.
- سجلات الفحص المحلي في `C:\Users\xxx\Ahmed-Projects\setup-results\site-handoff-2026-09-11` ليست مصدر المشروع.
- لا تستخدم `git reset --hard` أو `git clean` أو force push أو حذف الفروع لتسوية حالة النقل.

## Phone-first SEO / Indexing checkpoint — 12 سبتمبر 2026

- تم تنفيذ الفحص من الهاتف، مع الالتزام بقاعدة Phone-first وعدم نقل أي عمل قادر عليه الهاتف إلى اللابتوب.
- HEAD البعيد الذي بُني عليه هذا checkpoint قبل تحديث `HANDOFF.md`: `95a659de3aa7f36dfb84697c3e0ac8279df4c339` على `handoff/safe-transfer-2026-09-11`.
- `main` المنشور بقي عند `c1a886f089be2e33c43bd69e56223ea795bd4bee`؛ لم يحدث نشر أو تعديل لمحتوى الموقع في هذه المرحلة.
- Google Search Console خلال آخر 28 يومًا حتى 9 سبتمبر 2026: 26 نقرة، 126 ظهورًا، CTR نحو 20.63%، ومتوسط موضع نحو 6.74.
- `sitemap.xml` يحتوي 43 URL. Indexing Tracker يسجل: 43 متتبعة، 2 مفهرسة، 41 غير مفهرسة، دون أخطاء أو warnings نشطة. التفصيل الحالي: 40 `URL is unknown to Google`، صفحتان `Submitted and indexed`، وصفحة واحدة `Crawled - currently not indexed`.
- الصفحتان المفهرستان المثبتتان: `/` و`/about/`.
- أُعيد فحص أهم 10 صفحات عبر Google URL Inspection؛ بقيت الصفحات ذات الأولوية غير مفهرسة في آخر تحقق.
- فحص On-page مباشر لعينة الصفحات المهمة أثبت أنها ترجع 200 وقابلة للفهرسة، مع canonical ذاتي وبدون `noindex`، ولا توجد عيوب SEO حرجة/عالية/متوسطة في العينة. الربط الداخلي من الرئيسية ومركز الأبحاث موجود ومباشر.
- GA4 مثبت مركزيًا منذ 6 سبتمبر 2026، ولذلك أرقام GA4 قبل هذا التاريخ غير متاحة. التتبع يعمل حاليًا؛ لا يوجد دليل مثبت على عطل GA4.
- Bing Webmaster Tools غير مهيأ في الاتصال الحالي، وIndexNow غير مهيأ حاليًا؛ لا توجد submissions مسجلة.

### Laptop-only / manual-browser step

**المطلوب فقط على اللابتوب:** استخدام واجهة Google Search Console عبر متصفح مسجل الدخول لتنفيذ `URL Inspection` ثم `Request indexing` للصفحات التالية، واحدة تلو الأخرى:

1. `https://ahmed-alhafiz.github.io/articles/`
2. `https://ahmed-alhafiz.github.io/articles/ratq-fatq-big-bang/`
3. `https://ahmed-alhafiz.github.io/articles/teaching-names-ai-understanding/`
4. `https://ahmed-alhafiz.github.io/articles/water-civilization-power/`
5. `https://ahmed-alhafiz.github.io/books/sirou-fi-alard/`
6. `https://ahmed-alhafiz.github.io/books/umm-abbas/`
7. `https://ahmed-alhafiz.github.io/books/juhayman/`

**سبب التحويل:** الأدوات المتاحة على الهاتف تستطيع قراءة Search Console، URL Inspection، التتبع والتحليل، لكنها لا تعرض إجراء Google UI الخاص بـ`Request indexing`. التحويل هنا بسبب قدرة غير متاحة، وليس لأن اللابتوب أفضل عمومًا.

**تعليمات اللابتوب:**
- لا تعِد تحليل SEO أو URL Inspection أو On-page audits المذكورة أعلاه ما لم تتغير مدخلاتها؛ استخدم الدليل الحالي.
- لا تعدل كود الموقع ولا `main` لهذه الخطوة.
- بعد تنفيذ طلبات الفهرسة، وثّق فقط أي نجاح/رفض/حد يومي ظهر في Search Console، ثم أعد بقية العمل إلى الهاتف.
- أول خطوة قبل التنفيذ: تحقق من HEAD البعيد الحالي واقرأ `LAPTOP_CREDIT_POLICY.md` و`DEVICE_HANDOFF_PROTOCOL.md` وموضع هذا القسم في `HANDOFF.md`.

### Phone-only continuation بعد إنشاء حزمة اللابتوب

- تم فحص **جميع URLs الـ43 الحية** في `sitemap.xml` عبر On-page audit مباشر، على دفعتين 25 + 18.
- النتيجة: **43/43 قابلة للفهرسة**، و**0 Critical / 0 High / 0 Medium**. ظهرت فقط ملاحظات Low على بعض الصفحات، أهمها طول/قصر بعض عناوين `<title>` وقلة النص في بعض صفحات الكتب قيد الإصدار.
- لم تُعدَّل صفحات الكتب لمجرد رفع عدد الكلمات، لأن المخطوطات غير المستلمة لا يجوز ملء صفحاتها بتفاصيل مخترعة.
- لا يوجد في الفحص الكامل مانع تقني يفسر كون 40 URL غير معروفة لـGoogle؛ المشكلة الحالية اكتشاف/زحف وفهرسة أكثر من كونها `noindex` أو canonical/HTTP failure.
- بيانات الأجهزة من Google Search Console للفترة نفسها: **25 من 26 نقرة جاءت من MOBILE** (75 ظهورًا، CTR 33.33%، متوسط موضع 4.19 تقريبًا)، مقابل نقرة واحدة من DESKTOP (51 ظهورًا). هذا يدعم استمرار معيار Phone-first في UX.
- فحص Core Web Vitals الميداني عبر CrUX لم يكن متاحًا لأن مفتاح CrUX API غير مهيأ في GSC Wizard؛ هذه النقطة **غير مفحوصة** وليست فشل أداء مثبتًا.
- لم يتغير محتوى الموقع ولم يحدث نشر خلال هذه الفحوص؛ لذلك لا حاجة لإعادة CI/visual review بسبب هذه المرحلة التحليلية وحدها.
