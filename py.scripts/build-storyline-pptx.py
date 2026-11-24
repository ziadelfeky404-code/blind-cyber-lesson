# -*- coding: utf-8 -*-
import json
import os
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from lxml import etree

EMU_PER_PX = 914400 // 96
NAVY = (0x0B, 0x3D, 0x6B)
DARK = (0x1A, 0x1A, 0x1A)
GREEN = (0x0B, 0x5D, 0x2E)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))


def px(v):
    return Emu(int(v * EMU_PER_PX))


def add_text(slide, left, top, width, height, text, size, bold, rgb, align="r"):
    tb = slide.shapes.add_textbox(px(left), px(top), px(width), px(height))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.name = "Arial"
        run.font.color.rgb = RGBColor(*rgb)
        pPr = p._p.get_or_add_pPr()
        pPr.set("rtl", "1")
        pPr.set("algn", align)
        rPr = run._r.get_or_add_rPr()
        for tag in ("a:ea", "a:cs"):
            el = etree.SubElement(rPr, qn(tag))
            el.set("typeface", "Arial")
    tb._element.nvSpPr.cNvPr.set("descr", text[:900])
    return tb


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def slide_title_body(prs, title, body, notes, body_size=18):
    s = blank(prs)
    add_text(s, 40, 24, 880, 68, title, 27, True, NAVY)
    add_text(s, 40, 100, 880, 420, body, body_size, False, DARK)
    s.notes_slide.notes_text_frame.text = notes
    return s


def main():
    data = json.load(open(ROOT + r"\course.json", encoding="utf-8"))
    meta = data["meta"]
    prs = Presentation()
    prs.slide_width = Emu(9144000)
    prs.slide_height = Emu(5143500)

    for sl in data["slides"]:
        t = sl["type"]
        if t == "title":
            s = blank(prs)
            add_text(s, 40, 120, 880, 90, sl["title"], 36, True, NAVY, align="c")
            add_text(s, 40, 220, 880, 60, sl.get("subtitle", ""), 18, False, DARK, align="c")
            add_text(s, 40, 290, 880, 60, sl.get("meta", "") + "\n" + meta["target"], 15, False, GREEN, align="c")
            s.notes_slide.notes_text_frame.text = sl["notes"]
        elif t == "objectives":
            body = sl.get("intro", "") + "\n\n" + "\n".join("• " + b for b in sl["bullets"])
            slide_title_body(prs, sl["title"], body, sl["notes"])
        elif t == "content":
            body = "\n".join("• " + b for b in sl["bullets"])
            slide_title_body(prs, sl["title"], body, sl["notes"])
        elif t == "scenario":
            em = sl["email"]
            body = ("من: " + em["from"] + "\n"
                    "الموضوع: " + em["subject"] + "\n"
                    "نص الرسالة: " + em["body"] + "\n\n"
                    "السؤال: " + sl["question"] + "\n"
                    "الإجابة الصحيحة: " + sl["answer"])
            slide_title_body(prs, sl["title"], body, sl["notes"])
        elif t == "summary":
            body = "\n".join("• " + b for b in sl["bullets"])
            slide_title_body(prs, sl["title"], body, sl["notes"])

    for i, q in enumerate(data["quiz"], 1):
        opts = "\n".join(f"{j+1}) {o}" for j, o in enumerate(q["options"]))
        body = q["question"] + "\n\n" + opts
        notes = (f"هدف السؤال: {q['objective']}.\n"
                 f"الإجابة الصحيحة: {q['options'][q['correct']]}.\n"
                 f"تغذية راجعة (صحيحة): {q['fbCorrect']}\n"
                 f"تغذية راجعة (خاطئة): {q['fbWrong']}")
        slide_title_body(prs, f"تقويم ذاتي {i}: {q['objective']}", body, notes)

    path = ROOT + r"\Storyline_Course.pptx"
    prs.save(path)
    print("saved:", path)
    print("slides:", len(prs.slides._sldIdLst), "quiz:", len(data["quiz"]))


if __name__ == "__main__":
    main()
