# -*- coding: utf-8 -*-
"""يولّد مقاطع صوتية عربية لكل جزء من النشاط التفاعلي (index.html) بصوتين.

لماذا؟ صفحة النشاط يجب أن تكون مسموعة بالكامل لمستخدم كفيف. المتصفح يعتمد على
أصوات النظام، وكثير من أجهزة ويندوز لا تحتوي صوتًا عربيًا. لذلك نولّد المقاطع
مرة واحدة ونشغّلها كملفات، ويبقى speechSynthesis احتياطًا فقط.

صوتان: مؤنث (ar-EG-SalmaNeural) ومذكر (ar-EG-ShakirNeural)، والنصوص تختلف
مع الضمير: صيغة المؤنث تُبنى من نفس النص عبر voice.feminize.

النص يُستخرج من index.html نفسه عبر dump-questions.js حتى لا يختلف الصوت عن
المكتوب. التشغيل: python scripts\\build-activity-audio.py [--force] [--voice m|f|all]
"""
import asyncio
import json
import os
import subprocess
import sys

import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import voice  # noqa: E402

PAGE = os.path.join(ROOT, "index.html")
OUTDIR = os.path.join(ROOT, "audio", "act")
CACHE = os.path.join(OUTDIR, ".texts.json")
CONCURRENCY = 4

QNUM = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس",
        "السادس", "السابع", "الثامن", "التاسع", "العاشر"]
ONUM = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس"]
COUNT = {1: "واحد", 2: "اثنان", 3: "ثلاثة", 4: "أربعة", 5: "خمسة",
         6: "ستة", 7: "سبعة", 8: "ثمانية", 9: "تسعة", 10: "عشرة"}
VOLWORD = {0: "صفر", 10: "عشرة", 20: "عشرون", 30: "ثلاثون", 40: "أربعون",
           50: "خمسون", 60: "ستون", 70: "سبعون", 80: "ثمانون", 90: "تسعون", 100: "مئة"}

# مؤثرات صوتية حقيقية (تصفيق / تنبيه) موجودة في audio/act، لا تُولّد بالتلاوة الآلية
SFX_EXTRA = {
    "sfx.clap": "clap.mp3",
    "sfx.buzz": "buzz.mp3",
}


def build_texts(questions):
    t = {}
    n_all = len(questions)
    for i, q in enumerate(questions, start=1):
        k = "q%d" % i
        opts = q["options"]
        t[k + ".num"] = "السؤال %s من %s." % (QNUM[i - 1], COUNT.get(n_all, str(n_all)))
        t[k + ".ctx"] = "الموقف: " + q["context"]
        t[k + ".q"] = "السؤال: " + q["question"]
        t[k + ".qr"] = "السؤال %s: %s" % (QNUM[i - 1], q["question"])
        t[k + ".hint"] = "عدد البدائل %s. استخدم السهم لأعلى أو لأسفل لسماع البدائل، ثم اضغط إنتر للاختيار، وبعده تب إلى زر تحقق من الإجابة ثم إنتر." % COUNT[len(opts)]
        for j, opt in enumerate(opts, start=1):
            t["%s.o%d" % (k, j)] = "البديل %s من %s: %s" % (ONUM[j - 1], COUNT[len(opts)], opt)
        t[k + ".fbok"] = "إجابة صحيحة. " + q["feedback"]
        t[k + ".fbbad"] = "إجابة غير صحيحة. " + q["feedback"]

    t["sum.none"] = "لم تُجب عن أي سؤال بعد."
    for a in range(1, n_all + 1):
        if a == 1:
            t["sum.a1"] = "أجبت عن سؤال واحد من عشرة."
        elif a == 2:
            t["sum.a2"] = "أجبت عن سؤالين من عشرة."
        else:
            t["sum.a%d" % a] = "أجبت عن %s أسئلة من عشرة." % COUNT[a]
    t["sum.c0"] = "ولم تُصب في أي سؤال."
    t["sum.c1"] = "وأصبت في سؤال واحد."
    t["sum.c2"] = "وأصبت في سؤالين."
    for c in range(3, n_all + 1):
        t["sum.c%d" % c] = "وأصبت في %s أسئلة." % COUNT[c]

    t["msg.nofb"] = "لم تتحقق من إجابة هذا السؤال بعد. اختر بديلًا ثم اضغط زر تحقق من الإجابة."
    t["msg.nocurrent"] = "لم تختر بديلًا بعد في هذا السؤال. استخدم السهم لأعلى أو لأسفل لسماع البدائل، ثم إنتر أو مسافة للاختيار."
    t["help.how.btn"] = (
        "طريقة الحل خطوة بخطوة. زر. اضغط إنتر لتسمع خطوات حل الموقف الأربع، أو ألت مع خمسة."
    )
    t["help.how"] = (
        "طريقة حل المواقف في أربع خطوات. "
        "أولًا: اقرأ الموقف. عند وصولك إلى أول بديل في أي موقف يُقرأ لك الموقف كاملًا، ثم السؤال، ثم البديل. "
        "ثانيًا: اختر. تنقّل بين البدائل بالسهم لأعلى ولأسفل، ويُعلَن كل بديل لحظة الوصول إليه، "
        "ثم اضغط إنتر للاختيار، والمسافة تعمل أيضًا. "
        "ثالثًا: تحقق. اضغط تب حتى تصل إلى زر تحقق من الإجابة، ثم إنتر، فتسمع إجابة صحيحة أو إجابة غير صحيحة مع التفسير. "
        "رابعًا: أكمل. بعد التحقق تظهر ثلاثة أزرار: السؤال التالي، وإعادة الإجابة على هذا السؤال، "
        "واسمَع الإجابة الصحيحة والتفسير؛ تنقّل بينها بمفتاح تب، وشغّل الذي تريده بمفتاح إنتر. "
        "وبعد آخر موقف يتحول زر السؤال التالي إلى «عرض النتيجة»؛ اضغطه بالإنتر فتسمع درجتك النهائية، ثم تجد نفسك في قسم نتيجة النشاط. "
        "وفي أي لحظة: إسكيب يوقف الصوت، وألت مع واحد يعيد الموقف، وألت مع اثنين يعيد السؤال، "
        "وألت مع ثلاثة يعيد البديل، وألت مع أربعة يعيد التغذية الراجعة."
    )
    t["msg.nocheck"] = "تنبيه: لم تختر بديلًا. اختر أحد البدائل ثم اضغط تحقق من الإجابة."
    t["msg.selected"] = "محدد."
    t["msg.first"] = "هذا أول سؤال."
    t["msg.last"] = "هذا آخر سؤال."
    t["msg.reset"] = "تمت إعادة المحاولة. جميع الإجابات محيت."
    t["msg.ttson"] = "التلاوة الصوتية مفعّلة. للتنقل بين الأسئلة استخدم السهم لأعلى أو لأسفل، ولكل بديل إعلان عند الوصول إليه."
    t["msg.ttsoff"] = "تم إيقاف التلاوة الصوتية."
    t["msg.after"] = "لسماع التفسير مرة أخرى اضغط إعادة التغذية الراجعة، ولإعادة السؤال اضغط إعادة السؤال."
    t["msg.choices"] = "هناك ثلاثة أزرار: السؤال التالي، وإعادة الإجابة على السؤال، واسمِع الإجابة الصحيحة والتفسير. اضغط Tab للوصول إليها، ثم Enter."
    t["kt.next"] = "السؤال التالي. زر. اضغط Enter للانتقال إلى السؤال التالي."
    t["kt.finish"] = "عرض النتيجة. زر. اضغط إنتر لتسمع درجتك النهائية في النشاط."
    t["kt.retry"] = "إعادة الإجابة على هذا السؤال. زر. اضغط Enter لإعادة المحاولة."
    t["kt.reveal"] = "اسمع الإجابة الصحيحة والتفسير. زر. اضغط Enter لتسمع الإجابة الصحيحة مع التفسير."
    t["fb.ok"] = "أحسنت. إجابة صحيحة."
    t["fb.bad"] = "خطأ. حاول مرة أخرى."
    t["fb.incomplete"] = "لم تكمل الجزء بعد. اختر أحد البدائل ثم اضغط تحقق من الإجابة."
    t["fb.section_done"] = "ممتاز. أكملت هذا الجزء بنجاح."
    t["sfx.wait"] = "اختر إجابتك الآن."

    for v in range(0, 101, 10):
        t["vol.%d" % v] = "مستوى الصوت %s بالمئة." % VOLWORD[v]

    return t


def file_for(vk, key):
    return os.path.join(OUTDIR, vk, key.replace(".", "_") + ".mp3")


async def gen(sem, vk, key, text, force, cache):
    path = file_for(vk, key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not force and not voice.needs_build(cache, vk, key, text, path):
        return key, path, "skip"
    async with sem:
        last = ""
        for attempt in range(4):
            try:
                await asyncio.wait_for(
                    edge_tts.Communicate(text, voice.VOICES[vk], rate=voice.RATE).save(path),
                    timeout=30,
                )
                if os.path.getsize(path) > 1000:
                    voice.mark_built(cache, vk, key, text)
                    return key, path, "ok"
                last = "small file"
            except Exception as e:  # noqa: BLE001
                last = str(e)
            await asyncio.sleep(1.5 * (attempt + 1))
        return key, path, "FAIL " + last
    return key, path, "FAIL unreachable"


def inject_manifest(texts):
    manifest = {}
    for vk in voice.VOICES:
        manifest[vk] = {k: "audio/act/%s/%s.mp3" % (vk, k.replace(".", "_")) for k in sorted(texts)}
        # مؤثرات صوتية حقيقية (مولّدة بـ ffmpeg) لا تُبنى بالتلاوة الآلية — مشتركة
        for key, file_name in SFX_EXTRA.items():
            manifest[vk][key] = "audio/act/" + file_name
    block = ("<!-- ACT_AUDIO_START -->\n<script>\nconst ACT_AUDIO = " +
             json.dumps(manifest, ensure_ascii=False, indent=0).replace("\n", "") +
             ";\n</script>\n<!-- ACT_AUDIO_END -->")

    with open(PAGE, encoding="utf-8") as f:
        html = f.read()

    start = html.find("<!-- ACT_AUDIO_START -->")
    end = html.find("<!-- ACT_AUDIO_END -->")
    if start >= 0 and end > start:
        html = html[:start] + block + html[end + len("<!-- ACT_AUDIO_END -->"):]
    else:
        idx = html.find("<script>")
        if idx < 0:
            raise SystemExit("no <script> tag in index.html")
        html = html[:idx] + block + "\n" + html[idx:]

    with open(PAGE, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    return len(manifest["f"])


async def main():
    force = "--force" in sys.argv
    which = "all"
    if "--voice" in sys.argv:
        which = sys.argv[sys.argv.index("--voice") + 1]
    voices = list(voice.VOICES) if which == "all" else [which]

    os.makedirs(OUTDIR, exist_ok=True)
    subprocess.run(["node", os.path.join(HERE, "dump-questions.js")], check=True, cwd=HERE)
    with open(os.path.join(OUTDIR, "questions.json"), encoding="utf-8") as f:
        questions = json.load(f)

    texts = build_texts(questions)
    cache = voice.load_cache(CACHE)
    sem = asyncio.Semaphore(CONCURRENCY)
    fails = []
    total_ok = total_skip = 0
    for vk in voices:
        print("== صوت %s (%s) ==" % (voice.VOICE_LABEL[vk], voice.VOICES[vk]))
        tasks = [gen(sem, vk, k, voice.variants(v)[vk], force, cache) for k, v in texts.items()]
        results = await asyncio.gather(*tasks)
        fails += [r for r in results if r[2].startswith("FAIL")]
        total_ok += len([r for r in results if r[2] == "ok"])
        total_skip += len([r for r in results if r[2] == "skip"])
        voice.save_cache(CACHE, cache)

    print("generated:", total_ok, "skipped:", total_skip, "failed:", len(fails))
    for f in fails[:10]:
        print("  FAIL", f[0], f[2])
    if fails:
        raise SystemExit(1)

    n = inject_manifest(texts)
    total = 0
    count = 0
    for base, _dirs, files in os.walk(OUTDIR):
        for x in files:
            if x.endswith(".mp3"):
                total += os.path.getsize(os.path.join(base, x))
                count += 1
    print("manifest entries per voice:", n)
    print("mp3 files:", count, "total MB: %.2f" % (total / 1048576.0))


if __name__ == "__main__":
    asyncio.run(main())
