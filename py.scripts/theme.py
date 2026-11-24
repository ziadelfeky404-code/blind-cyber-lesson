# -*- coding: utf-8 -*-
"""Shared child-friendly design system for the cyber-threats lesson pages.

Keeps high contrast, keyboard focus, RTL and text-first access (per the
visual-impairment and ethics guidelines) while giving a warm, playful look.
"""

FONT_LINKS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+Bhaijaan+2:wght@500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">"""

CSS = """
  :root{
    --ink:#12263a; --navy:#0b3d6b; --blue:#0f5aa0; --blue2:#1b6ec2;
    --sky:#eaf4fe; --sun:#ffcf3f; --sun-dk:#7a5a00;
    --green:#0b6b34; --green-bg:#e6f6ec; --red:#b3261e; --red-bg:#fdecea;
    --line:#cfe0f2; --card:#ffffff; --focus:#b35c00;
    --r:22px; --shadow:0 8px 24px rgba(15,90,160,.12);
  }
  *{box-sizing:border-box;}
  html{scroll-behavior:smooth;}
  body{
    margin:0; color:var(--ink);
    font-family:"Tajawal","Segoe UI",Tahoma,Arial,sans-serif;
    font-size:19px; line-height:1.95; background:#eef6fe;
  }
  h1,h2,h3,h4,legend,.display{font-family:"Baloo Bhaijaan 2","Tajawal","Segoe UI",Tahoma,sans-serif; line-height:1.45;}
  a{color:var(--blue);}
  a.skip{position:absolute; inset-inline-start:-999px; top:0; z-index:60; background:#000; color:#fff; padding:10px 16px; border-radius:0 0 12px 0;}
  a.skip:focus{inset-inline-start:0;}
  :focus-visible{outline:3px solid var(--focus); outline-offset:3px; border-radius:6px;}

  .wrap{max-width:960px; margin:0 auto; padding:0 16px 40px;}

  /* Hero header */
  .hero{
    position:relative; color:#fff; padding:26px 24px 34px;
    background:linear-gradient(140deg,#0b3d6b 0%,#11538f 55%,#1667a8 100%);
    border-radius:0 0 30px 30px;
  }
  .hero .inner{max-width:900px; margin:0 auto; display:flex; gap:18px; align-items:center; flex-wrap:wrap;}
  .hero h1{margin:.1rem 0 .3rem; font-size:clamp(1.6rem,1.2rem + 2vw,2.4rem); font-weight:800;}
  .hero p{margin:.15rem 0; color:#eaf4fe; font-size:1rem;}
  .mascot{width:118px; height:auto; flex:0 0 auto; filter:drop-shadow(0 6px 10px rgba(0,0,0,.25));}
  .chips{display:flex; gap:8px; flex-wrap:wrap; margin-top:10px;}
  .chip{background:#ffffff; border:2px solid #ffffff; color:#0b3d6b; border-radius:999px; padding:3px 12px; font-size:.82rem; font-weight:700;}
  .wave{display:block; width:100%; height:26px;}

  main{max-width:960px; margin:0 auto; padding:20px 18px 40px;}

  .card{
    background:var(--card); border:3px solid var(--line); border-radius:var(--r);
    padding:22px 24px; box-shadow:var(--shadow);
  }
  .card:focus{outline:none;}
  .card:focus-visible{outline:4px solid var(--focus); outline-offset:3px;}

  .eyebrow{display:inline-block; background:var(--sky); color:var(--blue);
    font-weight:800; border-radius:999px; padding:2px 14px; font-size:.85rem; margin-bottom:8px;}

  /* Big friendly buttons */
  .btn{
    font-family:inherit; font-size:1rem; font-weight:800; cursor:pointer;
    border:3px solid var(--blue); background:var(--blue); color:#fff;
    border-radius:999px; padding:12px 26px; min-height:50px;
    box-shadow:0 4px 0 rgba(11,61,107,.35); transition:transform .06s ease, background .15s;
  }
  .btn:hover{background:var(--blue2);}
  .btn:active{transform:translateY(2px); box-shadow:0 2px 0 rgba(11,61,107,.35);}
  .btn[disabled]{opacity:.45; cursor:not-allowed; box-shadow:none;}
  .btn.sun{background:var(--sun); border-color:#e7b400; color:#4a3800; box-shadow:0 4px 0 #b98a00;}
  .btn.ghost{background:#fff; color:var(--blue);}

  .toolbar{display:flex; gap:12px; align-items:center; justify-content:space-between; flex-wrap:wrap; margin:16px 0;}
  .toolbar .group{display:flex; gap:12px; flex-wrap:wrap;}
  .progress{font-weight:800; color:var(--navy);}
  .bar{height:16px; background:#dcebf9; border-radius:999px; overflow:hidden; border:2px solid var(--line); min-width:180px; flex:1 1 180px;}
  .bar > i{display:block; height:100%; background:linear-gradient(90deg,var(--sun),#ff9f1c); width:0; transition:width .3s;}

  .autoplay{display:inline-flex; gap:10px; align-items:center; background:#fff; border:3px solid var(--line);
    border-radius:999px; padding:8px 16px; font-weight:800; cursor:pointer; color:var(--navy);}
  .autoplay input{width:22px; height:22px; accent-color:var(--blue);}

  /* Slide */
  .slide{display:block;}
  .slide[hidden]{display:none;}
  .slide h2{color:var(--navy); font-size:1.7rem; margin:2px 0 14px;}
  .slide ul{padding-inline-start:26px;}
  .slide li{margin:.5rem 0;}
  .slide li::marker{color:var(--blue2); font-weight:800;}

  .audio-wrap{background:var(--sky); border:3px dashed #a9cdf0; border-radius:18px; padding:12px 16px; margin:4px 0 18px;}
  .audio-wrap .lbl{display:block; font-weight:800; color:var(--navy); margin-bottom:6px;}
  audio.narration{width:100%; max-width:560px; height:44px;}

  .email{background:#fff8e7; border:3px solid #ffd98a; border-radius:18px; padding:14px 18px;}
  .email p{margin:.35rem 0;}
  .q{background:var(--sky); border-radius:14px; padding:10px 16px; font-weight:700;}
  details{background:#f4f9ff; border:3px solid var(--line); border-radius:16px; padding:6px 16px; margin-top:10px;}
  details summary{cursor:pointer; font-weight:800; color:var(--blue); padding:8px 0;}

  /* Quiz */
  .quiz-item{border:3px solid var(--line); border-radius:var(--r); padding:18px 20px; margin:18px 0; background:#fff;}
  .quiz-item legend{font-weight:800; color:var(--navy); font-size:1.12rem; padding:0 8px;}
  .qnum{display:inline-grid; place-items:center; width:34px; height:34px; margin-inline-end:6px;
    background:var(--sun); color:#4a3800; border-radius:50%; font-weight:800;}
  .obj{font-weight:600; color:#5b6b7b; font-size:.85rem;}
  .options{list-style:none; padding:0; margin:12px 0 0; display:grid; gap:10px;}
  .options label{display:flex; gap:12px; align-items:flex-start; padding:12px 16px; border:3px solid var(--line);
    border-radius:16px; cursor:pointer; background:#fff; transition:border-color .12s, background .12s;}
  .options label:hover{background:var(--sky);}
  .options label:has(input:checked){border-color:var(--blue); background:#e7f1fd; box-shadow:inset 0 0 0 1px var(--blue);}
  .options input{width:22px; height:22px; margin-top:4px; accent-color:var(--blue); flex:0 0 auto;}
  .feedback{font-weight:800; margin-top:14px; padding:14px 16px; border-radius:16px; display:none;}
  .feedback.show{display:block;}
  .feedback.ok{color:var(--green); background:var(--green-bg); border:3px solid #9ad4b0;}
  .feedback.err{color:var(--red); background:var(--red-bg); border:3px solid #f0b0ab;}
  .feedback.ok::before{content:"\\2714  ";}
  .feedback.err::before{content:"\\2718  ";}

  details.answer{background:#f3f8ff; border:3px solid var(--line); border-radius:16px; padding:6px 16px; margin-top:14px;}
  details.answer summary{cursor:pointer; font-weight:800; color:var(--blue); padding:6px 0;}

  .srcnote{color:#4b5b6b; font-size:.88rem; border-top:2px dashed var(--line); margin-top:26px; padding-top:12px;}

  @media (max-width:560px){
    body{font-size:18px;}
    .mascot{width:92px;}
    main{padding:16px 12px 32px;}
    .card{padding:18px 16px;}
  }
  @media (prefers-reduced-motion:reduce){
    *{transition:none !important; scroll-behavior:auto !important;}
  }
  @media print{
    body{background:#fff;}
    .toolbar,.autoplay,.btn{display:none !important;}
    .card{box-shadow:none; border-color:#999;}
  }
"""

MASCOT = """<svg class="mascot" viewBox="0 0 140 152" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="روبوت ودود يحمل درعًا للحماية الرقمية">
  <line x1="70" y1="12" x2="70" y2="28" stroke="#08324f" stroke-width="5" stroke-linecap="round"/>
  <circle cx="70" cy="10" r="7" fill="#ffcf3f" stroke="#08324f" stroke-width="4"/>
  <rect x="30" y="28" width="80" height="62" rx="22" fill="#9ad6ff" stroke="#08324f" stroke-width="5"/>
  <rect x="42" y="44" width="56" height="36" rx="13" fill="#08324f"/>
  <circle cx="59" cy="60" r="7" fill="#fff"/>
  <circle cx="81" cy="60" r="7" fill="#fff"/>
  <circle cx="60" cy="61" r="3.2" fill="#08324f"/>
  <circle cx="82" cy="61" r="3.2" fill="#08324f"/>
  <path d="M60 71 q10 9 20 0" stroke="#ffcf3f" stroke-width="3.4" fill="none" stroke-linecap="round"/>
  <rect x="40" y="96" width="60" height="48" rx="18" fill="#1b6ec2" stroke="#08324f" stroke-width="5"/>
  <path d="M70 100 l22 8 v15 q0 15 -22 23 q-22 -8 -22 -23 v-15 z" fill="#ffcf3f" stroke="#08324f" stroke-width="5" stroke-linejoin="round"/>
  <path d="M62 122 l6 7 l13 -15" stroke="#08324f" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

WAVE = """<svg class="wave" viewBox="0 0 1200 26" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M0 12 C 200 26 400 0 600 12 S 1000 26 1200 10 L1200 26 L0 26 Z" fill="#eef6fe"/></svg>"""

# Friendly extra classes shared by the guide/activity pages
EXTRA = """
  .hero{position:relative;}
  .hero-inner{display:flex; gap:16px; align-items:center; flex-wrap:wrap; max-width:1000px; margin:0 auto;}
  .lead{background:#fff; border:3px solid var(--line); border-radius:var(--r); padding:18px 22px; box-shadow:var(--shadow); margin:18px 0;}
  .grid{display:grid; gap:16px; grid-template-columns:repeat(auto-fit,minmax(240px,1fr));}
  .step{background:#fff; border:3px solid var(--line); border-radius:var(--r); padding:18px 20px; box-shadow:var(--shadow); position:relative;}
  .step .num{position:absolute; top:-16px; inset-inline-start:18px; width:38px; height:38px; border-radius:50%;
    background:var(--sun); color:#4a3800; font-weight:800; display:grid; place-items:center; border:3px solid #e7b400;}
  .step h3{margin:8px 0 6px; color:var(--navy);}
  .keys{background:var(--sky); border:3px dashed #a9cdf0; border-radius:var(--r); padding:16px 22px;}
  .kbd{display:inline-block; background:#fff; border:2px solid #b9cde3; border-bottom-width:4px; border-radius:10px; padding:1px 10px; font-weight:800; font-family:monospace;}
  table.tbl{width:100%; border-collapse:collapse; background:#fff; border-radius:16px; overflow:hidden; box-shadow:var(--shadow);}
  table.tbl th,table.tbl td{border-bottom:2px solid #e2ebf5; padding:12px 14px; text-align:right;}
  table.tbl th{background:var(--navy); color:#fff;}
  .note{background:#fff8e7; border:3px solid #ffd98a; border-radius:var(--r); padding:16px 22px;}
  footer.foot{margin:26px 0 40px; text-align:center; color:#4b5b6b; font-size:.95rem;}
"""
