#!/usr/bin/env python3
"""Prepare site photos: download originals from Wikimedia Commons (cached in
tools/.cache), crop each to the exact shape of the frame it fills, and export
sharp WebP + JPEG at several widths into public/images.

    python3 tools/images.py

To use your own photo instead, drop a JPG into tools/.cache/<id>.jpg (e.g.
tools/.cache/hero.jpg), update its author/licence in photos.config.json,
and run this script, then build.py.
"""
import json, pathlib, subprocess, time, urllib.parse
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools/.cache"
OUT = ROOT / "public/images"
CONFIG = json.loads((ROOT / "tools/photos.config.json").read_text(encoding="utf-8"))
WIDTHS = [480, 800, 1200, 1600]
UA = "YiasemiStaticSite/1.0 (image build script)"

def fetch(title, dest):
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url", "iiurlwidth": "1920", "format": "json"})
    for attempt in range(8):
        r = subprocess.run(["curl", "-sS", "-A", UA, api], capture_output=True, text=True)
        try:
            page = next(iter(json.loads(r.stdout)["query"]["pages"].values()))
            src = page["imageinfo"][0].get("thumburl") or page["imageinfo"][0]["url"]
            tmp = dest.with_suffix(".part")
            d = subprocess.run(["curl", "-sSL", "-A", UA, "-o", str(tmp), "-w", "%{http_code}", src], capture_output=True, text=True)
            if d.stdout == "200":
                Image.open(tmp).verify()          # make sure it is a real image, not an error page
                tmp.rename(dest)
                return
        except Exception:
            pass
        time.sleep(10 * (attempt + 1))
    raise SystemExit(f"could not download {title}")

def crop(im, aspect, focal):
    if not aspect:
        return im
    aw, ah = map(int, aspect.split(":"))
    W, H = im.size
    target = aw / ah
    fx, fy = focal or (0.5, 0.5)
    if W / H > target:                      # too wide -> trim sides
        nw = round(H * target); x = round((W - nw) * fx)
        return im.crop((x, 0, x + nw, H))
    nh = round(W / target); y = round((H - nh) * fy)  # too tall -> trim top/bottom
    return im.crop((0, y, W, y + nh))

def main():
    CACHE.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for c in CONFIG:
        src = CACHE / f'{c["id"]}.jpg'
        if not src.exists():
            print("downloading", c["title"]); fetch(c["title"], src); time.sleep(3)
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im = crop(im, c.get("aspect"), c.get("focal"))
        widths = sorted({w for w in WIDTHS if w < im.width} | {min(im.width, WIDTHS[-1])})
        for w in widths:
            h = round(im.height * w / im.width)
            r = im.resize((w, h), Image.LANCZOS)
            r.save(OUT / f'{c["base"]}-{w}.webp', "WEBP", quality=80, method=6)
            r.save(OUT / f'{c["base"]}-{w}.jpg', "JPEG", quality=82, optimize=True, progressive=True)
        big = widths[-1]
        manifest[c["id"]] = {"base": c["base"], "widths": widths, "w": big, "h": round(im.height * big / im.width),
                             "alt": c["alt"], "cat": c.get("cat"), "author": c["author"], "license": c["license"],
                             "licurl": c["licurl"], "source": c["source"], "title": c["title"]}
        print(f'{c["id"]:11s} {im.width}x{im.height} -> {widths}')
    # Open Graph / social share image, exactly 1200x630
    og_src = CACHE / "plaka-1.jpg"
    if og_src.exists():
        og = crop(ImageOps.exif_transpose(Image.open(og_src)).convert("RGB"), "40:21", (0.5, 0.6)).resize((1200, 630), Image.LANCZOS)
        og.save(OUT / "og.jpg", "JPEG", quality=84, optimize=True, progressive=True)
    (OUT / "photos.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("manifest:", len(manifest))

if __name__ == "__main__":
    main()
