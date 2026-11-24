import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "دليل_استخدام_نسخة_Storyline.docx"))

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Arial"
style.font.size = Pt(12)
style.element.rPr.rFonts.set(qn("w:cs"), "Arial")


def rtl(p):
    pPr = p._p.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    pPr.append(bidi)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in p.runs:
        rPr = r._r.get_or_add_rPr()
        rtl_el = OxmlElement("w:rtl")
        rPr.append(rtl_el)


def h(text, level=1):
    p = doc.add_heading(text, level=level)
    rtl(p)
    return p


def para(text, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    rtl(p)
    return p


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text)
    rtl(p)
    return p


h("دليل استخدام نسخة Articulate Storyline", 0)
para("درس: التهديدات السيبرانية المتقدمة — الصف الثاني الإعدادي")
para("الوحدة الأولى: الذكاء الاصطناعي وحماية بياناتنا الرقمية")

h("١) الملفات المرفقة", 1)
bullet("التهديدات_السيبرانية_المتقدمة.story — مشروع Storyline 3 جاهز للفتح والتعديل والنشر (٢٢ شريحة: ١٤ شريحة محتوى + ٨ أسئلة تقويم).")
bullet("Storyline_Course.pptx — عرض PowerPoint مرتّب للاستيراد داخل Storyline إن رغبت ببناء مشروع جديد (Format > ... أو File > Import > Import PowerPoint).")
bullet("course.html — نسخة ويب تفاعلية متاحة الوصول تعمل مباشرة في المتصفح (بدون Storyline)، وفيها مشغّل شرح صوتي لكل شريحة وزر تشغيل تلقائي.")
bullet("مجلد audio — شرح صوتي عربي لكل شريحة وسؤال (s01.mp3 ... q8.mp3) بصوت واضح مناسب للأطفال، مع narration_full.mp3 للشرح كاملًا في ملف واحد.")
bullet("دليل_المرافق.html — دليل مصمّم بشكل مبهّج وودّي للمرافق (الأخ/المعلّم/الصديق) الذي يجلس بجانب المتعلّم الكفيف، وفيه الخطوات ومفتاح الإجابات.")

h("ملاحظة عن النصوص والصوت", 1)
bullet("عُدّل اتجاه النصوص في مشروع Storyline إلى الكتابة من اليمين إلى اليسار (RTL) ومحاذاة اليمين لظهور العربية صحيحة.")
bullet("الشرح الصوتي مُولّد بصوت عربي فصيح واضح (ar-EG) مناسب للتعلّم السمعي، ويمكن استبداله بتسجيل بشري أو صوت الفيديو الأصلي عند الحاجة.")

h("٢) فتح المشروع", 1)
bullet("شغّل برنامج Articulate Storyline 3.")
bullet("اختر File ثم Open، ثم حدّد ملف التهديدات_السيبرانية_المتقدمة.story.")
bullet("أو انقر نقرًا مزدوجًا على الملف مباشرةً. سيُفتح خلال ثوانٍ (المشروع بحجم ~٢٦ ميجابايت).")

h("٣) ملاحظات حول الاتجاه والخط (RTL)", 1)
bullet("النصوص العربية مُدخلة داخل المشروع. لضبط اتجاه النص من اليمين لليسار: حدّد مربع النص ثم من مجموعة Paragraph اضبط الاتجاه إلى Right-to-Left.")
bullet("تأكد من اختيار خط يدعم العربية (مثل Arial أو Traditional Arabic) من نافذة Font.")

h("٣) النشر للتشغيل على المتصفح", 1)
bullet("اختر File ثم Publish، ثم Web.")
bullet("حدّد مجلد الإخراج، ثم اضغط Publish وافتح ملف story.html الناتج في المتصفح.")
bullet("يمكن تشغيل الخرج على أي جهاز دون تثبيت Storyline.")

h("٣) إمكانية الوصول", 1)
bullet("جميع نصوص الدرس نصية وقابلة للقراءة بواسطة قارئات الشاشة.")
bullet("لإضافة نص بديل للصور: اختر الصورة ثم من قسم Alt Text أدخل وصفًا.")
bullet("يُنصح بترقيم العناوين (Alt Text) وترتيب التنقل باستخدام لوحة المفاتيح عند النشر.")

h("٣) ملاحظات مهمة", 1)
bullet("المحتوى مطابق لكتاب الصف الثاني الإعدادي. لا توجد ادعاءات خارج المصدر.")
bullet("أمثلة الروابط المستخدمة تعليمية وتنتهي بالنطاق .example (غير فعّالة) لتفادي أي مخاطر.")
bullet("موضوعا برامج الفدية وهجمات DDoS وردا في المصدر داخل صور/مخططات، وقد صيغا هنا بصورة مبسطة ويُنصح بمراجعة بشرية للتأكد من مطابقتهما للمصدر.")

doc.save(OUT)
print("wrote:", OUT, os.path.getsize(OUT), "bytes")
