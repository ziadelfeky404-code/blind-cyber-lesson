# -*- coding: utf-8 -*-
"""فحص نحوي لكل كتل <script> في صفحات المشروع عبر node --check."""
import os
import re
import subprocess
import sys
import tempfile

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
pages = [p for p in os.listdir(ROOT) if p.endswith(".html")]
bad = 0
for page in sorted(pages):
    path = os.path.join(ROOT, page)
    with open(path, encoding="utf-8") as f:
        html = f.read()
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S | re.I)
    for i, code in enumerate(blocks, 1):
        if not code.strip():
            continue
        # كتلة بيانات JSON فقط (مثل ACT_AUDIO) ليست كودًا كاملًا؛ نفحصها أيضًا لأنها كود JS صالح
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tmp:
            tmp.write(code)
            name = tmp.name
        res = subprocess.run(["node", "--check", name], capture_output=True, text=True)
        os.unlink(name)
        if res.returncode != 0:
            bad += 1
            print("FAIL %s block %d: %s" % (page, i, res.stderr.strip().splitlines()[-3:]))
        else:
            print("ok   %s block %d (%d chars)" % (page, i, len(code)))
print("pages:", len(pages), "failures:", bad)
sys.exit(1 if bad else 0)
