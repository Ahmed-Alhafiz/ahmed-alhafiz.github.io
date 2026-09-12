# حماية الفرع `main`

ملفات المشروع لا تستطيع وحدها منع push مباشر أو force-push؛ يجب تفعيل Ruleset/Branch Protection من إعدادات GitHub.

## الإعداد المطلوب
أنشئ Ruleset يستهدف `main` واجعله Active، ثم فعّل:
- Require a pull request before merging.
- Block force pushes.
- Restrict deletions.
- Require status checks to pass before merging.
- Require branches to be up to date before merging إذا لم يسبب ذلك تعطيلًا غير مبرر.
- لا bypass دائمًا إلا لسبب موثق.

## الفحوص المطلوبة
بعد تثبيت Project OS v2 اختر من الواجهة الفحوص المستقرة التالية عند ظهورها:
- `Governance integrity / validate`
- `PR policy / policy`
- `Site integrity / audit`
- `Visual review / render`
- `Content research architecture / validate`
- `Citation metadata integrity` أو اسم job المطابق الظاهر في PR.

إذا تغير اسم job حدّث Ruleset وهذه الوثيقة معًا.

## الموافقات
حاليًا يكفي PR + checks لأن المالك واحد. إذا توفر مراجع مستقل موثوق لاحقًا، اجعل موافقة واحدة على الأقل مطلوبة للتغييرات المؤثرة.

## اختبار الحماية
بعد التفعيل افتح PR تجريبيًا صغيرًا وتأكد أن الدمج محجوب عند فشل check مطلوب وأن push المباشر/force-push إلى `main` ممنوعان وفق الإعداد.
