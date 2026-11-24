# -*- coding: utf-8 -*-
import json
import html
import os
import theme

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = ROOT + r"\course.html"


def esc(t):
    return html.escape(str(t), quote=True)


def ul(items):
    return "\n".join(f"            <li>{esc(x)}</li>" for x in items)


TYPE_LABEL = {
    "objectives": "الأهداف",
    "content": "شرح",
    "scenario": "موقف تطبيقي",
    "summary": "تلخيص",
}


def content_sections(seq):
    out = []
    for i, s in enumerate(seq, 1):
        t = s["type"]
        p = [f'      <section class="slide" id="slide-{i}" tabindex="-1" aria-labelledby="h-{i}" hidden>']
        p.append(f'        <span class="eyebrow">{esc(TYPE_LABEL.get(t, "محتوى"))}</span>')
        p.append(f'        <h2 id="h-{i}">{esc(s["title"])}</h2>')
        if s.get("bridge"):
            p.append(f'        <p class="bridge">{esc(s["bridge"])}</p>')
        p.append('        <div class="audio-wrap">')
        p.append('          <span class="lbl"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" style="vertical-align:-3px"><path d="M3 9v6h4l5 4V5L7 9H3z"/><path d="M16 8a5 5 0 0 1 0 8v-2a3 3 0 0 0 0-4V8z"/></svg> اسمع الشرح</span>')
        p.append(f'          <audio class="narration" controls preload="none" data-a="{esc(s["id"])}.mp3" src="audio/f/{esc(s["id"])}.mp3" aria-label="الشرح الصوتي لهذه الشريحة"></audio>')
        p.append("        </div>")
        if t == "objectives":
            p.append(f'        <p>{esc(s.get("intro", ""))}</p>')
            p.append(f'        <ul>\n{ul(s["bullets"])}\n        </ul>')
        elif t == "content":
            p.append(f'        <ul>\n{ul(s["bullets"])}\n        </ul>')
        elif t == "scenario":
            em = s["email"]
            p.append('        <div class="email" role="group" aria-label="نص الرسالة الافتراضية">')
            p.append(f'          <p><strong>من:</strong> <span dir="ltr">{esc(em["from"])}</span></p>')
            p.append(f'          <p><strong>الموضوع:</strong> {esc(em["subject"])}</p>')
            p.append(f'          <p><strong>نص الرسالة:</strong> {esc(em["body"])}</p>')
            p.append("        </div>")
            p.append(f'        <p class="q"><strong>السؤال:</strong> {esc(s["question"])}</p>')
            p.append(f'        <details class="answer"><summary>اعرض التصرف الآمن الصحيح</summary><p>{esc(s["answer"])}</p></details>')
        elif t == "summary":
            p.append(f'        <ul>\n{ul(s["bullets"])}\n        </ul>')
        p.append("      </section>")
        out.append("\n".join(p))
    return "\n".join(out)


def quiz_section(quiz, index):
    p = [f'      <section class="slide" id="slide-{index}" tabindex="-1" aria-labelledby="h-{index}" hidden>']
    p.append('        <span class="eyebrow">التقويم الذاتي</span>')
    p.append(f'        <h2 id="h-{index}">اختبر نفسك</h2>')
    p.append('        <p>اختر إجابة واحدة لكل سؤال، ثم اضغط «تحقق من الإجابة». ستسمع تصفيقًا أو تنبيهًا حسب إجابتك، وبعدها تختار: السؤال التالي، أو إعادة المحاولة، أو اسمع الإجابة الصحيحة.</p>')
    for q in quiz:
        opts = []
        for j, o in enumerate(q["options"]):
            opts.append(f'              <li><label><input type="radio" name="{esc(q["id"])}" value="{j}"> <span>{esc(o)}</span></label></li>')
        p.append(f'        <fieldset class="quiz-item" data-correct="{q["correct"]}" data-id="{esc(q["id"])}">')
        p.append(f'          <legend><span class="qnum">{q["id"][1:]}</span>{esc(q["question"])} <span class="obj">({esc(q["objective"])})</span></legend>')
        p.append(f'          <audio class="narration" controls preload="none" data-a="{esc(q["id"])}.mp3" src="audio/f/{esc(q["id"])}.mp3" aria-label="الشرح الصوتي للسؤال {q["id"][1:]}"></audio>')
        p.append('          <ul class="options">')
        p.extend(opts)
        p.append("          </ul>")
        p.append('          <p class="quiz-actions">')
        p.append('            <button type="button" class="btn check">تحقق من الإجابة</button>')
        p.append('            <button type="button" class="btn ghost reset" hidden>إعادة المحاولة</button>')
        p.append('            <button type="button" class="btn ghost reveal" hidden>اسمع الإجابة الصحيحة</button>')
        p.append('            <button type="button" class="btn ghost nextq" hidden>السؤال التالي</button>')
        p.append('          </p>')
        p.append('          <p class="feedback" role="status" aria-live="polite"></p>')
        p.append('          <audio class="fb-audio" preload="none" data-a="' + esc(q["id"]) + '_fb.mp3" src="audio/f/' + esc(q["id"]) + '_fb.mp3"></audio>')
        p.append('          <p class="fb-correct" hidden>' + esc(q["fbCorrect"]) + "</p>")
        p.append('          <p class="fb-wrong" hidden>' + esc(q["fbWrong"]) + "</p>")
        p.append("        </fieldset>")
    p.append("      </section>")
    return "\n".join(p)


JS = """
  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
  var i = 0;
  var prev = document.getElementById('prev');
  var next = document.getElementById('next');
  var count = document.getElementById('count');
  var bar = document.getElementById('bar');
  var live = document.getElementById('live');
  var autoplay = document.getElementById('autoplay');
  var IS_EMBED = document.documentElement.classList.contains('embed');
  var IS_FRAMED = false;
  try { IS_FRAMED = !!(window.parent && window.parent !== window); } catch (e) { IS_FRAMED = false; }

  /* ---------- الصوت: مؤنث (f) أو مذكر (m) ----------
     الترتيب: ?voice= في الرابط، ثم تفضيل محفوظ، ثم رسالة {hub:'voice'} من الصفحة الأم. */
  var VOICE = 'f';
  try {
    var vq = (location.search.match(/[?&]voice=([mf])(?:&|$)/) || [])[1];
    if (vq) { VOICE = vq; }
    else {
      var prefsRaw = window.localStorage.getItem('hub.sp');
      if (prefsRaw) {
        var prefsObj = JSON.parse(prefsRaw);
        if (prefsObj && (prefsObj.voice === 'm' || prefsObj.voice === 'f')) { VOICE = prefsObj.voice; }
      }
    }
  } catch (e) { /* تجاهل */ }

  function applyVoice() {
    Array.prototype.forEach.call(document.querySelectorAll('audio[data-a]'), function (a) {
      var file = a.getAttribute('data-a');
      var want = 'audio/' + VOICE + '/' + file;
      if (a.getAttribute('src') === want) { return; }
      var playing = !a.paused;
      try { a.pause(); } catch (e) { /* تجاهل */ }
      a.setAttribute('src', want);
      try { a.load(); } catch (e) { /* تجاهل */ }
      if (playing) { try { a.play(); } catch (e2) { /* تجاهل */ } }
    });
  }

  function hubPost(msg) {
    if (!IS_FRAMED) { return; }
    try { window.parent.postMessage(msg, "*"); } catch (e) { /* تجاهل */ }
  }

  function stopAllAudio() {
    Array.prototype.forEach.call(document.querySelectorAll('audio.narration'), function (a) { a.pause(); });
  }

  /* عند بدء أي تلاوة داخل الدرس نُخبر الصفحة الأم لتوقف صوتها */
  Array.prototype.forEach.call(document.querySelectorAll('audio.narration'), function (a) {
    a.addEventListener('play', function () { hubPost({ hub: 'speaking' }); });
  });

  function slideStep(dir) {
    var t = i + dir;
    if (t < 0 || t >= slides.length) {
      hubPost({ hub: 'edge', dir: dir > 0 ? 'next' : 'prev' });
      return;
    }
    i = t;
    render();
  }

  window.addEventListener('message', function (e) {
    var d = e.data || {};
    if (d.hub === 'stop') { stopAllAudio(); return; }
    if (d.hub === 'enter') {
      if (d.dir === 'next') { i = 0; render(); }
      else if (d.dir === 'prev') { i = slides.length - 1; render(); }
      else {
        try { slides[i].focus(); } catch (err) { /* تجاهل */ }
        var a = slides[i].querySelector('audio.narration');
        if (a) { try { a.play(); } catch (err2) { /* تجاهل */ } }
      }
      return;
    }
    if (d.hub === 'read') { slideStep(d.dir === 'prev' ? -1 : 1); return; }
    if (d.hub === 'voice') {
      if (d.voice === 'm' || d.voice === 'f') {
        VOICE = d.voice;
        stopAllAudio();
        applyVoice();
      }
      return;
    }
  });

  function playCurrent() {
    if (!autoplay || !autoplay.checked) { return; }
    var a = slides[i].querySelector('audio.narration');
    if (a) { try { a.play(); } catch (e) {} }
  }
  function render(initial) {
    slides.forEach(function (s, k) { s.hidden = (k !== i); });
    prev.disabled = (i === 0);
    next.disabled = (i === slides.length - 1);
    count.textContent = 'الشريحة ' + (i + 1) + ' من ' + slides.length;
    bar.style.width = Math.round(((i + 1) / slides.length) * 100) + '%';
    live.textContent = 'الشريحة ' + (i + 1) + ' من ' + slides.length;
    // In embed mode the parent page owns the initial focus, so opening the lesson
    // must not scroll past the slide toolbar.
    if (!(initial && IS_EMBED)) { slides[i].focus(); }
    stopAllAudio();
    playCurrent();
  }
  applyVoice();

  if (autoplay) {
    autoplay.addEventListener('change', function () {
      if (autoplay.checked) { playCurrent(); } else { stopAllAudio(); }
    });
  }
  prev.addEventListener('click', function () { if (i > 0) { i--; render(); } });
  next.addEventListener('click', function () { if (i < slides.length - 1) { i++; render(); } });
  document.addEventListener('keydown', function (e) {
    if (e.target.closest && e.target.closest('fieldset')) { return; }
    /* Enter على جسم المستند بعد الدخول إلى الإطار: اقرأ الشريحة الحالية */
    if (e.key === 'Enter' && !e.altKey && !e.ctrlKey && !e.metaKey &&
        (document.activeElement === document.body || document.activeElement === document.documentElement)) {
      e.preventDefault();
      try { slides[i].focus(); } catch (err) { /* تجاهل */ }
      var cur = slides[i].querySelector('audio.narration');
      if (cur) { try { cur.play(); } catch (err2) { /* تجاهل */ } }
      return;
    }
    /* Alt+السهم لأسفل/أعلى للتنقل بين الشرائح بالقراءة (داخل إطار الدرس) */
    if (e.altKey && !e.ctrlKey && !e.metaKey) {
      if (e.key === 'ArrowDown') { e.preventDefault(); slideStep(1); return; }
      if (e.key === 'ArrowUp') { e.preventDefault(); slideStep(-1); return; }
    }
    if (e.key === 'ArrowLeft') { if (i < slides.length - 1) { i++; render(); } }
    else if (e.key === 'ArrowRight') { if (i > 0) { i--; render(); } }
    else if (e.key === 'Home') { i = 0; render(); }
    else if (e.key === 'End') { i = slides.length - 1; render(); }
  });

  Array.prototype.forEach.call(document.querySelectorAll('.quiz-item'), function (item) {
    var check = item.querySelector('.check');
    var reset = item.querySelector('.reset');
    var reveal = item.querySelector('.reveal');
    var nextq = item.querySelector('.nextq');
    var fb = item.querySelector('.feedback');
    var fbAudio = item.querySelector('.fb-audio');
    var sfxOk = new Audio('audio/hub/clap.mp3');
    var sfxBad = new Audio('audio/hub/buzz.mp3');

    function playSfx(ok) {
      try { var a = ok ? sfxOk : sfxBad; a.currentTime = 0; a.play(); } catch (e) { /* تجاهل */ }
    }

    check.addEventListener('click', function () {
      var chosen = item.querySelector('input[type=radio]:checked');
      if (!chosen) {
        fb.className = 'feedback show err';
        fb.textContent = 'لم تختر إجابة. اختر أحد البدائل أولًا.';
        playSfx(false);
        return;
      }
      var ok = Number(chosen.value) === Number(item.dataset.correct);
      fb.className = 'feedback show ' + (ok ? 'ok' : 'err');
      fb.textContent = ok ? 'إجابة صحيحة.' : 'إجابة غير صحيحة.';
      check.disabled = true;
      reset.hidden = false;
      reveal.hidden = false;
      nextq.hidden = false;
      playSfx(ok);
    });

    reveal.addEventListener('click', function () {
      if (fbAudio) {
        try { fbAudio.currentTime = 0; fbAudio.play(); } catch (e) { /* تجاهل */ }
      }
      var p = item.querySelector(fb.classList.contains('ok') ? '.fb-correct' : '.fb-wrong');
      if (p) {
        fb.textContent = (fb.classList.contains('ok') ? 'إجابة صحيحة. ' : 'إجابة غير صحيحة. ') + p.textContent;
      }
    });

    nextq.addEventListener('click', function () {
      var all = Array.prototype.slice.call(document.querySelectorAll('.quiz-item'));
      var idx = all.indexOf(item);
      var target = all[idx + 1];
      if (target) {
        var btn = target.querySelector('.check');
        if (btn) { btn.focus(); }
        if (typeof target.scrollIntoView === 'function') { target.scrollIntoView({ block: 'center' }); }
      } else {
        fb.textContent = (fb.textContent || '') + ' انتهت الأسئلة.';
      }
    });

    reset.addEventListener('click', function () {
      Array.prototype.forEach.call(item.querySelectorAll('input[type=radio]'), function (r) { r.checked = false; });
      fb.className = 'feedback';
      fb.textContent = '';
      check.disabled = false;
      reset.hidden = true;
      reveal.hidden = true;
      nextq.hidden = true;
      var first = item.querySelector('input[type=radio]');
      if (first) { first.focus(); }
    });
  });

  render(true);
"""

# وضع التضمين (?embed=1): الصفحة الأم تُقدّم العنوان والتنقل، فنخفي ترويسة الدرس
BRIDGE_CSS = """
.hero .audio-wrap { margin: 0.6rem 0 0.9rem; }

  /* جملة الربط بين أجزاء الدرس: تتابع منطقي من جزئية للتي بعدها */
  .bridge{
    background:#eef6ff; border-inline-start:6px solid var(--blue); border-radius:12px;
    padding:12px 16px; margin:14px 0 6px; color:#123c60; font-weight:700;
  }
"""

EMBED_CSS = """
  /* ---- Embed mode (?embed=1): the parent site supplies header and navigation ---- */
  html.embed body > header.hero{display:none !important;}
  html.embed a.skip{display:none !important;}
  html.embed body{background:#fff;}
  html.embed main{max-width:1060px; padding-top:24px;}
  html.embed .sr-embed{
    position:absolute !important; width:1px; height:1px; margin:-1px; padding:0;
    overflow:hidden; clip-path:inset(50%); white-space:nowrap; border:0;
  }
"""

EMBED_JS = """
<script>
(function () {
  if (!/[?&]embed=1/.test(location.search)) { return; }
  document.documentElement.className += " embed";
  document.addEventListener("DOMContentLoaded", function () {
    var h = document.querySelector("body > header h1");
    var m = document.querySelector("main");
    if (!h || !m) { return; }
    var t = document.createElement("h1");
    t.className = "sr-embed";
    t.textContent = h.textContent.trim();
    m.insertBefore(t, m.firstChild);
  });
})();
</script>
"""


def build():
    d = json.load(open(ROOT + r"\course.json", encoding="utf-8"))
    meta = d["meta"]
    seq = [s for s in d["slides"] if s["type"] != "title"]

    content_html = content_sections(seq)
    quiz_index = len(seq) + 1
    quiz_html = quiz_section(d["quiz"], quiz_index)

    doc = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta['title'])} - درس تفاعلي</title>
{theme.FONT_LINKS}
<style>{theme.CSS}{BRIDGE_CSS}{EMBED_CSS}</style>
{EMBED_JS}
</head>
<body>
<a class="skip" href="#main">تخطَّ إلى المحتوى الرئيسي</a>
<header class="hero">
  <div class="hero-inner">
    {theme.MASCOT}
    <div>
      <h1>{esc(meta['title'])}</h1>
      <p>{esc(next(s for s in d["slides"] if s["type"] == "title").get("subtitle", ""))}</p>
      <p>{esc(meta["grade"])} • {esc(meta["target"])}</p>
      <div class="audio-wrap">
        <span class="lbl"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" style="vertical-align:-3px"><path d="M3 9v6h4l5 4V5L7 9H3z"/><path d="M16 8a5 5 0 0 1 0 8v-2a3 3 0 0 0 0-4V8z"/></svg> اسمع الترحيب</span>
        <audio class="narration" controls preload="none" data-a="s01.mp3" src="audio/f/s01.mp3" aria-label="الترحيب بالدرس وشرح الشريحة الأولى"></audio>
      </div>
      <div class="chips">
        <span class="chip">نص كامل وقارئ شاشة</span>
        <span class="chip">شرح صوتي لكل شريحة</span>
        <span class="chip">لا يعتمد على اللون وحده</span>
        <span class="chip">لوحة المفاتيح</span>
      </div>
    </div>
  </div>
  <svg class="wave" viewBox="0 0 1200 26" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M0 12 C 200 26 400 0 600 12 S 1000 26 1200 10 L1200 26 L0 26 Z" fill="#eef6fe"/></svg>
</header>
<main id="main">
  <p id="live" class="progress" role="status" aria-live="polite"></p>
  <div class="toolbar">
    <div class="group">
      <button id="prev" type="button" class="btn">السابق</button>
      <button id="next" type="button" class="btn sun">التالي</button>
    </div>
    <label class="autoplay"><input type="checkbox" id="autoplay"> تشغيل الشرح الصوتي تلقائيًا</label>
    <div class="bar" aria-hidden="true"><i id="bar"></i></div>
    <div class="progress" id="count"></div>
  </div>
  <div class="card">
{content_html}
{quiz_html}
  </div>
  <p class="srcnote">{esc(meta['sourceNote'])}</p>
</main>
<script>
{JS}
</script>
</body>
</html>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print("saved:", OUT)
    print("slides:", len(seq) + 1, "quiz:", len(d["quiz"]))


if __name__ == "__main__":
    build()
