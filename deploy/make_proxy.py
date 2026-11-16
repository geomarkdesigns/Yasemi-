#!/usr/bin/env python3
"""Generate the interim Vercel proxy deployment (used until the Vercel GitHub app has repo access).

    python3 deploy/make_proxy.py            # writes deploy/vercel.proxy.json and deploy/deployment.json

Pages come from the current commit. Images, fonts and the favicon come from the commit where they
last changed, so their CDN URLs stay the same (and cached) across content-only releases.
Before deploying, warm the CDN:  python3 deploy/make_proxy.py --warm
"""
import json, pathlib, subprocess, sys, time, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent.parent
git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()

head = git("rev-parse", "HEAD")
assets = git("log", "-1", "--format=%H", "--", "public/images/*.jpg", "public/images/*.webp", "public/images/*.png",
             "public/images/*.svg", "public/fonts", "public/favicon.ico")
CDN = "https://cdn.jsdelivr.net/gh/geomarkdesigns/Yasemi-@{}/public"
pages = "menu|photos|visit|credits|privacy"
sec = json.loads((ROOT / "deploy/security-headers.json").read_text()) + [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]
cfg = {"trailingSlash": False,
       "rewrites": [
           {"source": "/images/:path*", "destination": CDN.format(assets) + "/images/:path*"},
           {"source": "/fonts/:path*", "destination": CDN.format(assets) + "/fonts/:path*"},
           {"source": "/favicon.ico", "destination": CDN.format(assets) + "/favicon.ico"},
           {"source": "/", "destination": CDN.format(head) + "/index.html"},
           {"source": "/el", "destination": CDN.format(head) + "/el/index.html"},
           {"source": f"/:page({pages})", "destination": CDN.format(head) + "/:page.html"},
           {"source": f"/el/:page({pages})", "destination": CDN.format(head) + "/el/:page.html"},
           {"source": "/:path((?!__access$|__logout$).*)", "destination": CDN.format(head) + "/:path"}],
       "headers": [
           {"source": "/((?!.*\\.).*)", "headers": [{"key": "Content-Type", "value": "text/html; charset=utf-8"},
                                                   {"key": "x-vercel-enable-rewrite-caching", "value": "0"},
                                                   {"key": "Cache-Control", "value": "private, no-store"}]},
           {"source": "/(.*)", "headers": sec}]}
(ROOT / "deploy/vercel.proxy.json").write_text(json.dumps(cfg, indent=1) + "\n")
body = {"name": "yiasemi", "project": "yiasemi", "target": "production", "files": [
    {"file": "vercel.json", "encoding": "utf-8", "data": json.dumps(cfg, separators=(",", ":"))},
    {"file": "middleware.js", "encoding": "utf-8", "data": (ROOT / "deploy/middleware.js").read_text()}]}
(ROOT / "deploy/deployment.json").write_text(json.dumps(body))
print("pages @", head, "\nassets @", assets)

if "--warm" in sys.argv:
    files = [f"{CDN.format(head)}/{p}" for p in ["index.html", "el/index.html", "404.html", "js/main.js", "sitemap.xml", "robots.txt"]
             + [f"{x}.html" for x in pages.split("|")] + [f"el/{x}.html" for x in pages.split("|")]]
    import re
    used = set()
    for f in (ROOT / "public").rglob("*.html"):
        used |= set(re.findall(r"/(images/[a-z0-9-]+\.(?:webp|jpg|png|svg))", f.read_text(encoding="utf-8")))
    files += [f"{CDN.format(assets)}/{u}" for u in sorted(used)] + [f"{CDN.format(assets)}/fonts/{p.name}" for p in (ROOT / "public/fonts").iterdir()]
    bad = []
    for u in files:
        for i in range(6):
            try:
                if urllib.request.urlopen(u, timeout=30).status == 200: break
            except Exception:
                time.sleep(3 * (i + 1))
        else:
            bad.append(u)
    print(f"warmed {len(files)} files; failed: {bad or 'none'}")
    sys.exit(1 if bad else 0)
