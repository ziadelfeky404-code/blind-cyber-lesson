# -*- coding: utf-8 -*-
import re
import theme

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.abspath(os.path.join(HERE, "..", "lesson.html"))

LESSON_CSS = """
  body{padding-bottom:40px;}
  .lesson{max-width:960px;margin:0 auto;padding:22px 18px 44px;}
  .lesson h2{color:var(--navy);margin-top:36px;border-bottom:3px dashed var(--line);
    padding-bottom:8px;font-size:1.55rem;}
  .lesson h3{color:var(--blue);margin-top:26px;}
  .lesson h4{color:var(--blue2);margin-top:20px;}
  .lesson ol,.lesson ul{padding-inline-start:28px;}
  .lesson li{margin:.45rem 0;}
  .lesson p{margin:.7rem 0;}
  .lesson table{border-collapse:collapse;width:100%;background:#fff;border-radius:16px;
    overflow:hidden;box-shadow:var(--shadow);border:0;}
  .lesson th,.lesson td{border:0;border-bottom:2px solid #e2ebf5;padding:12px 14px;text-align:right;}
  .lesson th{background:var(--navy);color:#fff;}
  .lesson tr:last-child td{border-bottom:0;}
  .lesson strong{color:var(--navy);}
"""

HERO = """<header>
  <div class="hero-inner">
    {mascot}
    <div>
      <h1>الدرس الرقمي: التهديدات السيبرانية المتقدمة</h1>
      <p><strong>المقرر:</strong> الكمبيوتر وتكنولوجيا المعلومات والاتصالات</p>
      <p><strong>الصف:</strong> الثاني الإعدادي — الفصل الدراسي الأول 2025/2026</p>
      <p><strong>الوحدة:</strong> الوحدة الأولى «الذكاء الاصطناعي وحماية بياناتنا الرقمية» — الدرس الثاني</p>
      <p><strong>الفئة المستهدفة:</strong> متعلمون من ذوي الإعاقة السمعية أو البصرية، مع مراعاة أن احتياجات كل فئة متنوعة وليست متطابقة.</p>
      <div class="chips">
        <span class="chip">نص كامل وقارئ شاشة</span>
        <span class="chip">عناوين متسلسلة</span>
        <span class="chip">لا يعتمد على اللون وحده</span>
      </div>
    </div>
  </div>
</header>

<main class="lesson">
"""


def build():
    with open(P, encoding="utf-8") as f:
        s = f.read()

    # fix Arabic typos found on review
    s = s.replace("تسليمجه", "تسليمه")
    s = s.replace("ضرر مادي وسرعة للمؤسسة", "ضرر مادي وسمعة للمؤسسة")

    # viewport + theme in <head>
    s = s.replace(
        '<meta charset="utf-8">',
        '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">',
        1,
    )
    s = s.replace(
        "</head>",
        theme.FONT_LINKS + "\n<style>" + theme.CSS + LESSON_CSS + "</style>\n</head>",
        1,
    )

    # hero + open main, replacing the plain title block
    hero = HERO.replace("{mascot}", theme.MASCOT)
    s = re.sub(r"<body>.*?(?=<h2>)", "<body>\n" + hero, s, count=1, flags=re.S)

    # close main before </body>
    s = s.replace("</body>", "</main>\n</body>", 1)

    with open(P, "w", encoding="utf-8") as f:
        f.write(s)
    print("saved:", P)


if __name__ == "__main__":
    build()
