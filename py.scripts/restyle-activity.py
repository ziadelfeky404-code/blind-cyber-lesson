# -*- coding: utf-8 -*-
import re
import theme

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.abspath(os.path.join(HERE, "..", "index.html"))

ACTIVITY_CSS = """
  /* activity specifics built on the shared theme */
  body{padding-bottom:3rem;}
  header,main,footer{max-width:62rem;margin:0 auto;}
  header{
    background:linear-gradient(135deg,#0b3d6b,#11538f);color:#fff;
    border-radius:0 0 26px 26px;padding:24px 20px;margin-bottom:18px;
  }
  header .hero-inner{display:flex;gap:16px;align-items:center;flex-wrap:wrap;max-width:62rem;margin:0 auto;}
  header h1{color:#fff;margin:0 0 6px;font-size:1.6rem;}
  header p{color:#eaf4fe;margin:4px 0;}
  header details{background:#fff;color:var(--ink);margin-top:16px;}
  header details ul{padding-inline-start:22px;}
  main{padding:0 16px;}
  h2{color:var(--navy);}
  a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{
    outline:4px solid var(--focus);outline-offset:2px;border-radius:10px;}
  button{
    font:inherit;font-size:1rem;font-weight:800;cursor:pointer;
    background:var(--blue);color:#fff;border:3px solid var(--blue);
    border-radius:999px;padding:12px 26px;min-height:50px;
    box-shadow:0 4px 0 rgba(11,61,107,.35);margin-top:8px;
  }
  button:hover{background:var(--blue2);}
  button.secondary{background:#fff;color:var(--blue);}
  .context{background:#fff8e7;border:3px solid #ffd98a;border-radius:16px;padding:12px 16px;margin:.5rem 0 .9rem;}
  .scenario{background:#fff;border:3px solid var(--line);border-radius:var(--r);padding:1rem 1.2rem;margin:1.2rem 0;box-shadow:var(--shadow);}
  fieldset{border:0;padding:0;margin:0 0 .7rem;}
  legend{font-weight:800;color:var(--navy);padding:0 0 .5rem;font-size:1.15rem;}
  .option{display:flex;gap:12px;align-items:flex-start;margin:.5rem 0;padding:12px 16px;
    border:3px solid var(--line);border-radius:16px;cursor:pointer;}
  .option:hover{background:var(--sky);}
  .option:has(input:checked){border-color:var(--blue);background:#e7f1fd;}
  .option input{width:22px;height:22px;margin-top:4px;accent-color:var(--blue);flex:0 0 auto;}
  .feedback{margin:.8rem 0 0;padding:14px 16px;border-radius:16px;display:none;font-weight:700;}
  .feedback.show{display:block;}
  .feedback.ok{color:var(--green);background:var(--green-bg);border:3px solid #9ad4b0;}
  .feedback.bad{color:var(--red);background:var(--red-bg);border:3px solid #f0b0ab;}
  .feedback .verdict{display:block;font-weight:800;margin-bottom:4px;}
  .summary{background:#fff;border:3px solid var(--blue);border-radius:var(--r);padding:1.1rem 1.3rem;margin-top:2rem;box-shadow:var(--shadow);}
  .summary p{margin:.3rem 0;}
  details{background:var(--sky);border:3px solid var(--line);border-radius:18px;padding:.6rem .9rem;margin:1rem 0;}
  summary{cursor:pointer;font-weight:800;color:var(--blue);}
  footer{color:#4b5b6b;font-size:.95rem;text-align:center;padding:0 16px;}
"""

NEW_HEADER = """<header>
  <div class="hero-inner">
    {mascot}
    <div>
      <h1>النشاط التفاعلي: التهديدات السيبرانية المتقدمة</h1>
      <p>الوحدة الأولى: الذكاء الاصطناعي وحماية بياناتنا الرقمية — الدرس الثاني — الصف الثاني الإعدادي.</p>
      <p>عشرة مواقف افتراضية آمنة تقيس فهمك للتهديدات والتصرف الآمن. اختر بديلًا لكل موقف ثم اضغط زر «تحقق من الإجابة».</p>
      <div class="chips">
        <span class="chip">نص كامل</span>
        <span class="chip">قارئ شاشة</span>
        <span class="chip">لوحة المفاتيح</span>
        <span class="chip">أمثلة افتراضية آمنة</span>
      </div>
    </div>
  </div>
  <details>
    <summary>كيف أستخدم النشاط بلوحة المفاتيح أو قارئ الشاشة؟</summary>
    <ul>
      <li>تنقّل بحرف الجدولة (Tab) بين المواقف والمجموعات والأزرار.</li>
      <li>اختر بديلًا بالأسهم أو بمسافة على زر الاختيار.</li>
      <li>اضغط مفتاح الإدخال (Enter) على زر «تحقق من الإجابة».</li>
      <li>يُعلن قارئ الشاشة التغذية الراجعة ونتيجة النشاط تلقائيًا.</li>
      <li>لإعادة المحاولة اضغط زر «إعادة المحاولة» بعد آخر موقف.</li>
    </ul>
  </details>
</header>""".replace("{mascot}", theme.MASCOT)

with open(P, encoding="utf-8") as f:
    s = f.read()

new_style = "<style>\n" + theme.CSS + "\n" + ACTIVITY_CSS + "\n</style>"
s = re.sub(r"<style>.*?</style>", lambda m: new_style, s, count=1, flags=re.S)
s = re.sub(r"<header>.*?</header>", lambda m: NEW_HEADER, s, count=1, flags=re.S)

if theme.FONT_LINKS not in s:
    s = s.replace("<style>", theme.FONT_LINKS + "\n<style>", 1)

with open(P, "w", encoding="utf-8") as f:
    f.write(s)
print("restyled:", P, len(s))
