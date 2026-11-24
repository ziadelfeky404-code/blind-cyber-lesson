# -*- coding: utf-8 -*-
"""Generate learner-facing Arabic narration for each slide and quiz item — two voices.

Important: the `notes` field in course.json is teacher-facing guidance and is
NOT read aloud to the learner. The narration reads only what the learner sees.

الصوتان: مؤنث (f) ومذكر (m)، وفي كل صوتٍ ملفات في audio/{f,m}/.
التشغيل: python scripts\\build-audio.py [--force] [--voice m|f|all]
"""
import argparse
import asyncio
import json
import os
import re
import subprocess
import sys

import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
STORY_DIR = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import voice  # noqa: E402

AUDIO = os.path.join(STORY_DIR, "audio")
CACHE = os.path.join(AUDIO, ".texts.json")
COURSE = os.path.join(STORY_DIR, "course.json")
CONCURRENCY = 4

with open(COURSE, encoding="utf-8") as f:
    data = json.load(f)


def clean(t):
    t = t.replace("•", " ")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def slide_text(s):
    parts = []
    if s["type"] == "title":
        parts.append("مرحبًا بك في درس التهديدات السيبرانية المتقدمة.")
    if s.get("bridge"):
        parts.append(s["bridge"])
    parts.append(s["title"] + ".")
    if s.get("subtitle"):
        parts.append(s["subtitle"] + ".")
    if s.get("intro"):
        parts.append(s["intro"])
    for b in s.get("bullets", []):
        parts.append(b)
    if s.get("email"):
        e = s["email"]
        parts.append("لنقرأ مثالًا على رسالة مشبوهة. المرسل: " + e["from"] + ".")
        parts.append("الموضوع: " + e["subject"] + ".")
        parts.append("نص الرسالة: " + e["body"])
    if s.get("question"):
        parts.append("السؤال: " + s["question"])
    if s.get("answer"):
        parts.append("التصرف الآمن: " + s["answer"])
    return clean(". ".join(p for p in parts if p))


items = []
feed = []
for s in data["slides"]:
    items.append((s["id"], slide_text(s)))

letters = ["أ", "ب", "ج", "د"]
for q in data["quiz"]:
    parts = ["سؤال تقويمي. " + q["question"]]
    parts.append("الخيارات: " + "، ".join(
        letters[j] + ": " + o for j, o in enumerate(q["options"])) + ".")
    parts.append("اختر إجابة واحدة، ثم اضغط تحقق من الإجابة.")
    items.append((q["id"], clean(" ".join(parts))))
    # التغذية الراجعة تُسمع فقط عند طلبها بزر «اسمع الإجابة الصحيحة»
    fb = ("الإجابة الصحيحة هي الخيار " + letters[q["correct"]] + ": " +
          q["options"][q["correct"]] + ". " + q["fbCorrect"])
    feed.append((q["id"] + "_fb", clean(fb)))


def file_for(vk, sid):
    return os.path.join(AUDIO, vk, sid + ".mp3")


async def gen(sem, vk, sid, text, force, cache):
    path = file_for(vk, sid)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not force and not voice.needs_build(cache, vk, sid, text, path):
        return sid, path, "skip"
    async with sem:
        last = ""
        for attempt in range(4):
            try:
                await asyncio.wait_for(
                    edge_tts.Communicate(text, voice.VOICES[vk], rate=voice.RATE).save(path),
                    timeout=30,
                )
                if os.path.getsize(path) > 1000:
                    voice.mark_built(cache, vk, sid, text)
                    return sid, path, "ok"
                last = "small file"
            except Exception as e:  # noqa: BLE001
                last = str(e)
            await asyncio.sleep(1.5 * (attempt + 1))
        return sid, path, "FAIL " + last
    return sid, path, "FAIL unreachable"


def make_full(vk):
    concat = os.path.join(AUDIO, vk, "_concat.txt")
    with open(concat, "w", encoding="utf-8") as f:
        for sid, _ in items:
            f.write("file '" + sid + ".mp3'\n")
    out = os.path.join(AUDIO, vk, "narration_full.mp3")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "_concat.txt", "-c", "copy",
                    "narration_full.mp3"], check=False, cwd=os.path.join(AUDIO, vk))
    print("combined:", out)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--voice", choices=["m", "f", "all"], default="all")
    args = ap.parse_args()
    voices = list(voice.VOICES) if args.voice == "all" else [args.voice]

    cache = voice.load_cache(CACHE)
    sem = asyncio.Semaphore(CONCURRENCY)
    fails = []
    ok = skip = 0
    for vk in voices:
        print("== صوت %s (%s) ==" % (voice.VOICE_LABEL[vk], voice.VOICES[vk]))
        tasks = []
        for sid, text in items + feed:
            tasks.append(gen(sem, vk, sid, voice.variants(text)[vk], args.force, cache))
        results = await asyncio.gather(*tasks)
        fails += [r for r in results if r[2].startswith("FAIL")]
        ok += len([r for r in results if r[2] == "ok"])
        skip += len([r for r in results if r[2] == "skip"])
        voice.save_cache(CACHE, cache)
        make_full(vk)

    print("generated:", ok, "skipped:", skip, "failed:", len(fails))
    for f in fails[:10]:
        print("  FAIL", f[0], f[2])
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
