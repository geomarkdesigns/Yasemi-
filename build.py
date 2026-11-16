#!/usr/bin/env python3
"""Yiasemi static site generator.

Reads content/site.json (café details) and content/menu.json (official menu),
then writes English pages at /, Greek pages at /el/, plus sitemap.xml,
robots.txt, manifest, 404 and vercel.json headers into ./public.

    python3 build.py

Café facts and the menu live ONLY in content/*.json.
Interface copy lives below as (English, Greek) pairs.
"""
import base64, datetime, hashlib, json, pathlib, sys
from sitegen.core import (esc, pick, url as _url, abs_url as _abs, fmt_price, DIETS,
                          validate_menu, hours_rows, opening_hours_ld, maps_links)

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "public"
BASE = "https://yiasemi.vercel.app"          # change to the custom domain when there is one
SITE = json.loads((ROOT / "content/site.json").read_text(encoding="utf-8"))
MENU = json.loads((ROOT / "content/menu.json").read_text(encoding="utf-8"))
PHOTOS = json.loads((OUT / "images/photos.json").read_text(encoding="utf-8")) if (OUT / "images/photos.json").exists() else {}
TODAY = datetime.date.today().isoformat()
LANG = "en"

THEME_JS = 'try{var t=localStorage.getItem("theme")||"light";document.documentElement.setAttribute("data-theme",t)}catch(e){}document.documentElement.classList.add("js")'
THEME_HASH = "sha256-" + base64.b64encode(hashlib.sha256(THEME_JS.encode()).digest()).decode()

def _min_css(css):
    import re
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css).replace(";}", "}")
    return css.strip()
# CSS is inlined (≈7 KB gzipped) so the first paint needs no extra round trip.
INLINE_CSS = _min_css((OUT / "css/fonts.css").read_text(encoding="utf-8") + (OUT / "css/style.css").read_text(encoding="utf-8"))

def T(en, el): return el if LANG == "el" else en
def P(v): return pick(v, LANG)
def url(path, lang=None): return _url(path, lang or LANG)
def abs_url(path, lang=None): return _abs(BASE, path, lang or LANG)
def ver(rel): return hashlib.sha1((OUT / rel).read_bytes()).hexdigest()[:8]

A = SITE["address"]
NAME = SITE["name"]
PHONE, PHONE_TXT = SITE["phone"], SITE["phoneDisplay"]
MAPS = maps_links("Yiasemi", A["street"]["en"], A["postalCode"], A["city"]["en"])
def street_line(): return f'{P(A["street"])}, {P(A["area"])}, {A["postalCode"]} {P(A["city"])}'

# ------------------------------------------------------------ graphics
def jasmine(cls="", fill=True, style=""):
    petals = "".join(f'<ellipse cx="20" cy="10.5" rx="5.2" ry="8.5" transform="rotate({a} 20 20)"/>' for a in (0, 72, 144, 216, 288))
    st = f' style="{style}"' if style else ""
    if fill:
        return f'<svg class="{cls}"{st} viewBox="0 0 40 40" aria-hidden="true" focusable="false"><g fill="currentColor">{petals}</g><circle cx="20" cy="20" r="3.4" fill="var(--bg)"/></svg>'
    return f'<svg class="{cls}"{st} viewBox="0 0 40 40" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor" stroke-width="1.4">{petals}<circle cx="20" cy="20" r="3"/></g></svg>'

ARROW = '<span class="arrow" aria-hidden="true">→</span>'
ICON = {
 "sun": '<svg class="glyph" viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" aria-hidden="true"><path d="M4 24h26"/><path d="M10 24a7 7 0 0 1 14 0"/><path d="M17 9v3M8 13l2 2M26 13l-2 2"/></svg>',
 "noon": '<svg class="glyph" viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" aria-hidden="true"><circle cx="17" cy="17" r="6"/><path d="M17 4v3M17 27v3M4 17h3M27 17h3M8 8l2 2M24 24l2 2M8 26l2-2M24 10l2-2"/></svg>',
 "cup": '<svg class="glyph" viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" aria-hidden="true"><path d="M7 14h17v6a7 7 0 0 1-7 7h-3a7 7 0 0 1-7-7z"/><path d="M24 16h2a3 3 0 0 1 0 6h-2"/><path d="M12 5c-1 2 1 3 0 5M17 5c-1 2 1 3 0 5"/></svg>',
 "moon": '<svg class="glyph" viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M25 20.5A10 10 0 1 1 13.5 9a8 8 0 0 0 11.5 11.5z"/><path d="M25 6v4M23 8h4"/></svg>',
 "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
 "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
 "insta": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
 "leaf": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M5 19c0-8 5-14 15-14 0 10-6 15-14 15"/><path d="M5 19c3-4 6-6 9-8"/></svg>',
 "bread": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 11a4 4 0 0 1 2-7h10a4 4 0 0 1 2 7v8a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1z"/><path d="M9 9v3M13 9v3"/></svg>',
 "coffee": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 9h12v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M16 11h1.5a2.5 2.5 0 0 1 0 5H16"/><path d="M8 3v2M12 3v2"/></svg>',
}

# ------------------------------------------------------------ photos
def pic(pid, cls="", color="c-stone", sizes="100vw", eager=False, extra="", cap=None, full=False, alt_in_caption=False):
    p = PHOTOS.get(pid)
    ph = f'<div class="ph">{jasmine(fill=False)}</div>'
    if not p:
        return f'<figure class="frame {color} {cls}"{extra}>{ph}</figure>'
    alt = "" if alt_in_caption else esc(p["alt"][LANG])   # caption already describes it: avoid double reading
    webp = ", ".join(f'/images/{p["base"]}-{w}.webp {w}w' for w in p["widths"])
    jpg = ", ".join(f'/images/{p["base"]}-{w}.jpg {w}w' for w in p["widths"])
    mid = p["widths"][min(1, len(p["widths"]) - 1)]
    load = ('loading="eager" fetchpriority="high"' if eager == "high" or (eager is True and pid == "hero") else 'loading="eager"') if eager else 'loading="lazy"'
    caption = f'<figcaption>{cap}</figcaption>' if cap else ""
    fd = (f' data-full="/images/{p["base"]}-{p["widths"][-1]}.webp" data-alt="{esc(p["alt"][LANG])}"') if full else ""
    return (f'<figure class="frame {color} {cls}"{extra}{fd}>{ph}<picture>'
            f'<source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="/images/{p["base"]}-{mid}.jpg" srcset="{jpg}" sizes="{sizes}" alt="{alt}" '
            f'width="{p["w"]}" height="{p["h"]}" {load} decoding="async"></picture>{caption}</figure>')

def credit(pid):
    p = PHOTOS.get(pid)
    if not p: return ""
    return f'{T("Photo", "Φωτογραφία")}: {esc(p["author"])} · {esc(p["license"])}'

def img_abs(pid, w=None):
    p = PHOTOS.get(pid)
    if not p: return BASE + "/images/og.jpg"
    return f'{BASE}/images/{p["base"]}-{w or p["widths"][-1]}.jpg'

# ------------------------------------------------------------ structured data
def address_ld():
    return {"@type": "PostalAddress", "streetAddress": P(A["street"]), "addressLocality": P(A["city"]),
            "addressRegion": P(A["region"]), "postalCode": A["postalCode"], "addressCountry": A["country"]}

def cafe_ld():
    d = {"@type": ["CafeOrCoffeeShop", "Restaurant"], "@id": f"{BASE}/#cafe",
         "name": "Yiasemi", "alternateName": ["Γιασεμί", "Yiasemi café bistrot"],
         "description": T("Traditional café bistrot half way up the stepped Mnisikleous Street in Plaka, Athens, serving coffee, drinks, homemade pies and desserts.",
                          "Παραδοσιακό καφέ μπιστρό στα μισά της σκαλωτής οδού Μνησικλέους στην Πλάκα, με καφέ, ποτά, σπιτικές πίτες και γλυκά."),
         "url": abs_url(""), "telephone": PHONE, "address": address_ld(),
         "image": [img_abs(k) for k in ("hero", "evening-1") if k in PHOTOS],
         "logo": BASE + "/images/icon-512.png",
         "servesCuisine": ["Greek", "Coffee", "Vegetarian"],
         "hasMenu": abs_url("menu") + "#menu", "priceRange": "€",
         "acceptsReservations": None,
         "sameAs": [u for u in (SITE.get("instagram"), SITE.get("officialWebsite")) if u]}
    if SITE.get("geo"):
        d["geo"] = {"@type": "GeoCoordinates", "latitude": SITE["geo"]["lat"], "longitude": SITE["geo"]["lng"]}
    if SITE.get("openingHours"):
        d["openingHoursSpecification"] = opening_hours_ld(SITE["openingHours"])
    if SITE.get("email"):
        d["email"] = SITE["email"]
    return {k: v for k, v in d.items() if v is not None}

def website_ld():
    return {"@type": "WebSite", "@id": f"{BASE}/#website", "url": BASE + "/", "name": "Yiasemi",
            "alternateName": "Γιασεμί", "inLanguage": ["en", "el"], "publisher": {"@id": f"{BASE}/#cafe"}}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "@id": f"{items[-1][1]}#breadcrumb",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def webpage_ld(path, name, desc, kind="WebPage", img=None):
    return {"@type": kind, "@id": abs_url(path) + "#webpage", "url": abs_url(path), "name": name, "description": desc,
            "inLanguage": LANG, "isPartOf": {"@id": f"{BASE}/#website"}, "about": {"@id": f"{BASE}/#cafe"},
            "breadcrumb": {"@id": abs_url(path) + "#breadcrumb"},
            "primaryImageOfPage": {"@type": "ImageObject", "url": img or img_abs("hero")}}

# ------------------------------------------------------------ layout
NAV = [("", ("Home", "Αρχική")), ("menu", ("Menu", "Μενού")), ("photos", ("Photos", "Φωτογραφίες")), ("visit", ("Visit", "Επίσκεψη"))]

def head(path, title, desc, ld, og_img=None, noindex=False):
    other = "el" if LANG == "en" else "en"
    og_img = og_img or BASE + "/images/og.jpg"
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    alts = "" if noindex else (
        f'<link rel="alternate" hreflang="en" href="{abs_url(path, "en")}">\n'
        f'<link rel="alternate" hreflang="el" href="{abs_url(path, "el")}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{abs_url(path, "en")}">\n')
    graph = json.dumps({"@context": "https://schema.org", "@graph": ld}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pre = ""
    if path == "" and "hero" in PHOTOS:
        p = PHOTOS["hero"]
        ss = ", ".join(f'/images/{p["base"]}-{w}.webp {w}w' for w in p["widths"])
        pre = f'<link rel="preload" as="image" type="image/webp" imagesrcset="{ss}" imagesizes="(max-width: 960px) 92vw, 440px" fetchpriority="high">\n'
    nav = "".join(f'<li><a href="{url(p)}"{" aria-current=\"page\"" if p == path else ""}>{T(*n)}</a></li>' for p, n in NAV)
    return f'''<!doctype html>
<html lang="{LANG}" dir="ltr" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{abs_url(path)}">
{alts}<meta name="theme-color" content="#f6f0e6">
<meta name="format-detection" content="telephone=yes">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{T("Yiasemi · Plaka, Athens", "Γιασεμί · Πλάκα, Αθήνα")}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{abs_url(path)}">
<meta property="og:locale" content="{"el_GR" if LANG == "el" else "en_GB"}">
<meta property="og:locale:alternate" content="{"en_GB" if LANG == "el" else "el_GR"}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(T("Mnisikleous Street in Plaka, Athens", "Η οδός Μνησικλέους στην Πλάκα"))}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/images/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preload" href="/fonts/gfs-didot-{"greek" if LANG == "el" else "latin"}.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/commissioner-{"greek" if LANG == "el" else "latin"}.woff2" as="font" type="font/woff2" crossorigin>
{pre}<style>{INLINE_CSS}</style>
<script>{THEME_JS}</script>
<script src="/js/main.js?v={ver("js/main.js")}" defer></script>
<script type="application/ld+json">{graph}</script>
</head>
<body>
<a class="skip" href="#main">{T("Skip to content", "Μετάβαση στο περιεχόμενο")}</a>
<header class="site-header">
  <nav class="wrap nav" aria-label="{T("Main", "Κύριο μενού")}">
    <a href="{url("")}" class="logo">{jasmine()}<span>{T("Yiasemi", "Γιασεμί")}</span></a>
    <ul class="links" id="site-links">{nav}</ul>
    <div class="controls">
      <a class="pill-btn lang-link" href="{url(path, other)}" hreflang="{other}" lang="{other}" aria-label="{"EN, read in English" if other == "en" else "ΕΛ, διαβάστε στα Ελληνικά"}">{"EN" if other == "en" else "ΕΛ"}</a>
      <button class="pill-btn" id="theme-toggle" type="button" aria-pressed="false" aria-label="{T("Dark mode", "Σκοτεινή λειτουργία")}">
        <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
      <button class="pill-btn menu-toggle" type="button" aria-controls="site-links" aria-expanded="false" aria-label="{T("Menu", "Μενού")}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M4 9h16M4 15h16"/></svg>
      </button>
    </div>
  </nav>
</header>
<main id="main" tabindex="-1">
'''

def foot():
    ig = f'<li><a href="{SITE["instagram"]}" rel="noopener" target="_blank">Instagram ↗</a></li>' if SITE.get("instagram") else ""
    return f'''</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="meander" aria-hidden="true"></div>
    <div class="foot-grid">
      <div>
        <a href="{url("")}" class="logo">{jasmine()}<span>{T("Yiasemi", "Γιασεμί")}</span></a>
        <p class="muted foot-note">{T("Coffee, drinks, homemade pies and desserts, half way up the steps of Mnisikleous.", "Καφές, ποτά, σπιτικές πίτες και γλυκά, στα μισά των σκαλιών της Μνησικλέους.")}</p>
      </div>
      <div>
        <h2 class="foot-h">{T("Explore", "Περιηγηθείτε")}</h2>
        <ul>{"".join(f'<li><a href="{url(p)}">{T(*n)}</a></li>' for p, n in NAV[1:])}{ig}</ul>
      </div>
      <div>
        <h2 class="foot-h">{T("Find us", "Βρείτε μας")}</h2>
        <address><ul>
          <li>{P(A["street"])}, {P(A["area"])}</li>
          <li>{A["postalCode"]} {P(A["city"])}</li>
          <li><a href="tel:{PHONE}">{PHONE_TXT}</a></li>
        </ul></address>
      </div>
    </div>
    <div class="wordmark" aria-hidden="true">Γιασεμί</div>
    <div class="foot-base">
      <span>&copy; <span id="year">2026</span> {T("Yiasemi", "Γιασεμί")}</span>
      <span class="foot-links"><a href="{url("privacy")}">{T("Privacy", "Απόρρητο")}</a><a href="{url("credits")}">{T("Photo credits", "Πηγές φωτογραφιών")}</a></span>
    </div>
  </div>
</footer>
<nav class="dock" aria-label="{T("Quick actions", "Γρήγορες ενέργειες")}">
  <a href="tel:{PHONE}">{ICON["phone"]}<span>{T("Call", "Κλήση")}</span></a>
  <a class="primary" href="{MAPS["google"]}" target="_blank" rel="noopener">{ICON["pin"]}<span>{T("Directions", "Οδηγίες")}</span></a>
</nav>
</body>
</html>
'''

def write(path, content):
    f = OUT / (("el/" if LANG == "el" else "") + (path or "index") + ".html")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")

# ------------------------------------------------------------ shared blocks
def map_facade():
    return f'''<div class="map reveal" data-map="{esc(MAPS["embed"] + ("&hl=el" if LANG == "el" else "&hl=en"))}" data-title="{esc(T(f"Map of Yiasemi, {P(A['street'])}, Plaka", f"Χάρτης: Γιασεμί, {P(A['street'])}, Πλάκα"))}">
  <div class="map-facade">
    {ICON["pin"]}
    <p><b>{street_line()}</b></p>
    <button class="btn btn-ghost" type="button" data-load-map>{T("Show interactive map", "Εμφάνιση χάρτη")}</button>
    <p class="fine">{T("Loads Google Maps, which may set cookies and receive your IP address.", "Φορτώνει το Google Maps, το οποίο μπορεί να ορίσει cookies και να λάβει τη διεύθυνση IP σας.")}</p>
  </div>
</div>'''

def directions_buttons(primary=True):
    return f'''<div class="actions">
  <a class="btn {"btn-solid" if primary else "btn-ghost"}" href="{MAPS["google"]}" target="_blank" rel="noopener">{ICON["pin"]}{T("Google Maps directions", "Οδηγίες Google Maps")}</a>
  <a class="btn btn-ghost" href="{MAPS["apple"]}" target="_blank" rel="noopener">{T("Apple Maps", "Apple Maps")}</a>
  <a class="btn btn-ghost" href="tel:{PHONE}">{ICON["phone"]}{T("Call", "Κλήση")} {PHONE_TXT}</a>
</div>'''

def hours_block():
    rows = hours_rows(SITE.get("openingHours"), LANG)
    if not rows:
        return f'<p>{T("Opening hours are not published yet. Please call before you visit.", "Το ωράριο δεν έχει δημοσιευτεί ακόμη. Παρακαλούμε τηλεφωνήστε πριν έρθετε.")}</p>'
    return '<table class="hours"><tbody>' + "".join(f"<tr><th scope=\"row\">{d}</th><td>{h}</td></tr>" for d, h in rows) + "</tbody></table>"

def info_dl():
    return f'''<dl class="info-list">
  <div><dt>{T("Address", "Διεύθυνση")}</dt><dd>{street_line()}</dd></div>
  <div><dt>{T("Phone", "Τηλέφωνο")}</dt><dd><a href="tel:{PHONE}">{PHONE_TXT}</a></dd></div>
  <div><dt>{T("Opening hours", "Ωράριο")}</dt><dd>{hours_block()}</dd></div>
  {f'<div><dt>Instagram</dt><dd><a href="{SITE["instagram"]}" target="_blank" rel="noopener">@yiasemi_bistrot ↗</a></dd></div>' if SITE.get("instagram") else ""}
</dl>'''

def notice_bar():
    n = SITE.get("notice")
    return f'<div class="notice" role="status"><div class="wrap">{esc(P(n))}</div></div>' if n else ""

def section_head(eyebrow, title, hid, extra=""):
    return f'<div class="sec-head"><div><p class="eyebrow reveal">{eyebrow}</p><h2 id="{hid}" class="reveal">{title}</h2></div>{extra}</div>'

# ================================================================ HOME
def home():
    title = T("Yiasemi café bistrot in Plaka, Athens | Mnisikleous Steps",
              "Γιασεμί καφέ μπιστρό στην Πλάκα | Στα σκαλιά της Μνησικλέους")
    desc = T("Yiasemi (Γιασεμί) is a traditional café bistrot half way up the stepped Mnisikleous Street in Plaka, Athens: Greek coffee, homemade pies, desserts, Greek wine and cocktails.",
             "Το Γιασεμί είναι παραδοσιακό καφέ μπιστρό στα μισά της σκαλωτής Μνησικλέους στην Πλάκα: ελληνικός καφές, σπιτικές πίτες, γλυκά, ελληνικό κρασί και cocktails.")
    strip = [("Greek coffee", "Ελληνικός καφές"), ("Spinach pie", "Σπανακόπιτα"), ("Lemon pie", "Λεμονόπιτα"), ("Orange pie", "Πορτοκαλόπιτα"),
             ("Galaktoboureko", "Γαλακτομπούρεκο"), ("Moussaka", "Μουσακάς"), ("Strapatsada", "Στραπατσάδα"), ("Tsipouro", "Τσίπουρο"), ("Granny's Spritz", "Granny's Spritz")]
    strip_html = "".join(f'<li>{T(a, b)}</li>' for a, b in strip)

    day = [("sun", ("Morning", "Πρωί"), ("Breakfast", "Πρωινό"), ("Yiasemi breakfast, strapatsada, yogurt with honey and homemade granola.", "Γιασεμί πρωινό, στραπατσάδα, γιαούρτι με μέλι και σπιτική γκρανόλα.")),
           ("noon", ("Midday", "Μεσημέρι"), ("Pies & plates", "Πίτες & φαγάκια"), ("Spinach pie, cheese pie with kataifi, moussaka, stuffed tomatoes and salads.", "Σπανακόπιτα, τυρόπιτα με καταΐφι, μουσακάς, γεμιστά και σαλάτες.")),
           ("cup", ("Afternoon", "Απόγευμα"), ("Coffee & something sweet", "Καφές & κάτι γλυκό"), ("Greek coffee with a spoon sweet, lemon pie, orange pie, galaktoboureko.", "Ελληνικός καφές με γλυκό του κουταλιού, λεμονόπιτα, πορτοκαλόπιτα, γαλακτομπούρεκο.")),
           ("moon", ("Evening", "Βράδυ"), ("Wine & cocktails", "Κρασί & cocktails"), ("Greek wines, tsipouro and the house Yiasemi cocktails.", "Ελληνικά κρασιά, τσίπουρο και τα cocktails του Γιασεμιού."))]
    day_html = "".join(f'<li class="step reveal">{ICON[k]}<span class="time">{T(*a)}</span><h3>{T(*b)}</h3><p>{T(*c)}</p></li>' for k, a, b, c in day)

    sigs = [("sig-coffee", "c-clay", ("The classic", "Το κλασικό"), ("Greek coffee", "Ελληνικός καφές"), ("Single or double, served with a spoon sweet.", "Μονός ή διπλός, σερβίρεται με γλυκό του κουταλιού."), "coffee"),
            ("sig-sweet", "c-olive", ("Homemade desserts", "Σπιτικά γλυκά"), ("Lemon pie & orange pie", "Λεμονόπιτα & πορτοκαλόπιτα"), ("Two of the homemade desserts guests come back for.", "Δύο από τα σπιτικά γλυκά για τα οποία επιστρέφουν οι επισκέπτες."), "desserts"),
            ("sig-pie", "c-sea", ("Made in our kitchen", "Από την κουζίνα μας"), ("Homemade pies", "Σπιτικές πίτες"), ("Spinach pie, and cheese pie with yellow cheeses and kataifi.", "Σπανακόπιτα και τυρόπιτα με κίτρινα τυριά και καταΐφι."), "pies")]
    sigs_html = "".join(
        f'<li class="sig reveal"><a class="sig-link" href="{url("menu")}#{anchor}">{pic(pid, "arch", col, "(max-width: 760px) 92vw, 360px", cap=T("Illustrative photo", "Ενδεικτική φωτογραφία"))}'
        f'<span class="tag">{T(*tag)}</span><h3>{T(*h)}</h3><p>{T(*p)}</p></a></li>' for pid, col, tag, h, p, anchor in sigs)

    def cup(gr, say, en, el, n):
        sugar = "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(3))
        return f'<li class="cup reveal"><span class="gr" lang="el">{gr}</span><span class="say">{say}</span><p>{T(en, el)}</p><div class="sugar" aria-hidden="true">{sugar}</div></li>'
    cups = (cup("Σκέτος", "[ské-tos]", "No sugar. Strong and bitter.", "Χωρίς ζάχαρη. Δυνατός και πικρός.", 0)
          + cup("Μέτριος", "[mé-tri-os]", "Medium sweet, with one teaspoon of sugar.", "Μέτριος, με ένα κουταλάκι ζάχαρη.", 1)
          + cup("Γλυκός", "[gli-kós]", "Sweet, with two teaspoons of sugar.", "Γλυκός, με δύο κουταλάκια ζάχαρη.", 2))

    feats = [("bread", ("Homemade, every morning", "Σπιτικά, κάθε πρωί"), ("Pies, desserts and bread are made on site each morning, with pure virgin olive oil.", "Πίτες, γλυκά και ψωμί φτιάχνονται κάθε πρωί στον χώρο μας, με αγνό παρθένο ελαιόλαδο.")),
             ("leaf", ("Vegetarian & vegan friendly", "Για χορτοφάγους & vegan"), ("Most of the menu is vegetarian, with clearly marked vegan dishes.", "Το μεγαλύτερο μέρος του μενού είναι χορτοφαγικό, με σημειωμένα vegan πιάτα.")),
             ("coffee", ("Greek coffee, done properly", "Ελληνικός καφές, όπως πρέπει"), ("Brewed in a briki and served with a spoon sweet.", "Ψημένος στο μπρίκι και σερβιρισμένος με γλυκό του κουταλιού."))]
    feats_html = "".join(f'<li class="feature reveal"><span class="feature-ic">{ICON[ic]}</span><h3>{T(*h)}</h3><p>{T(*p)}</p></li>' for ic, h, p in feats)

    faqs = home_faqs()
    faq_html = "".join(f'<details class="faq"><summary><h3>{q}</h3></summary><p>{a}</p></details>' for q, a in faqs)
    ld = [website_ld(), cafe_ld(), webpage_ld("", title, desc), crumbs_ld([(T("Home", "Αρχική"), abs_url(""))]),
          {"@type": "FAQPage", "@id": abs_url("") + "#faq", "inLanguage": LANG,
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}]

    body = f'''{notice_bar()}
<section class="hero" aria-labelledby="hero-h">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="greeting">{jasmine()}<span data-greeting>{T("Welcome to Yiasemi.", "Καλώς ήρθατε στο Γιασεμί.")}</span></p>
      <h1 id="hero-h">{T('A traditional café bistrot on the <span class="soft">steps</span> of Plaka.', 'Παραδοσιακό καφέ μπιστρό στα <span class="soft">σκαλιά</span> της Πλάκας.')}</h1>
      <p class="lead">{T("Coffee, drinks, homemade pies and desserts, half way up Mnisikleous Street below the Acropolis.", "Καφές, ποτά, σπιτικές πίτες και γλυκά, στα μισά της οδού Μνησικλέους, κάτω από την Ακρόπολη.")}</p>
      <div class="actions">
        <a class="btn btn-solid" href="{url("menu")}">{T("See the menu", "Δείτε το μενού")} {ARROW}</a>
        <a class="btn btn-ghost" href="{url("visit")}">{T("Plan your visit", "Οργανώστε την επίσκεψή σας")}</a>
      </div>
      <ul class="facts" aria-label="{T("At a glance", "Με μια ματιά")}">
        <li class="chip">{ICON["pin"]}{P(A["street"])}, {P(A["area"])}</li>
        <li class="chip">{ICON["leaf"]}{T("Vegetarian & vegan options", "Χορτοφαγικές & vegan επιλογές")}</li>
        <li class="chip">{ICON["bread"]}{T("Everything homemade", "Όλα σπιτικά")}</li>
      </ul>
    </div>
    <div class="hero-photo">
      {pic("hero", "arch", "c-olive", "(max-width: 960px) 92vw, 440px", eager=True, cap=T("Mnisikleous Street, Plaka", "Οδός Μνησικλέους, Πλάκα"))}
      <div class="badge" aria-hidden="true">{jasmine("core")}</div>
    </div>
  </div>
  <div class="wrap"><ul class="strip" aria-label="{T("From the menu", "Από το μενού")}">{strip_html}</ul></div>
</section>

<section class="wrap section" aria-labelledby="about-h">
  <div class="about">
    {pic("about", "reveal", "c-clay", "(max-width: 960px) 92vw, 500px", cap=T("A lane in Plaka", "Στενό στην Πλάκα"))}
    <div class="reveal">
      <p class="eyebrow">{T("Our place", "Ο χώρος μας")}</p>
      <h2 id="about-h">{T("Named after jasmine.", "Πήρε το όνομά του από το γιασεμί.")}</h2>
      <blockquote class="owner-quote">
        <p>{T("“My café is here, half way up. Its name is Yiasemi, jasmine, the sweet-smelling flower whose white blossom shines even at midnight.”",
              "«Το καφέ μου είναι εδώ, στα μισά της ανηφόρας. Λέγεται Γιασεμί, όπως το ευωδιαστό λουλούδι που τα λευκά του άνθη λάμπουν ακόμη και τα μεσάνυχτα.»")}</p>
        <footer>{T("Mariza Kouzeli, owner, from", "Μαρίζα Κουζέλη, ιδιοκτήτρια, από το")} <a href="https://www.yiasemi.gr/our-vision" target="_blank" rel="noopener">yiasemi.gr</a></footer>
      </blockquote>
      <p class="muted">{T("Mnisikleous is the street of central steps that climbs from Plaka toward the Acropolis, named after the ancient architect Mnesikles. The recipes come from the plants and flavours of the Aegean islands, taught by a grandmother from the archipelago.",
                       "Η Μνησικλέους είναι ο δρόμος με τα κεντρικά σκαλιά που ανεβαίνει από την Πλάκα προς την Ακρόπολη, με το όνομα του αρχαίου αρχιτέκτονα Μνησικλή. Οι συνταγές έρχονται από τα φυτά και τις γεύσεις των νησιών του Αιγαίου, όπως τις δίδαξε μια γιαγιά από το αρχιπέλαγος.")}</p>
    </div>
  </div>
</section>

<section class="wrap section" aria-labelledby="feat-h">
  {section_head(T("Why people come", "Γιατί έρχονται"), T("Simple, homemade, Greek.", "Απλά, σπιτικά, ελληνικά."), "feat-h")}
  <ul class="features">{feats_html}</ul>
</section>

<section class="wrap section" aria-labelledby="day-h">
  {section_head(T("A day at Yiasemi", "Μια μέρα στο Γιασεμί"), T("From breakfast<br>to a glass of wine.", "Από το πρωινό<br>ως ένα ποτήρι κρασί."), "day-h")}
  <ol class="steps">{day_html}</ol>
</section>

<section class="wrap section" aria-labelledby="sig-h">
  {section_head(T("From the menu", "Από το μενού"), T("Guest favourites.", "Τα αγαπημένα."), "sig-h", f'<a class="btn btn-ghost reveal" href="{url("menu")}">{T("Full menu & prices", "Μενού & τιμές")} {ARROW}</a>')}
  <ul class="sigs">{sigs_html}</ul>
</section>

<section class="wrap section" id="greek-coffee" aria-labelledby="gc-h">
  <div class="guide">
    <p class="eyebrow">{T("A small guide", "Ένας μικρός οδηγός")}</p>
    <h2 id="gc-h">{T("How to order Greek coffee.", "Πώς παραγγέλνεις ελληνικό καφέ.")}</h2>
    <p class="lead">{T("The sugar goes into the briki while it brews, so you choose before it is made.", "Η ζάχαρη μπαίνει στο μπρίκι πριν ψηθεί, γι' αυτό τη διαλέγεις από πριν.")}</p>
    <ul class="cups">{cups}</ul>
    <p class="tip">{T("<b>Tip:</b> let the grounds settle for a minute and leave the last sip in the cup.", "<b>Συμβουλή:</b> αφήστε το κατακάθι να κατακαθίσει για ένα λεπτό και αφήστε την τελευταία γουλιά στο φλιτζάνι.")}</p>
  </div>
</section>

<section class="quote wrap" aria-label="{T("Press", "Τύπος")}">
  <figure>
    {jasmine("mark")}
    <blockquote><p>{T("“Athens' best café for people watching.”", "«Το καλύτερο καφέ της Αθήνας για να χαζεύεις τον κόσμο.»")}</p></blockquote>
    <figcaption>{T("Headline,", "Τίτλος άρθρου,")} <a href="https://greekcitytimes.com/2022/04/16/yiasemi-athens-for-people-watching" target="_blank" rel="noopener">Greek City Times</a>{T(", 2022", ", 2022")}</figcaption>
  </figure>
</section>

<section class="wrap section" id="faq" aria-labelledby="faq-h">
  {section_head(T("Good to know", "Χρήσιμα"), T("Questions guests ask.", "Ερωτήσεις των επισκεπτών."), "faq-h")}
  <div class="faqs">{faq_html}</div>
</section>

<section class="wrap section-tight" aria-labelledby="cta-h">
  <div class="cta-band">
    <div>
      <h2 id="cta-h">{T("Find us half way up the steps.", "Θα μας βρείτε στα μισά των σκαλιών.")}</h2>
      <p>{street_line()}</p>
    </div>
    <div class="actions">
      <a class="btn btn-solid" href="{MAPS["google"]}" target="_blank" rel="noopener">{T("Get directions", "Οδηγίες")} {ARROW}</a>
      <a class="btn btn-ghost" href="tel:{PHONE}">{T("Call", "Κλήση")} {PHONE_TXT}</a>
    </div>
  </div>
</section>
'''
    write("", head("", title, desc, ld) + body + foot())

def home_faqs():
    return [
      (T("Where is Yiasemi?", "Πού βρίσκεται το Γιασεμί;"),
       T(f"At {street_line()}, half way up the stepped Mnisikleous Street that climbs from Plaka toward the Acropolis.",
         f"Στη διεύθυνση {street_line()}, στα μισά της σκαλωτής οδού Μνησικλέους που ανεβαίνει από την Πλάκα προς την Ακρόπολη.")),
      (T("What is the nearest metro station?", "Ποιος είναι ο πλησιέστερος σταθμός μετρό;"),
       T("Monastiraki (lines 1 and 3) is the closest station; from there it is a short walk through Plaka.",
         "Ο πλησιέστερος σταθμός είναι το Μοναστηράκι (γραμμές 1 και 3)· από εκεί είναι μια σύντομη βόλτα μέσα από την Πλάκα.")),
      (T("Are there vegetarian and vegan options?", "Υπάρχουν χορτοφαγικές και vegan επιλογές;"),
       T("Yes. Most of the food menu is vegetarian and several dishes are vegan; they are marked on the menu.",
         "Ναι. Το μεγαλύτερο μέρος του μενού είναι χορτοφαγικό και αρκετά πιάτα είναι vegan· σημειώνονται στο μενού.")),
      (T("I have a food allergy. What should I do?", "Έχω τροφική αλλεργία. Τι να κάνω;"),
       T("Please tell the staff before you order. They can explain the ingredients of each dish.",
         "Ενημερώστε το προσωπικό πριν παραγγείλετε. Θα σας εξηγήσουν τα συστατικά κάθε πιάτου.")),
      (T("Is the café step-free?", "Υπάρχει πρόσβαση χωρίς σκαλιά;"),
       T("No. Mnisikleous is a stepped street and the café is half way up, so the approach involves stairs.",
         "Όχι. Η Μνησικλέους είναι σκαλωτός δρόμος και το καφέ βρίσκεται στα μισά της, οπότε η πρόσβαση γίνεται από σκαλιά.")),
      (T("What are the opening hours?", "Ποιο είναι το ωράριο;"),
       T(f"Hours are not published on this site yet. Please call {PHONE_TXT} before you come.",
         f"Το ωράριο δεν έχει δημοσιευτεί ακόμη. Τηλεφωνήστε στο {PHONE_TXT} πριν έρθετε.") if not SITE.get("openingHours")
       else T("See the Visit page for this week's opening hours.", "Δείτε το ωράριο στη σελίδα Επίσκεψη.")),
    ]

# ================================================================ MENU
def price_html(it):
    if "prices" in it:
        return '<span class="price">' + " · ".join(f'<span class="p-label">{P(p["label"])}</span> {fmt_price(p["price"], LANG)}' for p in it["prices"]) + "</span>"
    return f'<span class="price">{fmt_price(it["price"], LANG)}</span>'

def diet_badge(it):
    out = ""
    d = it.get("diet")
    if d:
        out += f'<span class="diet diet-{d}" title="{DIETS[d][LANG]}"><span aria-hidden="true">{DIETS[d]["short"]}</span><span class="sr-only">{DIETS[d][LANG]}</span></span>'
    if it.get("veganOption"):
        out += f'<span class="diet diet-option">{T("vegan option", "vegan επιλογή")}</span>'
    return out

KIND = {"white": ("White", "Λευκά"), "rose": ("Rosé", "Ροζέ"), "red": ("Red", "Κόκκινα"), "sparkling": ("Sparkling & Champagne", "Αφρώδη & σαμπάνια")}
GROUPS = {"food": ("Food", "Φαγητό"), "drinks": ("Coffee & drinks", "Καφές & ροφήματα"), "bar": ("Bar", "Μπαρ")}

def menu_item(it):
    diet = it.get("diet") or ""
    vopt = " vegan-option" if it.get("veganOption") else ""
    desc = f'<p class="mi-desc">{esc(P(it["desc"]))}</p>' if it.get("desc") else ""
    multi = " mi-multi" if "prices" in it else ""
    return (f'<li class="mi{multi}" data-diet="{diet}{vopt}" id="item-{it["id"]}"><div class="mi-row">'
            f'<h3 class="mi-name">{esc(P(it["name"]))}</h3>{diet_badge(it)}<span class="dots" aria-hidden="true"></span>{price_html(it)}</div>{desc}</li>')

def menu():
    validate_menu(MENU)
    title = T("Menu & prices | Yiasemi café bistrot, Plaka Athens",
              "Μενού & τιμές | Γιασεμί καφέ μπιστρό, Πλάκα")
    desc = T("Yiasemi's full menu with prices: breakfast, homemade pies and tarts, salads, moussaka, desserts like lemon pie and orange pie, Greek coffee, fresh juices, Greek wine, tsipouro and cocktails.",
             "Το πλήρες μενού του Γιασεμιού με τιμές: πρωινό, σπιτικές πίτες και τάρτες, σαλάτες, μουσακάς, γλυκά όπως λεμονόπιτα και πορτοκαλόπιτα, ελληνικός καφές, φυσικοί χυμοί, ελληνικό κρασί, τσίπουρο και cocktails.")
    secs = MENU["sections"]
    chips = "".join(f'<li><a href="#{s["id"]}" data-spy="{s["id"]}">{esc(P(s["name"]))}</a></li>' for s in secs)
    body_secs, cur_group = "", None
    for s in secs:
        if s["group"] != cur_group:
            if cur_group: body_secs += "</div>"
            cur_group = s["group"]
            body_secs += f'<div class="menu-group-block"><p class="group-label">{T(*GROUPS[cur_group])}</p>'
        meta = ""
        if s.get("served"): meta += f'<p class="served">{esc(P(s["served"]))}</p>'
        if s["id"] == "wine":
            lists = ""
            for kind in ("white", "rose", "red", "sparkling"):
                its = [i for i in s["items"] if i.get("kind") == kind]
                if its: lists += f'<h3 class="kind">{T(*KIND[kind])}</h3><ul class="mi-list">{"".join(menu_item(i) for i in its)}</ul>'
        else:
            lists = f'<ul class="mi-list">{"".join(menu_item(i) for i in s["items"])}</ul>'
        foot_ = f'<p class="footnote">{esc(P(s["footnote"]))}</p>' if s.get("footnote") else ""
        body_secs += f'<section class="menu-sec" id="{s["id"]}" aria-labelledby="h-{s["id"]}"><div class="menu-sec-head"><h2 id="h-{s["id"]}">{esc(P(s["name"]))}</h2>{meta}</div>{lists}{foot_}</section>'
    body_secs += "</div>"
    n = MENU["notes"]
    notes = "".join(f"<li>{esc(P(n[k]))}</li>" for k in ("homemade", "allergies", "oil", "beef", "dishesOfDay"))
    legal = "".join(f"<li>{esc(P(n[k]))}</li>" for k in ("receipt", "alcohol", "complaints"))
    sup = SITE.get("foodSafetySupervisor")
    legal += f'<li>{T("Market supervisor", "Αγορανομικός υπεύθυνος")}: {esc(P(sup))}</li>' if sup else ""

    def offer(it):
        if "prices" in it:
            return [{"@type": "Offer", "price": f'{p["price"]:.2f}', "priceCurrency": "EUR", "name": p["label"]["en"]} for p in it["prices"]]
        return {"@type": "Offer", "price": f'{it["price"]:.2f}', "priceCurrency": "EUR"}
    menu_ld = {"@type": "Menu", "@id": abs_url("menu") + "#menu", "name": T("Yiasemi menu", "Μενού Γιασεμί"), "inLanguage": LANG,
               "hasMenuSection": [{"@type": "MenuSection", "name": P(s["name"]),
                   "hasMenuItem": [dict({"@type": "MenuItem", "name": P(i["name"]), "offers": offer(i)},
                                        **({"description": P(i["desc"])} if i.get("desc") else {}),
                                        **({"suitableForDiet": "https://schema.org/" + ("VeganDiet" if i["diet"] == "vegan" else "VegetarianDiet")} if i.get("diet") else {}))
                                   for i in s["items"]]} for s in secs]}
    ld = [website_ld(), {**cafe_ld(), "hasMenu": {"@id": abs_url("menu") + "#menu"}}, menu_ld, webpage_ld("menu", title, desc, img=img_abs("sig-sweet")),
          crumbs_ld([(T("Home", "Αρχική"), abs_url("")), (T("Menu", "Μενού"), abs_url("menu"))])]
    body = f'''{notice_bar()}
<section class="wrap page-head">
  <p class="eyebrow">{T("Menu", "Μενού")}</p>
  <h1>{T("Coffee, pies, desserts<br>&amp; Greek wine.", "Καφές, πίτες, γλυκά<br>&amp; ελληνικό κρασί.")}</h1>
  <p class="lead">{T("Everything is homemade. Prices in euro, including VAT.", "Όλα είναι σπιτικά. Τιμές σε ευρώ, με ΦΠΑ.")}</p>
</section>
<div class="wrap">
    <div class="menu-tools" role="search">
      <label class="search"><span class="sr-only">{T("Search the menu", "Αναζήτηση στο μενού")}</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg>
        <input type="search" id="menu-search" placeholder="{T("Search dishes & drinks", "Αναζήτηση πιάτων & ποτών")}" autocomplete="off" enterkeyhint="search">
      </label>
      <div class="diet-filter" role="group" aria-label="{T("Dietary filter", "Φίλτρο διατροφής")}">
        <button type="button" data-diet-filter="all" aria-pressed="true">{T("All", "Όλα")}</button>
        <button type="button" data-diet-filter="vegetarian" aria-pressed="false">{T("Vegetarian", "Χορτοφαγικά")}</button>
        <button type="button" data-diet-filter="vegan" aria-pressed="false">Vegan</button>
      </div>
    </div>
</div>
<div class="menu-bar" id="menu-bar">
  <div class="wrap menu-bar-inner">
    <nav class="cat-nav" aria-label="{T("Menu sections", "Κατηγορίες μενού")}"><ul>{chips}</ul></nav>
  </div>
</div>
<section class="wrap menu-wrap" id="menu" aria-label="{T("Menu items", "Είδη μενού")}">
  <p class="menu-legend"><span class="diet diet-vegetarian" aria-hidden="true">V</span> {T("Vegetarian", "Χορτοφαγικό")} <span class="diet diet-vegan" aria-hidden="true">VG</span> Vegan</p>
  <p class="menu-empty" id="menu-empty" hidden>{T("Nothing matches your search.", "Δεν βρέθηκε κάτι.")} <button type="button" class="link-btn" data-clear-search>{T("Clear search", "Καθαρισμός")}</button></p>
  <p class="sr-only" aria-live="polite" id="menu-count"></p>
  {body_secs}
  <div class="menu-notes">
    <h2 class="notes-h">{T("Good to know", "Χρήσιμες πληροφορίες")}</h2>
    <ul>{notes}</ul>
    <ul class="legal">{legal}</ul>
  </div>
</section>
'''
    write("menu", head("menu", title, desc, ld, og_img=img_abs("sig-sweet", 1200) if "sig-sweet" in PHOTOS else None) + body + foot())

# ================================================================ PHOTOS
CATS = {"street": ("The street", "Ο δρόμος"), "evening": ("Evening", "Βράδυ"), "taste": ("Coffee & food", "Καφές & φαγητό"), "plaka": ("Around Plaka", "Γύρω από την Πλάκα")}

def photos():
    title = T("Photos of Mnisikleous Street & Plaka | Yiasemi, Athens", "Φωτογραφίες: Μνησικλέους & Πλάκα | Γιασεμί, Αθήνα")
    desc = T("Photos of Yiasemi's neighbourhood: the steps of Mnisikleous Street, Plaka at night, Greek coffee, pies and desserts.",
             "Φωτογραφίες από τη γειτονιά του Γιασεμιού: τα σκαλιά της Μνησικλέους, η Πλάκα τη νύχτα, ελληνικός καφές, πίτες και γλυκά.")
    ids = [k for k, v in PHOTOS.items() if v.get("cat")]
    items, objs = "", []
    for n, k in enumerate(ids):
        p = PHOTOS[k]
        cap = f'{esc(p["alt"][LANG])}<small>{credit(k)}</small>'
        items += (f'<li class="g-item" data-cat="{p["cat"]}">'
                  f'<button type="button" class="g-open"><span class="sr-only">{T("Open photo", "Άνοιγμα φωτογραφίας")}: </span>'
                  f'{pic(k, "", "c-stone", "(max-width: 760px) 46vw, (max-width: 1100px) 30vw, 380px", eager=("high" if n == 0 else n < 3), cap=cap, full=True, alt_in_caption=True)}</button></li>')
        objs.append({"@type": "ImageObject", "contentUrl": img_abs(k), "name": p["alt"][LANG], "width": p["w"], "height": p["h"],
                     "creator": {"@type": "Person", "name": p["author"]}, "creditText": p["author"],
                     "license": p["licurl"], "acquireLicensePage": p["source"], "copyrightNotice": f'{p["author"]}, {p["license"]}'})
    fbtn = f'<button type="button" data-filter="all" aria-pressed="true">{T("All", "Όλες")}</button>' + "".join(
        f'<button type="button" data-filter="{k}" aria-pressed="false">{T(*v)}</button>' for k, v in CATS.items() if any(PHOTOS[g]["cat"] == k for g in ids))
    ld = [website_ld(), cafe_ld(),
          {**webpage_ld("photos", title, desc, kind="CollectionPage"), "mainEntity": {"@type": "ImageGallery", "name": T("Photos", "Φωτογραφίες"), "associatedMedia": objs}},
          crumbs_ld([(T("Home", "Αρχική"), abs_url("")), (T("Photos", "Φωτογραφίες"), abs_url("photos"))])]
    body = f'''{notice_bar()}
<section class="wrap page-head">
  <p class="eyebrow">{T("Gallery", "Γκαλερί")}</p>
  <h1>{T("More photos", "Περισσότερες φωτογραφίες")}</h1>
  <p class="lead">{T("Yiasemi's corner of Athens: the steps of Mnisikleous, Plaka after dark, and the Greek coffee and homemade sweets it is known for.", "Η γωνιά του Γιασεμιού στην Αθήνα: τα σκαλιά της Μνησικλέους, η Πλάκα τη νύχτα, ο ελληνικός καφές και τα σπιτικά γλυκά.")}</p>
  <p class="fine">{T("These are openly licensed photos of the street and of Greek dishes, not photos taken inside Yiasemi.", "Πρόκειται για φωτογραφίες ελεύθερης άδειας του δρόμου και ελληνικών πιάτων, όχι φωτογραφίες από το εσωτερικό του Γιασεμιού.")}</p>
</section>
<section class="wrap" aria-label="{T("Photo gallery", "Γκαλερί φωτογραφιών")}">
  <div class="filters" role="group" aria-label="{T("Filter photos", "Φίλτρο φωτογραφιών")}">{fbtn}</div>
  <p class="sr-only" aria-live="polite" id="gallery-count"></p>
  <ul class="gallery">{items}</ul>
  <p class="fine"><a href="{url("credits")}">{T("Photo credits and licences", "Πηγές και άδειες φωτογραφιών")}</a></p>
</section>
<div class="lightbox" role="dialog" aria-modal="true" aria-label="{T("Photo viewer", "Προβολή φωτογραφίας")}" hidden>
  <figure class="lb-figure"><div class="lb-stage"><span class="lb-spinner" aria-hidden="true"></span><img alt=""></div><figcaption class="lb-cap"></figcaption></figure>
  <p class="lb-count" aria-live="polite"></p>
  <button class="lb-btn lb-close" type="button" aria-label="{T("Close", "Κλείσιμο")}">&times;</button>
  <button class="lb-btn lb-prev" type="button" aria-label="{T("Previous photo", "Προηγούμενη")}">←</button>
  <button class="lb-btn lb-next" type="button" aria-label="{T("Next photo", "Επόμενη")}">→</button>
</div>
'''
    write("photos", head("photos", title, desc, ld) + body + foot())

# ================================================================ VISIT
def visit():
    title = T(f"Visit Yiasemi | {A['street']['en']}, Plaka, Athens: directions & metro",
              f"Επίσκεψη στο Γιασεμί | {A['street']['el']}, Πλάκα: οδηγίες & μετρό")
    desc = T(f"How to find Yiasemi at {A['street']['en']}, Plaka, Athens: address, phone, Google and Apple Maps directions, nearest metro and what to expect on the stepped street.",
             f"Πώς θα βρείτε το Γιασεμί στη {A['street']['el']} στην Πλάκα: διεύθυνση, τηλέφωνο, οδηγίες Google και Apple Maps, πλησιέστερο μετρό και τι να περιμένετε στον σκαλωτό δρόμο.")
    metro = [(("Monastiraki", "Μοναστηράκι"), ("Lines 1 & 3 · closest station", "Γραμμές 1 & 3 · πλησιέστερος σταθμός")),
             (("Syntagma", "Σύνταγμα"), ("Lines 2 & 3", "Γραμμές 2 & 3")),
             (("Akropoli", "Ακρόπολη"), ("Line 2", "Γραμμή 2"))]
    near = [("Roman Agora", "Ρωμαϊκή Αγορά"), ("Tower of the Winds", "Αέρηδες"), ("Anafiotika", "Αναφιώτικα"), ("Acropolis", "Ακρόπολη"), ("Monastiraki Square", "Πλατεία Μοναστηρακίου")]
    mlis = "".join(f'<li><span>{T(*a)}</span><small>{T(*b)}</small></li>' for a, b in metro)
    nlis = "".join(f'<li><span>{T(*a)}</span></li>' for a in near)
    ld = [website_ld(), cafe_ld(), webpage_ld("visit", title, desc, kind="ContactPage"),
          crumbs_ld([(T("Home", "Αρχική"), abs_url("")), (T("Visit", "Επίσκεψη"), abs_url("visit"))])]
    body = f'''{notice_bar()}
<section class="wrap page-head">
  <p class="eyebrow">{T("Visit", "Επίσκεψη")}</p>
  <h1>{T("Half way up<br>the steps of Mnisikleous.", "Στα μισά των σκαλιών<br>της Μνησικλέους.")}</h1>
  <p class="lead">{T("In the heart of Plaka, on the stepped street that climbs toward the Acropolis.", "Στην καρδιά της Πλάκας, στον σκαλωτό δρόμο που ανεβαίνει προς την Ακρόπολη.")}</p>
</section>
<section class="wrap" aria-labelledby="where-h">
  <div class="location">
    <div class="info">
      <h2 id="where-h" class="sr-only">{T("Address and contact", "Διεύθυνση και επικοινωνία")}</h2>
      {info_dl()}
      {directions_buttons()}
    </div>
    {map_facade()}
  </div>
</section>
<section class="wrap section" aria-labelledby="getting-h">
  <div class="meander" aria-hidden="true"></div>
  <div class="cols">
    <div>
      <p class="eyebrow">{T("By metro", "Με το μετρό")}</p>
      <h2 id="getting-h">{T("Getting here", "Πώς θα έρθετε")}</h2>
      <ul class="walk">{mlis}</ul>
      <p class="fine">{T("From any of these stations, continue on foot through Plaka; Mnisikleous is a pedestrian street.", "Από όποιον σταθμό, συνεχίστε με τα πόδια μέσα από την Πλάκα· η Μνησικλέους είναι πεζόδρομος.")}</p>
    </div>
    <div>
      <p class="eyebrow">{T("Nearby", "Κοντά μας")}</p>
      <h2>{T("Around the café", "Γύρω από το καφέ")}</h2>
      <ul class="walk">{nlis}</ul>
    </div>
  </div>
  <div class="access">
    <h2>{T("Access", "Πρόσβαση")}</h2>
    <p>{T("Mnisikleous is a stepped, pedestrian street and the café is half way up, so the approach involves stairs and is not step-free. Cars cannot reach the door.", "Η Μνησικλέους είναι σκαλωτός πεζόδρομος και το καφέ βρίσκεται στα μισά της, επομένως η πρόσβαση γίνεται από σκαλιά. Τα αυτοκίνητα δεν φτάνουν ως την πόρτα.")}</p>
  </div>
</section>
'''
    write("visit", head("visit", title, desc, ld) + body + foot())

# ================================================================ PRIVACY
def privacy():
    title = T("Privacy & cookies | Yiasemi", "Απόρρητο & cookies | Γιασεμί")
    desc = T("How the Yiasemi website handles your data: no analytics, no tracking cookies.", "Πώς ο ιστότοπος του Γιασεμιού χειρίζεται τα δεδομένα σας: χωρίς analytics, χωρίς cookies παρακολούθησης.")
    ld = [website_ld(), webpage_ld("privacy", title, desc), crumbs_ld([(T("Home", "Αρχική"), abs_url("")), (T("Privacy", "Απόρρητο"), abs_url("privacy"))])]
    body = f'''
<section class="wrap page-head narrow">
  <p class="eyebrow">{T("Privacy", "Απόρρητο")}</p>
  <h1>{T("Privacy & cookies", "Απόρρητο & cookies")}</h1>
  <p class="lead">{T("This website does not use analytics, advertising or tracking cookies, and it does not ask for any personal information.", "Αυτός ο ιστότοπος δεν χρησιμοποιεί analytics, διαφημίσεις ή cookies παρακολούθησης και δεν ζητά προσωπικά στοιχεία.")}</p>
</section>
<section class="wrap narrow prose">
  <h2>{T("What is stored on your device", "Τι αποθηκεύεται στη συσκευή σας")}</h2>
  <p>{T("Only your colour-theme choice (light or dark), in your browser's local storage, and only after you press the theme button. It never leaves your device. Clear it at any time from your browser settings.", "Μόνο η επιλογή θέματος (φωτεινό ή σκοτεινό), στον τοπικό χώρο αποθήκευσης του προγράμματος περιήγησης, και μόνο αφού πατήσετε το κουμπί θέματος. Δεν φεύγει ποτέ από τη συσκευή σας.")}</p>
  <h2>{T("Hosting", "Φιλοξενία")}</h2>
  <p>{T("The site is hosted by Vercel Inc. Like any web server, it processes technical data such as your IP address to deliver the pages and protect against abuse. Fonts and images are served from this site; your browser does not contact Google or other third parties when pages load.", "Ο ιστότοπος φιλοξενείται από τη Vercel Inc. Όπως κάθε διακομιστής, επεξεργάζεται τεχνικά δεδομένα όπως τη διεύθυνση IP για να παραδώσει τις σελίδες και να προστατευθεί από κατάχρηση. Οι γραμματοσειρές και οι εικόνες σερβίρονται από τον ίδιο τον ιστότοπο.")}</p>
  <h2>{T("Maps and external links", "Χάρτες και εξωτερικοί σύνδεσμοι")}</h2>
  <p>{T("The map is only loaded if you press “Show interactive map”. Google Maps may then set cookies and receive your IP address under Google's own privacy policy. Links to Google Maps, Apple Maps and Instagram open those services, which apply their own policies.", "Ο χάρτης φορτώνεται μόνο αν πατήσετε «Εμφάνιση χάρτη». Τότε το Google Maps μπορεί να ορίσει cookies και να λάβει τη διεύθυνση IP σας σύμφωνα με τη δική του πολιτική. Οι σύνδεσμοι προς Google Maps, Apple Maps και Instagram ανοίγουν αυτές τις υπηρεσίες.")}</p>
  <h2>{T("Contact", "Επικοινωνία")}</h2>
  <p>{T("Questions about this notice:", "Ερωτήσεις για αυτή τη δήλωση:")} Yiasemi, {street_line()}, <a href="tel:{PHONE}">{PHONE_TXT}</a>.</p>
</section>
'''
    write("privacy", head("privacy", title, desc, ld) + body + foot())

# ================================================================ CREDITS
def credits():
    title = T("Photo credits | Yiasemi", "Πηγές φωτογραφιών | Γιασεμί")
    desc = T("Credits and licences for the photographs on the Yiasemi website.", "Πηγές και άδειες των φωτογραφιών του ιστότοπου.")
    lis = "".join(
        f'<li><img src="/images/{p["base"]}-{p["widths"][0]}.jpg" alt="" loading="lazy" width="96" height="72">'
        f'<div><b>{esc(p["alt"][LANG])}</b><br><span class="muted">{T("Photo", "Φωτογραφία")}: {esc(p["author"])} · '
        f'<a href="{esc(p["licurl"])}" target="_blank" rel="noopener license">{esc(p["license"])}</a> · '
        f'<a href="{esc(p["source"])}" target="_blank" rel="noopener">Wikimedia Commons</a> · {T("resized and cropped", "αλλαγή μεγέθους και περικοπή")}</span></div></li>'
        for p in PHOTOS.values())
    ld = [website_ld(), webpage_ld("credits", title, desc), crumbs_ld([(T("Home", "Αρχική"), abs_url("")), (T("Photo credits", "Πηγές φωτογραφιών"), abs_url("credits"))])]
    body = f'''
<section class="wrap page-head narrow">
  <p class="eyebrow">{T("Thank you", "Ευχαριστούμε")}</p>
  <h1>{T("Photo credits", "Πηγές φωτογραφιών")}</h1>
  <p class="lead">{T("These photographs come from Wikimedia Commons and are used under their Creative Commons licences. Our resized and cropped versions are shared under the same licences.", "Οι φωτογραφίες προέρχονται από το Wikimedia Commons και χρησιμοποιούνται σύμφωνα με τις άδειες Creative Commons. Οι εκδόσεις μας διατίθενται με τις ίδιες άδειες.")}</p>
</section>
<section class="wrap narrow"><ul class="credits">{lis}</ul></section>
'''
    write("credits", head("credits", title, desc, ld, noindex=True) + body + foot())

# ================================================================ 404
def notfound():
    global LANG
    LANG = "en"
    body = f'''
<section class="wrap page-head nf">
  {jasmine("nf-mark")}
  <h1>Lost on the steps?</h1>
  <p class="lead" lang="el">Χαθήκατε στα σκαλιά; Αυτή η σελίδα δεν υπάρχει.</p>
  <p class="lead">This page doesn't exist.</p>
  <div class="actions"><a class="btn btn-solid" href="/">Home {ARROW}</a><a class="btn btn-ghost" href="/menu">Menu</a><a class="btn btn-ghost" href="/el" lang="el">Αρχική</a></div>
</section>
'''
    (OUT / "404.html").write_text(head("404", "Page not found | Yiasemi", "This page could not be found.", [website_ld()], noindex=True) + body + foot(), encoding="utf-8")

# ================================================================ sitemap, robots, manifest, headers
PAGES = [("", "1.0"), ("menu", "0.9"), ("visit", "0.9"), ("photos", "0.6"), ("privacy", "0.2")]

def sitemap():
    rows = []
    for path, pri in PAGES:
        for lang in ("en", "el"):
            alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{abs_url(path, l)}"/>' for h, l in (("en", "en"), ("el", "el"), ("x-default", "en")))
            imgs = ""
            if path == "photos":
                imgs = "".join(f'\n    <image:image><image:loc>{img_abs(k)}</image:loc></image:image>' for k, v in PHOTOS.items() if v.get("cat"))
            elif path == "" and "hero" in PHOTOS:
                imgs = f'\n    <image:image><image:loc>{img_abs("hero")}</image:loc></image:image>'
            rows.append(f'  <url>\n    <loc>{abs_url(path, lang)}</loc>\n    <priority>{pri}</priority>{alts}{imgs}\n  </url>')
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    (OUT / "manifest.webmanifest").write_text(json.dumps({
        "name": "Yiasemi · Γιασεμί", "short_name": "Yiasemi", "description": "Café bistrot on the steps of Mnisikleous, Plaka, Athens",
        "start_url": "/", "display": "standalone", "background_color": "#f6f0e6", "theme_color": "#5e6e45", "lang": "en",
        "icons": [{"src": "/images/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/images/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "/images/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, ensure_ascii=False, indent=1), encoding="utf-8")

CSP = ("default-src 'self'; script-src 'self' '" + THEME_HASH + "'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; "
       "connect-src 'self'; frame-src https://www.google.com https://maps.google.com; base-uri 'self'; form-action 'self'; "
       "frame-ancestors 'self'; object-src 'none'; upgrade-insecure-requests")
SECURITY_HEADERS = [
    {"key": "Content-Security-Policy", "value": CSP},
    {"key": "X-Content-Type-Options", "value": "nosniff"},
    {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
    {"key": "X-Frame-Options", "value": "SAMEORIGIN"},
    {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), payment=(), usb=()"},
    {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains"},
]

def vercel_config():
    cfg = {"$schema": "https://openapi.vercel.sh/vercel.json", "outputDirectory": "public", "cleanUrls": True, "trailingSlash": False,
           "headers": [
               {"source": "/(images|fonts)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=2592000, stale-while-revalidate=86400"}]},
               {"source": "/(css|js)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
               {"source": "/(.*)", "headers": SECURITY_HEADERS}]}
    (ROOT / "vercel.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    (ROOT / "deploy").mkdir(exist_ok=True)
    (ROOT / "deploy/security-headers.json").write_text(json.dumps(SECURITY_HEADERS, indent=2) + "\n", encoding="utf-8")

def main():
    global LANG
    n = validate_menu(MENU)
    for LANG in ("en", "el"):
        home(); menu(); photos(); visit(); privacy(); credits()
    notfound(); sitemap(); vercel_config()
    print(f"built: {n} menu items, {len(PHOTOS)} photos")

if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        sys.exit(f"build failed: {e}")
