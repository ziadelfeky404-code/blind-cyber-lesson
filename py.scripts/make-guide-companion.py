# -*- coding: utf-8 -*-
import os
import json
import html
import theme

HERE = os.path.dirname(os.path.abspath(__file__))
COURSE = os.path.abspath(os.path.join(HERE, "..", "course.json"))
OUT = os.path.abspath(os.path.join(HERE, "..", "دليل_المرافق.html"))


def esc(t):
    return html.escape(str(t), quote=True)


with open(COURSE, encoding="utf-8") as f:
    data = json.load(f)

letters = ["أ", "ب", "ج", "د"]
answer_rows = "\n        ".join(
    '<tr><td>{}</td><td>{}</td><td class="ans">{}) {}</td></tr>'.format(
        esc(q["id"][1:]), esc(q["objective"]), letters[q["correct"]],
        esc(q["options"][q["correct"]]),
    )
    for q in data["quiz"]
)

steps = [
    ("شغّلا الصوت معًا", "اضغطا زر التشغيل في كل شريحة لتستمعا إلى الشرح الصوتي، أو فعّلا خيار «تشغيل الشرح الصوتي تلقائيًا» ليبدأ تلقائيًا عند كل شريحة."),
    ("اقرأ العنوان والجمل", "اقرأ عنوان الشريحة ونقاطها بصوت هادئ ومتأنٍّ، وامنحه وقتًا كافيًا لكل جملة."),
    ("تنقّلا معًا", "استخدما زرّي «التالي» و«السابق»، أو الأسهم في لوحة المفاتيح للتنقل بين الشرائح."),
    ("اقرأ السؤال والخيارات", "اقرأ السؤال ثم كل خيار بوضوح، واترك وقتًا للتفكير قبل أن يختار."),
    ("اقرأ التغذية الراجعة", "اقرأ النتيجة والسبب: لماذا الإجابة صحيحة أو غير صحيحة. هذا أهم من الدرجة."),
    ("شجّع دائمًا", "قل: «أحسنت»، «محاولة جيدة»، «لنفكّر معًا». الخطأ فرصة للتعلّم لا للّوم."),
]

step_cards = "\n        ".join(
    '<article class="step"><span class="num">{}</span><h3>{}</h3><p>{}</p></article>'.format(
        i, esc(t), esc(d)
    )
    for i, (t, d) in enumerate(steps, 1)
)

GUIDE_CSS = """
  .guide{max-width:1000px;margin:0 auto;padding:20px 18px 44px;}
  header{background:linear-gradient(135deg,#0b3d6b,#11538f);color:#fff;border-radius:0 0 26px 26px;padding:24px 20px;}
  .guide h2{color:var(--navy);margin:32px 0 14px;font-size:1.5rem;}
  td.ans{color:var(--green);font-weight:800;}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>دليل المرافق — التهديدات السيبرانية المتقدمة</title>
@@FONTS@@
<style>@@CSS@@@@EXTRA@@
@@GUIDE@@
</style>
</head>
<body>
<header>
  <div class="hero-inner">
    @@MASCOT@@
    <div>
      <h1>دليل المرافق</h1>
      <p>كيف تساعد صديقك في درس «التهديدات السيبرانية المتقدمة».</p>
      <p>الوحدة الأولى: الذكاء الاصطناعي وحماية بياناتنا الرقمية — الصف الثاني الإعدادي.</p>
      <div class="chips">
        <span class="chip">للأخ أو المعلّم أو الصديق</span>
        <span class="chip">خطوات بسيطة</span>
        <span class="chip">مفتاح الإجابات</span>
      </div>
    </div>
  </div>
</header>

<main class="guide">
  <p class="lead">هذا الدليل موجّه إليك أنت: الأخ أو الأخت، أو المعلّم، أو الصديق الذي يجلس بجانب المتعلّم الكفيف. أنت «العيون» التي تشرح ما على الشاشة، والصوت الذي يقرأ ويشجّع. معًا ستصنعان تجربة تعلّم ممتعة.</p>

  <h2>ست خطوات بسيطة</h2>
  <div class="grid">
        @@STEPS@@
  </div>

  <h2>اختصارات لوحة المفاتيح</h2>
  <div class="keys">
    <ul>
      <li><span class="kbd">Tab</span> الانتقال بين العناصر والأزرار.</li>
      <li><span class="kbd">&#8594;</span> / <span class="kbd">&#8592;</span> السهمان للتنقل بين الشرائح.</li>
      <li><span class="kbd">Home</span> أول شريحة، و<span class="kbd">End</span> آخر شريحة.</li>
      <li><span class="kbd">Enter</span> أو <span class="kbd">Space</span> لتشغيل الزر المحدّد.</li>
    </ul>
  </div>

  <h2>مفتاح الإجابات (لك أنت فقط)</h2>
  <table class="tbl">
    <thead><tr><th>السؤال</th><th>المهارة</th><th>الإجابة الصحيحة</th></tr></thead>
    <tbody>
        @@ANSWERS@@
    </tbody>
  </table>

  <h2>تنبيهات أمان مهمة</h2>
  <div class="note">
    <p>جميع الأمثلة في الدرس افتراضية وآمنة، والنطاقات المستخدمة غير فعّالة. ذكّر المتعلّم دائمًا بالخطوات الآمنة: التحقق من المصدر، وعدم مشاركة كلمة المرور أو رمز التحقق، وإبلاغ شخص موثوق عند الشك.</p>
  </div>

  <footer class="foot">صُمِّم هذا الدليل ليكون واضحًا ومطمئنًا للمرافق. شخص واحد بجانبه — وقد تكون أنت — يكفي ليصنع فرقًا كبيرًا.</footer>
</main>
</body>
</html>
"""

doc = (
    TEMPLATE
    .replace("@@FONTS@@", theme.FONT_LINKS)
    .replace("@@CSS@@", theme.CSS)
    .replace("@@EXTRA@@", theme.EXTRA)
    .replace("@@GUIDE@@", GUIDE_CSS)
    .replace("@@MASCOT@@", theme.MASCOT)
    .replace("@@STEPS@@", step_cards)
    .replace("@@ANSWERS@@", answer_rows)
)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)
print("saved:", OUT)
