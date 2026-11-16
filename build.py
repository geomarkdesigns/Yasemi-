#!/usr/bin/env python3
"""Yiasemi static site generator.

Builds English pages at /, Greek pages at /el/, plus sitemap.xml, robots.txt,
manifest and 404 into ./public.  Run:  python3 build.py
Edit text below (every string is a pair: English, Greek).
Photos are described in public/images/photos.json (made by tools/images.py).
"""
import json, html, pathlib, datetime

BASE = "https://yiasemi.vercel.app"          # change to your custom domain later
PHONE = "+302130417937"
PHONE_TXT = "+30 213 041 7937"
OUT = pathlib.Path(__file__).parent / "public"
PHOTOS = json.loads((OUT / "images/photos.json").read_text(encoding="utf-8")) if (OUT / "images/photos.json").exists() else {}
TODAY = datetime.date.today().isoformat()
LANG = "en"

def T(en, el):
    return el if LANG == "el" else en

def esc(s):
    return html.escape(s, quote=True)

def url(path, lang=None):
    lang = lang or LANG
    p = path.strip("/")
    pre = "/el" if lang == "el" else ""
    return f"{pre}/{p}" if p else (pre or "/")

def abs_url(path, lang=None):
    return BASE + url(path, lang)

# ---------------------------------------------------------------- graphics
def jasmine(cls="", fill=True, style=""):
    petals = "".join(f'<ellipse cx="20" cy="10.5" rx="5.2" ry="8.5" transform="rotate({a} 20 20)"/>' for a in (0, 72, 144, 216, 288))
    st = f' style="{style}"' if style else ""
    if fill:
        return f'<svg class="{cls}"{st} viewBox="0 0 40 40" aria-hidden="true"><g fill="currentColor">{petals}</g><circle cx="20" cy="20" r="3.4" fill="var(--bg)"/></svg>'
    return f'<svg class="{cls}"{st} viewBox="0 0 40 40" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.4">{petals}<circle cx="20" cy="20" r="3"/></g></svg>'

ARROW = '<span class="arrow" aria-hidden="true">→</span>'
ICON = {
 "book": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5"/></svg>',
 "people": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15 14.5c3 0 6 1.8 6 5"/></svg>',
 "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
}

# ---------------------------------------------------------------- photos
def pic(pid, cls="", color="c-stone", sizes="100vw", eager=False, extra="", cap=None, full=False):
    """A <figure> frame with a responsive <picture>. Falls back to a jasmine placeholder."""
    p = PHOTOS.get(pid)
    ph = f'<div class="ph">{jasmine(fill=False)}</div>'
    if not p:
        return f'<figure class="frame {color} {cls}"{extra}>{ph}</figure>'
    alt = esc(p["alt"][LANG])
    webp = ", ".join(f'/images/{p["base"]}-{w}.webp {w}w' for w in p["widths"])
    jpg = ", ".join(f'/images/{p["base"]}-{w}.jpg {w}w' for w in p["widths"])
    mid = p["widths"][min(1, len(p["widths"]) - 1)]
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    caption = ""
    if cap is not None:
        caption = f'<figcaption>{cap}</figcaption>'
    fd = f' data-full="/images/{p["base"]}-{p["widths"][-1]}.webp"' if full else ""
    return (f'<figure class="frame {color} {cls}"{extra}{fd}>{ph}<picture>'
            f'<source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="/images/{p["base"]}-{mid}.jpg" srcset="{jpg}" sizes="{sizes}" alt="{alt}" '
            f'width="{p["w"]}" height="{p["h"]}" {load} decoding="async"></picture>{caption}</figure>')

def img_abs(pid, w=None):
    p = PHOTOS.get(pid)
    if not p: return BASE + "/images/og.jpg"
    w = w or p["widths"][-1]
    return f'{BASE}/images/{p["base"]}-{w}.jpg'

# ---------------------------------------------------------------- shared data
ADDRESS = {"@type": "PostalAddress", "streetAddress": "Mnisikleous 23", "addressLocality": "Athens",
           "addressRegion": "Attica", "postalCode": "105 55", "addressCountry": "GR"}
ADDRESS_EL = {**ADDRESS, "streetAddress": "Μνησικλέους 23", "addressLocality": "Αθήνα", "addressRegion": "Αττική"}

def cafe_ld():
    return {
        "@type": "CafeOrCoffeeShop", "@id": f"{BASE}/#cafe",
        "name": "Yiasemi", "alternateName": ["Γιασεμί", "Yasemi", "Yiasemi Café Plaka"],
        "description": T("A cosy café on the stepped Mnisikleous Street in Plaka, Athens, below the Acropolis, serving Greek coffee, homemade pies, sweets and rakomelo.",
                         "Φιλόξενο καφέ στα σκαλιά της Μνησικλέους στην Πλάκα, κάτω από την Ακρόπολη, με ελληνικό καφέ, σπιτικές πίτες, γλυκά και ρακόμελο."),
        "url": abs_url(""), "telephone": PHONE,
        "address": ADDRESS_EL if LANG == "el" else ADDRESS,
        "image": [img_abs(k) for k in ("hero", "about", "evening-1") if k in PHOTOS] or [BASE + "/images/og.jpg"],
        "logo": BASE + "/images/icon-512.png",
        "servesCuisine": ["Greek", "Coffee", "Desserts", "Meze"],
        "hasMenu": abs_url("menu"),
        "areaServed": {"@type": "Place", "name": "Plaka, Athens"},
        "hasMap": "https://www.google.com/maps/search/?api=1&query=Yiasemi+Mnisikleous+23+Athens",
        "containedInPlace": {"@type": "Place", "name": T("Plaka, Athens", "Πλάκα, Αθήνα")},
        "knowsLanguage": ["el", "en"],
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": T("Outdoor seating on the steps", "Θέσεις στα σκαλιά"), "value": True}],
    }

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
            "primaryImageOfPage": {"@type": "ImageObject", "url": img or img_abs("hero")},
            "dateModified": TODAY}

# ---------------------------------------------------------------- layout
NAV = [("", ("Home", "Αρχική")), ("menu", ("Menu", "Μενού")), ("photos", ("More photos", "Περισσότερες φωτογραφίες")), ("visit", ("Visit", "Επίσκεψη"))]

def head(path, title, desc, ld, og_img=None, noindex=False, og_type="website"):
    other = "el" if LANG == "en" else "en"
    og_img = og_img or BASE + "/images/og.jpg"
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    alts = "" if noindex else (
        f'<link rel="alternate" hreflang="en" href="{abs_url(path, "en")}">\n'
        f'<link rel="alternate" hreflang="el" href="{abs_url(path, "el")}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{abs_url(path, "en")}">\n')
    graph = json.dumps({"@context": "https://schema.org", "@graph": ld}, ensure_ascii=False, separators=(",", ":"))
    hero_preload = ""
    if path == "" and "hero" in PHOTOS:
        p = PHOTOS["hero"]
        ss = ", ".join(f'/images/{p["base"]}-{w}.webp {w}w' for w in p["widths"])
        hero_preload = f'<link rel="preload" as="image" type="image/webp" imagesrcset="{ss}" imagesizes="(max-width: 960px) 92vw, 440px" fetchpriority="high">\n'
    return f'''<!doctype html>
<html lang="{LANG}" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{abs_url(path)}">
{alts}<meta name="theme-color" content="#f6f0e6">
<meta name="color-scheme" content="light dark">
<meta name="format-detection" content="telephone=yes">
<meta name="geo.region" content="GR-I">
<meta name="geo.placename" content="{T("Plaka, Athens", "Πλάκα, Αθήνα")}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{T("Yiasemi Café · Plaka, Athens", "Γιασεμί Καφέ · Πλάκα, Αθήνα")}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{abs_url(path)}">
<meta property="og:locale" content="{"el_GR" if LANG == "el" else "en_US"}">
<meta property="og:locale:alternate" content="{"en_US" if LANG == "el" else "el_GR"}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(T("Mnisikleous Street in Plaka, Athens, home of Yiasemi café", "Η οδός Μνησικλέους στην Πλάκα, όπου βρίσκεται το Γιασεμί"))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{og_img}">
<link rel="icon" href="/images/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{hero_preload}<link href="https://fonts.googleapis.com/css2?family=Commissioner:wght@300;400;500&family=GFS+Didot&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
<script>try{{var d=document.documentElement,t=localStorage.getItem("theme")||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light");d.setAttribute("data-theme",t)}}catch(e){{}}</script>
<script src="/js/main.js" defer></script>
<script type="application/ld+json">{graph}</script>
</head>
<body>
<a class="skip" href="#main">{T("Skip to content", "Μετάβαση στο περιεχόμενο")}</a>
<header class="site-header">
  <nav class="wrap nav" aria-label="{T("Main", "Κύριο μενού")}">
    <a href="{url("")}" class="logo" aria-label="{T("Yiasemi home", "Γιασεμί αρχική")}">{jasmine()}<span>{T("Yiasemi", "Γιασεμί")}</span></a>
    <ul class="links">
      {"".join(f'<li><a href="{url(p)}"{" aria-current=\"page\"" if p == path else ""}>{T(*n)}</a></li>' for p, n in NAV)}
    </ul>
    <div class="controls">
      <a class="pill-btn lang-link" href="{url(path, other)}" hreflang="{other}" lang="{other}" title="{"English" if other == "en" else "Ελληνικά"}">{"EN" if other == "en" else "ΕΛ"}</a>
      <button class="pill-btn" id="theme-toggle" type="button" aria-label="{T("Toggle dark mode", "Εναλλαγή σκοτεινής λειτουργίας")}">
        <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
      <button class="pill-btn menu-toggle" type="button" aria-label="{T("Open menu", "Άνοιγμα μενού")}" aria-expanded="false">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M4 9h16M4 15h16"/></svg>
      </button>
    </div>
  </nav>
</header>
<main id="main">
'''

def foot():
    return f'''</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="meander" aria-hidden="true"></div>
    <div class="foot-grid" style="margin-top:44px">
      <div>
        <a href="{url("")}" class="logo">{jasmine()}<span>{T("Yiasemi", "Γιασεμί")}</span></a>
        <p class="muted" style="margin-top:14px;max-width:34ch">{T("A café on the steps of Mnisikleous, below the Acropolis. Pull up a cushion and stay a while.", "Ένα καφέ στα σκαλιά της Μνησικλέους, κάτω από την Ακρόπολη. Πάρτε ένα μαξιλάρι και μείνετε λίγο.")}</p>
      </div>
      <div>
        <h2 class="foot-h">{T("Pages", "Σελίδες")}</h2>
        <ul>{"".join(f'<li><a href="{url(p)}">{T(*n)}</a></li>' for p, n in NAV[1:])}<li><a href="{url("credits")}">{T("Photo credits", "Πηγές φωτογραφιών")}</a></li></ul>
      </div>
      <div>
        <h2 class="foot-h">{T("Find us", "Βρείτε μας")}</h2>
        <address style="font-style:normal"><ul>
          <li>{T("Mnisikleous 23, Plaka", "Μνησικλέους 23, Πλάκα")}</li>
          <li>{T("105 55 Athens, Greece", "105 55 Αθήνα")}</li>
          <li><a href="tel:{PHONE}">{PHONE_TXT}</a></li>
        </ul></address>
      </div>
    </div>
    <div class="wordmark" aria-hidden="true">Γιασεμί</div>
    <div class="foot-base">
      <span>&copy; <span id="year">2026</span> {T("Yiasemi", "Γιασεμί")} · {T("Athens time", "Ώρα Αθήνας")} <span data-athens-time>--:--</span></span>
      <a href="#main" class="to-top">{T("Back to top ↑", "Επιστροφή επάνω ↑")}</a>
    </div>
  </div>
</footer>
<nav class="dock" aria-label="{T("Quick actions", "Γρήγορες ενέργειες")}">
  <a href="tel:{PHONE}">{T("Call", "Κλήση")}</a>
  <a class="primary" href="{GMAPS}" target="_blank" rel="noopener">{T("Directions", "Οδηγίες")}</a>
</nav>
</body>
</html>
'''

GMAPS = "https://www.google.com/maps/search/?api=1&amp;query=Yiasemi+Mnisikleous+23+Athens"
MAP_SRC = "https://www.google.com/maps?q=Yiasemi,+Mnisikleous+23,+Athens+105+55&amp;z=17&amp;output=embed"

def map_iframe():
    lang = "&amp;hl=el" if LANG == "el" else "&amp;hl=en"
    return f'<div class="map reveal" data-delay="120"><iframe title="{T("Map: Yiasemi, Mnisikleous 23, Plaka, Athens", "Χάρτης: Γιασεμί, Μνησικλέους 23, Πλάκα, Αθήνα")}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="{MAP_SRC}{lang}"></iframe></div>'

def info_dl():
    return f'''<dl>
  <div><dt>{T("Address", "Διεύθυνση")}</dt><dd>{T("Mnisikleous 23, Plaka, 105 55 Athens", "Μνησικλέους 23, Πλάκα, 105 55 Αθήνα")}</dd></div>
  <div><dt>{T("Phone", "Τηλέφωνο")}</dt><dd><a href="tel:{PHONE}">{PHONE_TXT}</a></dd></div>
  <div><dt>{T("Hours", "Ωράριο")}</dt><dd>{T("Please call ahead to confirm", "Παρακαλούμε τηλεφωνήστε για επιβεβαίωση")}</dd></div>
  <div><dt>{T("Directions", "Οδηγίες")}</dt><dd><a href="{GMAPS}" target="_blank" rel="noopener">{T("Open in Google Maps ↗", "Άνοιγμα στο Google Maps ↗")}</a></dd></div>
</dl>'''

def write(path, content):
    f = OUT / (("el/" if LANG == "el" else "") + (path or "index") + ".html")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")

# ================================================================ HOME
def home():
    title = T("Yiasemi Café in Plaka, Athens | Greek Coffee on the Mnisikleous Steps",
              "Γιασεμί Καφέ στην Πλάκα | Ελληνικός Καφές στα Σκαλιά της Μνησικλέους")
    desc = T("Yiasemi (Γιασεμί) is a cosy café on the stepped Mnisikleous Street in Plaka, below the Acropolis. Greek coffee, homemade pies, orange cake with mastic ice cream and rakomelo. Come sit on the steps.",
             "Το Γιασεμί είναι ένα φιλόξενο καφέ στα σκαλιά της Μνησικλέους στην Πλάκα, κάτω από την Ακρόπολη. Ελληνικός καφές, σπιτικές πίτες, πορτοκαλόπιτα με παγωτό μαστίχα και ρακόμελο.")
    ring = "MNISIKLEOUS 23 · PLAKA · ATHENS · ΓΙΑΣΕΜΙ · "
    mq_items = [("Greek coffee", "Ελληνικός καφές"), ("Orange cake", "Πορτοκαλόπιτα"), ("Mastic ice cream", "Παγωτό μαστίχα"),
                ("Spinach pie", "Σπανακόπιτα"), ("Rakomelo", "Ρακόμελο"), ("Mezes", "Μεζέδες"), ("Mountain tea", "Τσάι του βουνού"), ("Freddo espresso", "Freddo espresso")]
    mq = "".join(f'<span class="item">{T(a, b)}</span>' for a, b in mq_items)

    g = {
     "sun": '<svg class="glyph" viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><path d="M4 24h26"/><path d="M10 24a7 7 0 0 1 14 0"/><path d="M17 9v3M8 13l2 2M26 13l-2 2"/></svg>',
     "noon": '<svg class="glyph" viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><circle cx="17" cy="17" r="6"/><path d="M17 4v3M17 27v3M4 17h3M27 17h3M8 8l2 2M24 24l2 2M8 26l2-2M24 10l2-2"/></svg>',
     "cup": '<svg class="glyph" viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><path d="M7 14h17v6a7 7 0 0 1-7 7h-3a7 7 0 0 1-7-7z"/><path d="M24 16h2a3 3 0 0 1 0 6h-2"/><path d="M12 5c-1 2 1 3 0 5M17 5c-1 2 1 3 0 5"/></svg>',
     "moon": '<svg class="glyph" viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M25 20.5A10 10 0 1 1 13.5 9a8 8 0 0 0 11.5 11.5z"/><path d="M25 6v4M23 8h4"/></svg>',
    }
    steps = [
      ("sun", ("Morning", "Πρωί"), ("Coffee &amp; pie", "Καφές &amp; πίτα"), ("A Greek coffee from the briki and a warm slice of spinach pie.", "Ελληνικός καφές στο μπρίκι και ένα ζεστό κομμάτι σπανακόπιτα.")),
      ("noon", ("Midday", "Μεσημέρι"), ("Mezes in the shade", "Μεζέδες στη σκιά"), ("Small plates to share while the street fills up.", "Μικρά πιάτα για μοίρασμα, καθώς ο δρόμος γεμίζει.")),
      ("cup", ("Afternoon", "Απόγευμα"), ("Something sweet", "Κάτι γλυκό"), ("Orange cake with a scoop of mastic ice cream.", "Πορτοκαλόπιτα με μπάλα παγωτό μαστίχα.")),
      ("moon", ("Evening", "Βράδυ"), ("Rakomelo", "Ρακόμελο"), ("Warm raki with honey as the street lights come on.", "Ζεστή ρακή με μέλι, καθώς ανάβουν τα φώτα.")),
    ]
    steps_html = "".join(f'<div class="step reveal" data-delay="{i*110}">{g[k]}<span class="time">{T(*a)}</span><h3>{T(*b)}</h3><p>{T(*c)}</p></div>' for i, (k, a, b, c) in enumerate(steps))

    sigs = [("sig-coffee", "c-clay", ("The classic", "Το κλασικό"), ("Greek coffee", "Ελληνικός καφές"), ("Slow-brewed in a briki, with a glass of cold water.", "Ψημένος αργά στο μπρίκι, με ένα ποτήρι κρύο νερό.")),
            ("sig-sweet", "c-olive", ("Guest favourite", "Αγαπημένο"), ("Orange cake &amp; mastic", "Πορτοκαλόπιτα &amp; μαστίχα"), ("Syrupy portokalopita with a scoop of mastic ice cream.", "Σιροπιαστή πορτοκαλόπιτα με παγωτό μαστίχα.")),
            ("sig-pie", "c-sea", ("Made here", "Φτιαγμένες εδώ"), ("Homemade pies", "Σπιτικές πίτες"), ("Spinach and cheese pies in crisp filo, made daily.", "Σπανακόπιτα και τυρόπιτα σε τραγανό φύλλο, κάθε μέρα."))]
    sigs_html = "".join(f'<article class="sig reveal" data-delay="{i*120}">{pic(pid, "arch", col, "(max-width: 760px) 92vw, 360px")}<span class="tag">{T(*tag)}</span><h3 style="margin-top:6px">{T(*h)}</h3><p>{T(*p)}</p></article>' for i, (pid, col, tag, h, p) in enumerate(sigs))

    def cup(gr, say, en, el, n):
        sugar = "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(3))
        return f'<div class="cup reveal"><span class="gr" lang="el">{gr}</span><span class="say">{say}</span><p>{T(en, el)}</p><div class="sugar" aria-hidden="true">{sugar}</div></div>'
    cups = (cup("Σκέτος", "[ské-tos]", "No sugar. Strong and bitter, the purist's cup.", "Χωρίς ζάχαρη. Δυνατός και πικρός.", 0)
          + cup("Μέτριος", "[mé-tri-os]", "Medium. One teaspoon of sugar, the most popular order.", "Με ένα κουταλάκι ζάχαρη. Η πιο συνηθισμένη επιλογή.", 1)
          + cup("Γλυκός", "[gli-kós]", "Sweet. Two teaspoons, rich and smooth.", "Με δύο κουταλάκια ζάχαρη. Πλούσιος και απαλός.", 2))

    invites = [("book", ("On your own", "Μόνοι σας"), ("Bring a book, take a cushion, order a coffee and let the afternoon go slowly. Nobody will rush you.", "Φέρτε ένα βιβλίο, πάρτε ένα μαξιλάρι, παραγγείλτε καφέ και αφήστε το απόγευμα να κυλήσει. Κανείς δεν θα σας βιάσει.")),
               ("people", ("With friends &amp; family", "Με φίλους &amp; οικογένεια"), ("Share mezes, sweets and a round of rakomelo. Coming as a bigger group? Give us a call before you come.", "Μοιραστείτε μεζέδες, γλυκά και ένα γύρο ρακόμελο. Έρχεστε πολλοί; Πάρτε μας ένα τηλέφωνο πριν έρθετε.")),
               ("pin", ("Before or after the Acropolis", "Πριν ή μετά την Ακρόπολη"), ("We're on the way up. Stop for a freddo on the climb, or rest your feet with something sweet on the way down.", "Είμαστε στον δρόμο προς τα πάνω. Ένας freddo στην ανάβαση ή κάτι γλυκό στην κατάβαση."))]
    inv_html = "".join(f'<div class="invite-card reveal" data-delay="{i*110}"><div class="emoji">{ICON[ic]}</div><h3>{T(*h)}</h3><p>{T(*p)}</p></div>' for i, (ic, h, p) in enumerate(invites))

    faqs = home_faqs()
    ld = [website_ld(), cafe_ld(), webpage_ld("", title, desc), crumbs_ld([(T("Home", "Αρχική"), abs_url(""))]),
          {"@type": "FAQPage", "@id": abs_url("") + "#faq", "inLanguage": LANG,
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}]

    faq_html = "".join(f'<details class="faq reveal"><summary>{q}</summary><p>{a}</p></details>' for q, a in faqs)

    body = f'''
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="greeting reveal">{jasmine()}<span data-greeting>{T("Welcome. There's a spot on the steps for you.", "Καλώς ήρθατε. Υπάρχει θέση στα σκαλιά για εσάς.")}</span></p>
      <h1 class="reveal" data-delay="80">{T('Yiasemi, a slow café on the <span class="soft">steps</span> of Plaka.', 'Γιασεμί, ένα χαλαρό καφέ στα <span class="soft">σκαλιά</span> της Πλάκας.')}</h1>
      <p class="lead reveal" data-delay="160" style="margin-top:24px">{T("Greek coffee, homemade pies and sweets on Mnisikleous Street, just below the Acropolis. Pull up a cushion, stay as long as you like.", "Ελληνικός καφές, σπιτικές πίτες και γλυκά στην οδό Μνησικλέους, κάτω από την Ακρόπολη. Πάρτε ένα μαξιλάρι και μείνετε όσο θέλετε.")}</p>
      <div class="actions reveal" data-delay="240">
        <a class="btn btn-solid" href="{url("visit")}">{T("Come and visit", "Ελάτε να μας δείτε")} {ARROW}</a>
        <a class="btn btn-ghost" href="{url("menu")}">{T("See the menu", "Δείτε το μενού")}</a>
      </div>
      <div class="facts reveal" data-delay="320">
        <span class="chip"><span class="dot"></span>{T("Athens", "Αθήνα")} <span data-athens-time>--:--</span></span>
        <span class="chip">{T("Mnisikleous 23", "Μνησικλέους 23")}</span>
        <span class="chip">{T("≈ 7 min from Monastiraki", "≈ 7 λεπτά από Μοναστηράκι")}</span>
      </div>
    </div>
    <div class="hero-photo reveal" data-delay="200">
      {pic("hero", "arch", "c-olive", "(max-width: 960px) 92vw, 440px", eager=True)}
      <div class="badge" aria-hidden="true">
        <svg class="ring" viewBox="0 0 116 116"><defs><path id="circ" d="M58 58m-46 0a46 46 0 1 1 92 0a46 46 0 1 1-92 0"/></defs><text><textPath href="#circ">{ring}</textPath></text></svg>
        {jasmine("core")}
      </div>
    </div>
  </div>
  <div class="marquee" aria-hidden="true"><div class="marquee-track">{mq}{mq}</div></div>
</section>

<section class="wrap" aria-labelledby="about-h">
  <div class="about">
    {pic("about", "reveal", "c-clay", "(max-width: 960px) 92vw, 500px")}
    <div class="reveal" data-delay="120">
      <p class="eyebrow">{T("Our place", "Ο χώρος μας")}</p>
      <h2 id="about-h">{T("Named after jasmine.", "Πήραμε το όνομα από το γιασεμί.")}</h2>
      <p class="muted" style="margin-top:20px">{T("<i>Yiasemi</i> (Γιασεμί) is Greek for jasmine, the small white flower that scents the courtyards of old Athens on summer nights.", "Το γιασεμί είναι το μικρό λευκό λουλούδι που αρωματίζει τις αυλές της παλιάς Αθήνας τις καλοκαιρινές νύχτες.")}</p>
      <p class="muted">{T("Cushions on the marble steps, small tables, and an easy pace from morning until late. Sit, order a coffee, and watch Plaka go by.", "Μαξιλάρια στα μαρμάρινα σκαλιά, μικρά τραπεζάκια και χαλαρός ρυθμός από το πρωί ως αργά. Καθίστε, παραγγείλτε έναν καφέ και δείτε την Πλάκα να περνά.")}</p>
      <div class="mini-facts">
        <div><b>{T("Steps", "Σκαλιά")}</b><span>{T("seating on Mnisikleous", "θέσεις στη Μνησικλέους")}</span></div>
        <div><b>{T("Daily", "Καθημερινά")}</b><span>{T("homemade pies &amp; sweets", "σπιτικές πίτες &amp; γλυκά")}</span></div>
        <div><b>{T("Plaka", "Πλάκα")}</b><span>{T("below the Acropolis", "κάτω από την Ακρόπολη")}</span></div>
      </div>
    </div>
  </div>
</section>

<section class="wrap" aria-labelledby="inv-h">
  <div class="sec-head">
    <div><p class="eyebrow reveal">{T("Everyone's welcome", "Όλοι είναι καλοδεχούμενοι")}</p><h2 id="inv-h" class="reveal" data-delay="80">{T("Come as you are.", "Ελάτε όπως είστε.")}</h2></div>
    <p class="muted reveal" data-delay="140">{T("Locals, travellers, early birds and night owls. There's always room for one more on the steps.", "Ντόπιοι, ταξιδιώτες, πρωινοί και νυχτοπούλια. Πάντα υπάρχει χώρος για έναν ακόμα στα σκαλιά.")}</p>
  </div>
  <div class="invite">{inv_html}</div>
</section>

<section class="wrap" aria-labelledby="day-h">
  <div class="sec-head">
    <div><p class="eyebrow reveal">{T("A day on the steps", "Μια μέρα στα σκαλιά")}</p><h2 id="day-h" class="reveal" data-delay="80">{T("From first coffee<br>to rakomelo.", "Από τον πρώτο καφέ<br>ως το ρακόμελο.")}</h2></div>
  </div>
  <div class="steps">{steps_html}</div>
</section>

<section class="wrap" aria-labelledby="sig-h">
  <div class="sec-head">
    <div><p class="eyebrow reveal">{T("Signatures", "Τα αγαπημένα")}</p><h2 id="sig-h" class="reveal" data-delay="80">{T("What people come back for.", "Αυτά για τα οποία επιστρέφουν.")}</h2></div>
    <a class="btn btn-ghost reveal" href="{url("menu")}">{T("Full menu", "Όλο το μενού")} {ARROW}</a>
  </div>
  <div class="sigs">{sigs_html}</div>
</section>

<section class="wrap" id="greek-coffee" aria-labelledby="gc-h">
  <div class="guide">
    <p class="eyebrow reveal">{T("A small guide", "Ένας μικρός οδηγός")}</p>
    <h2 id="gc-h" class="reveal" data-delay="80">{T("How to order Greek coffee.", "Πώς παραγγέλνεις ελληνικό καφέ.")}</h2>
    <p class="lead reveal" data-delay="140" style="margin-top:18px">{T("The sugar goes into the briki while it brews, so you choose before it's made.", "Η ζάχαρη μπαίνει στο μπρίκι πριν ψηθεί, γι' αυτό τη διαλέγεις από πριν.")}</p>
    <div class="cups">{cups}</div>
    <p class="tip reveal">{jasmine(style="width:16px;height:16px;flex:none;color:var(--clay);transform:translateY(3px)")}<span>{T("<b>Tip:</b> let the grounds settle for a minute, sip slowly, and leave the last mouthful in the cup.", "<b>Συμβουλή:</b> αφήστε το κατακάθι να κατακαθίσει, πίνετε αργά και αφήστε την τελευταία γουλιά στο φλιτζάνι.")}</span></p>
  </div>
</section>

<section class="quote wrap">
  <div class="reveal">{jasmine("mark")}</div>
  <blockquote class="reveal" data-delay="80">{T("“Athens' best café for people watching.”", "«Το καλύτερο καφέ της Αθήνας για να χαζεύεις τον κόσμο.»")}</blockquote>
  <cite class="reveal" data-delay="160">{T("Headline,", "Τίτλος άρθρου,")} <a href="https://greekcitytimes.com/2022/04/16/yiasemi-athens-for-people-watching" target="_blank" rel="noopener">Greek City Times</a></cite>
</section>

<section class="wrap" aria-labelledby="faq-h">
  <div class="sec-head"><div><p class="eyebrow reveal">{T("Good to know", "Χρήσιμα")}</p><h2 id="faq-h" class="reveal" data-delay="80">{T("Questions guests ask.", "Ερωτήσεις των επισκεπτών.")}</h2></div></div>
  <div class="faqs">{faq_html}</div>
</section>

<section class="wrap" style="padding-top:0">
  <div class="cta-band reveal">
    {jasmine("big-flower")}
    <div>
      <h2>{T("There's a cushion with your name on it.", "Υπάρχει ένα μαξιλάρι που σας περιμένει.")}</h2>
      <p>{T("Mnisikleous 23, Plaka. Climb a few steps, find a spot, and we'll bring the coffee.", "Μνησικλέους 23, Πλάκα. Ανεβείτε λίγα σκαλιά, βρείτε θέση και ο καφές έρχεται.")}</p>
    </div>
    <div class="actions">
      <a class="btn btn-solid" href="{GMAPS}" target="_blank" rel="noopener">{T("Get directions", "Οδηγίες")} {ARROW}</a>
      <a class="btn btn-ghost" href="tel:{PHONE}">{T("Call us", "Καλέστε μας")}</a>
    </div>
  </div>
</section>

<section class="wrap" aria-labelledby="loc-h">
  <div class="location">
    <div class="info reveal">
      <p class="eyebrow">{T("Visit", "Επίσκεψη")}</p>
      <h2 id="loc-h" style="margin-bottom:28px">{T("Find us", "Βρείτε μας")}</h2>
      {info_dl()}
      <div class="actions"><a class="btn btn-ghost" href="{url("visit")}">{T("Getting here &amp; nearby", "Πώς θα έρθετε &amp; κοντά μας")} {ARROW}</a></div>
    </div>
    {map_iframe()}
  </div>
</section>
'''
    write("", head("", title, desc, ld, og_img=BASE + "/images/og.jpg") + body + foot())

def home_faqs():
    return [
      (T("Where is Yiasemi café?", "Πού βρίσκεται το Γιασεμί;"),
       T("Yiasemi is at Mnisikleous 23 in Plaka, Athens (105 55), on the stepped pedestrian street that climbs toward the Acropolis.", "Το Γιασεμί βρίσκεται στη Μνησικλέους 23 στην Πλάκα (105 55), στον σκαλωτό πεζόδρομο που ανεβαίνει προς την Ακρόπολη.")),
      (T("What is the nearest metro station?", "Ποιος είναι ο πλησιέστερος σταθμός μετρό;"),
       T("Monastiraki (lines 1 and 3) is about a 7-minute walk away. Syntagma and Akropoli stations are around 15 minutes on foot.", "Το Μοναστηράκι (γραμμές 1 και 3) απέχει περίπου 7 λεπτά με τα πόδια. Σύνταγμα και Ακρόπολη περίπου 15 λεπτά.")),
      (T("What should I order at Yiasemi?", "Τι να παραγγείλω στο Γιασεμί;"),
       T("Try a traditional Greek coffee, a homemade spinach or cheese pie, and orange cake (portokalopita) with mastic ice cream. In the evening, a warm rakomelo.", "Δοκιμάστε ελληνικό καφέ, σπιτική σπανακόπιτα ή τυρόπιτα και πορτοκαλόπιτα με παγωτό μαστίχα. Το βράδυ, ένα ζεστό ρακόμελο.")),
      (T("Can I sit outside?", "Μπορώ να καθίσω έξω;"),
       T("Yes. Yiasemi is known for its seating with cushions on the marble steps of Mnisikleous Street.", "Ναι. Το Γιασεμί είναι γνωστό για τις θέσεις με μαξιλάρια στα μαρμάρινα σκαλιά της Μνησικλέους.")),
      (T("Is it close to the Acropolis?", "Είναι κοντά στην Ακρόπολη;"),
       T("Yes. Mnisikleous Street leads up toward the Acropolis; the entrance is roughly a 12-minute uphill walk.", "Ναι. Η Μνησικλέους οδηγεί προς την Ακρόπολη· η είσοδος απέχει περίπου 12 λεπτά ανηφορικό περπάτημα.")),
      (T("What are the opening hours?", "Ποιο είναι το ωράριο;"),
       T(f"Hours can change with the season, so please call {PHONE_TXT} before you come.", f"Το ωράριο αλλάζει ανάλογα με την εποχή, γι' αυτό τηλεφωνήστε στο {PHONE_TXT} πριν έρθετε.")),
    ]

# ================================================================ MENU
MENU = [
 ("coffee", ("Coffee", "Καφές"), [
   ("Greek coffee", "Ελληνικός καφές", "Traditional, brewed in a briki", "Παραδοσιακός, στο μπρίκι", False),
   ("Freddo espresso", "Freddo espresso", "Double espresso shaken over ice", "Διπλός espresso χτυπημένος με πάγο", False),
   ("Freddo cappuccino", "Freddo cappuccino", "With cold milk foam", "Με κρύο αφρόγαλα", False),
   ("Frappé", "Φραπέ", "The classic Greek iced coffee", "Ο κλασικός ελληνικός κρύος καφές", False),
   ("Espresso", "Espresso", "Single or double", "Μονός ή διπλός", False),
   ("Cappuccino", "Cappuccino", "Hot, with steamed milk", "Ζεστός, με αφρόγαλα", False)]),
 ("tea", ("Tea &amp; more", "Τσάι &amp; άλλα"), [
   ("Mountain tea", "Τσάι του βουνού", "Greek herbal tea with honey", "Ελληνικό τσάι του βουνού με μέλι", False),
   ("Chamomile", "Χαμομήλι", "Calm, with honey", "Με μέλι", False),
   ("Hot chocolate", "Ζεστή σοκολάτα", "Rich and thick", "Πλούσια και πηχτή", False),
   ("Fresh orange juice", "Φρέσκος χυμός πορτοκάλι", "Squeezed to order", "Στυμμένος τη στιγμή", False),
   ("Homemade lemonade", "Σπιτική λεμονάδα", "Fresh lemon and mint", "Φρέσκο λεμόνι και δυόσμος", False)]),
 ("food", ("Pies &amp; plates", "Πίτες &amp; πιάτα"), [
   ("Spinach pie", "Σπανακόπιτα", "Homemade, crisp filo", "Σπιτική, τραγανό φύλλο", True),
   ("Cheese pie", "Τυρόπιτα", "With feta", "Με φέτα", True),
   ("Meze plate", "Πιατέλα μεζέδων", "Small plates to share", "Μικρά πιάτα για μοίρασμα", False),
   ("Greek salad", "Χωριάτικη", "Tomato, cucumber, onion, olives, feta", "Ντομάτα, αγγούρι, κρεμμύδι, ελιές, φέτα", True),
   ("Toast", "Τοστ", "Ham and cheese, or cheese only", "Ζαμπόν-τυρί ή σκέτο τυρί", False)]),
 ("sweets", ("Sweets", "Γλυκά"), [
   ("Orange cake", "Πορτοκαλόπιτα", "With a scoop of mastic ice cream", "Με μπάλα παγωτό μαστίχα", True),
   ("Yogurt with honey", "Γιαούρτι με μέλι", "Greek yogurt, thyme honey, walnuts", "Θυμαρίσιο μέλι, καρύδια", True),
   ("Galaktoboureko", "Γαλακτομπούρεκο", "Semolina custard in filo, syrup", "Κρέμα σιμιγδαλιού σε φύλλο, σιρόπι", True),
   ("Baklava", "Μπακλαβάς", "Walnuts, filo and honey syrup", "Καρύδι, φύλλο και σιρόπι μελιού", True),
   ("Cake of the day", "Γλυκό ημέρας", "Ask us what's fresh", "Ρωτήστε μας τι είναι φρέσκο", True)]),
 ("evening", ("Evening", "Βράδυ"), [
   ("Rakomelo", "Ρακόμελο", "Warm raki with honey and spices", "Ζεστή ρακή με μέλι και μπαχαρικά", False),
   ("House wine", "Κρασί χύμα", "White, red or rosé, by the glass", "Λευκό, κόκκινο ή ροζέ, στο ποτήρι", False),
   ("Ouzo", "Ούζο", "With ice and a small meze", "Με πάγο και μεζεδάκι", False),
   ("Greek beer", "Ελληνική μπίρα", "Ask for today's selection", "Ρωτήστε για τη σημερινή επιλογή", False)]),
]

def menu():
    title = T("Menu | Yiasemi Café, Plaka Athens: Greek Coffee, Pies & Sweets",
              "Μενού | Γιασεμί Καφέ, Πλάκα: Ελληνικός Καφές, Πίτες & Γλυκά")
    desc = T("The Yiasemi menu: traditional Greek coffee, freddo, homemade spinach and cheese pies, meze, orange cake with mastic ice cream, baklava and rakomelo, on Mnisikleous Street in Plaka.",
             "Το μενού του Γιασεμιού: ελληνικός καφές, freddo, σπιτική σπανακόπιτα και τυρόπιτα, μεζέδες, πορτοκαλόπιτα με παγωτό μαστίχα, μπακλαβάς και ρακόμελο, στη Μνησικλέους στην Πλάκα.")
    V = f'<span class="v" title="{T("Vegetarian", "Χορτοφαγικό")}" aria-label="{T("Vegetarian", "Χορτοφαγικό")}">V</span>'
    tabs = "".join(f'<button type="button" role="tab" id="t-{k}" aria-controls="g-{k}" aria-selected="{"true" if i == 0 else "false"}">{T(*lab)}</button>' for i, (k, lab, _) in enumerate(MENU))
    groups = ""
    for i, (k, lab, items) in enumerate(MENU):
        lis = "".join(f'<li class="menu-item"><div class="row"><h3>{T(en, el)}</h3>{V if veg else ""}<span class="dots"></span><span class="price">€ —</span></div><p>{T(den, dl)}</p></li>' for en, el, den, dl, veg in items)
        groups += f'<div class="menu-group{" active" if i == 0 else ""}" id="g-{k}" role="tabpanel" aria-labelledby="t-{k}"><h2 class="sr-only">{T(*lab)}</h2><ul class="menu-list">{lis}</ul></div>'
    menu_ld = {"@type": "Menu", "@id": abs_url("menu") + "#menu", "name": T("Yiasemi menu", "Μενού Γιασεμί"), "inLanguage": LANG,
               "hasMenuSection": [{"@type": "MenuSection", "name": html.unescape(T(*lab)),
                   "hasMenuItem": [dict({"@type": "MenuItem", "name": T(en, el), "description": T(den, dl)},
                                        **({"suitableForDiet": "https://schema.org/VegetarianDiet"} if veg else {})) for en, el, den, dl, veg in items]}
                   for k, lab, items in MENU]}
    cafe = cafe_ld(); cafe["hasMenu"] = {"@id": abs_url("menu") + "#menu"}
    ld = [website_ld(), cafe, menu_ld, webpage_ld("menu", title, desc, img=img_abs("sig-sweet")),
          crumbs_ld([(T("Home", "Αρχική"), abs_url("")), (T("Menu", "Μενού"), abs_url("menu"))])]
    body = f'''
<section class="wrap page-head">
  <p class="eyebrow reveal">{T("Menu", "Μενού")}</p>
  <h1 class="reveal" data-delay="80">{T("Coffee, pies<br>and sweets.", "Καφές, πίτες<br>και γλυκά.")}</h1>
  <p class="lead reveal" data-delay="160">{T("Simple Greek things, made well. Everything sweet and savoury comes from our kitchen. Take your time, there's no rush on the steps.", "Απλά ελληνικά πράγματα, φτιαγμένα σωστά. Όλα τα γλυκά και αλμυρά φτιάχνονται στην κουζίνα μας. Χωρίς βιασύνη στα σκαλιά.")}</p>
</section>
<section class="wrap" style="padding-top:8px">
  <div class="menu-tabs reveal" role="tablist" aria-label="{T("Menu sections", "Κατηγορίες μενού")}">{tabs}</div>
  <div class="menu-layout">
    <div>
      {groups}
      <p class="fine">{V} {T("Vegetarian. Items and prices are indicative and may change. Please tell us about any allergies.", "Χορτοφαγικό. Τα είδη και οι τιμές είναι ενδεικτικά. Ενημερώστε μας για τυχόν αλλεργίες.")}</p>
    </div>
    <aside class="aside reveal" data-delay="200">
      {pic("sig-coffee", "arch", "c-clay", "300px")}
      <div class="card"><b>{T("New to Greek coffee?", "Πρώτη φορά ελληνικό καφέ;")}</b>{T("Order it <i>sketos</i>, <i>metrios</i> or <i>glykos</i>.", "Σκέτος, μέτριος ή γλυκός.")} <a href="{url("")}#greek-coffee" style="border-bottom:1px solid var(--line)">{T("Read the guide →", "Δείτε τον οδηγό →")}</a></div>
    </aside>
  </div>
  <div class="actions" style="margin-top:56px"><a class="btn btn-solid" href="{url("visit")}">{T("Come and try it", "Ελάτε να το δοκιμάσετε")} {ARROW}</a><a class="btn btn-ghost" href="{url("photos")}">{T("More photos", "Περισσότερες φωτογραφίες")}</a></div>
</section>
'''
    write("menu", head("menu", title, desc, ld, og_img=img_abs("sig-sweet", 1200) if "sig-sweet" in PHOTOS else None) + body + foot())

# ================================================================ PHOTOS
CATS = {"street": ("The street", "Ο δρόμος"), "evening": ("Evening", "Βράδυ"), "taste": ("Coffee &amp; food", "Καφές &amp; φαγητό"), "plaka": ("Around Plaka", "Γύρω από την Πλάκα")}

def photos():
    title = T("Photos of Mnisikleous Street & Yiasemi Café, Plaka | More Photos",
              "Φωτογραφίες: Οδός Μνησικλέους & Γιασεμί, Πλάκα | Περισσότερες Φωτογραφίες")
    desc = T("More photos of Yiasemi's corner of Athens: the marble steps of Mnisikleous Street, Plaka at night, Greek coffee, pies and sweets, and the lanes below the Acropolis.",
             "Περισσότερες φωτογραφίες από τη γωνιά του Γιασεμιού: τα μαρμάρινα σκαλιά της Μνησικλέους, η Πλάκα τη νύχτα, ελληνικός καφές, πίτες, γλυκά και τα στενά κάτω από την Ακρόπολη.")
    gal_ids = [k for k, v in PHOTOS.items() if v.get("cat")]
    items, objs = "", []
    for i, k in enumerate(gal_ids):
        p = PHOTOS[k]
        cap = f'{esc(p["alt"][LANG])}<small>{T("Photo", "Φωτογραφία")}: {esc(p["author"])} · {esc(p["license"])}</small>'
        items += pic(k, "reveal", "c-stone", "(max-width: 760px) 46vw, (max-width: 960px) 30vw, 380px",
                     extra=f' data-cat="{p["cat"]}" data-delay="{(i % 3) * 70}"', cap=cap, full=True)
        objs.append({"@type": "ImageObject", "contentUrl": img_abs(k), "thumbnailUrl": img_abs(k, p["widths"][0]),
                     "name": p["alt"][LANG], "caption": p["alt"][LANG], "width": p["w"], "height": p["h"],
                     "creator": {"@type": "Person", "name": p["author"]}, "creditText": p["author"],
                     "license": p["licurl"], "acquireLicensePage": p["source"], "copyrightNotice": f'{p["author"]}, {p["license"]}'})
    fbtn = f'<button type="button" data-filter="all" aria-pressed="true">{T("All", "Όλες")}</button>' + "".join(
        f'<button type="button" data-filter="{k}" aria-pressed="false">{T(*v)}</button>' for k, v in CATS.items() if any(PHOTOS[g]["cat"] == k for g in gal_ids))
    ld = [website_ld(), cafe_ld(),
          {**webpage_ld("photos", title, desc, kind="CollectionPage"), "mainEntity": {"@type": "ImageGallery", "name": T("More photos", "Περισσότερες φωτογραφίες"), "associatedMedia": objs}},
          crumbs_ld([(T("Home", "Αρχική"), abs_url("")), (T("More photos", "Περισσότερες φωτογραφίες"), abs_url("photos"))])]
    body = f'''
<section class="wrap page-head">
  <p class="eyebrow reveal">{T("Gallery", "Γκαλερί")}</p>
  <h1 class="reveal" data-delay="80">{T("More photos", "Περισσότερες φωτογραφίες")}</h1>
  <p class="lead reveal" data-delay="160">{T("Our corner of Athens: the steps of Mnisikleous, Plaka after dark, and the simple Greek things we love to serve.", "Η γωνιά μας στην Αθήνα: τα σκαλιά της Μνησικλέους, η Πλάκα τη νύχτα και τα απλά ελληνικά πράγματα που αγαπάμε να σερβίρουμε.")}</p>
</section>
<section class="wrap" style="padding-top:8px">
  <div class="filters reveal" role="group" aria-label="{T("Filter photos", "Φίλτρο φωτογραφιών")}">{fbtn}</div>
  <div class="gallery">{items}</div>
  <p class="fine">{T("Photos are shared under Creative Commons licences.", "Οι φωτογραφίες διατίθενται με άδειες Creative Commons.")} <a href="{url("credits")}" style="border-bottom:1px solid var(--line)">{T("See all photo credits", "Όλες οι πηγές φωτογραφιών")}</a></p>
  <div class="actions" style="margin-top:40px"><a class="btn btn-solid" href="{url("visit")}">{T("See it in person", "Ελάτε από κοντά")} {ARROW}</a></div>
</section>
<div class="lightbox" role="dialog" aria-modal="true" aria-label="{T("Photo viewer", "Προβολή φωτογραφίας")}">
  <button class="lb-btn lb-close" type="button" aria-label="{T("Close", "Κλείσιμο")}">&times;</button>
  <button class="lb-btn lb-prev" type="button" aria-label="{T("Previous", "Προηγούμενη")}">←</button>
  <img alt="">
  <button class="lb-btn lb-next" type="button" aria-label="{T("Next", "Επόμενη")}">→</button>
</div>
'''
    write("photos", head("photos", title, desc, ld) + body + foot())

# ================================================================ VISIT
def visit():
    title = T("Visit Yiasemi | Mnisikleous 23, Plaka, Athens: Map, Metro & Directions",
              "Επίσκεψη στο Γιασεμί | Μνησικλέους 23, Πλάκα: Χάρτης, Μετρό & Οδηγίες")
    desc = T("How to find Yiasemi café at Mnisikleous 23, Plaka, Athens: map, phone, nearest metro (Monastiraki, ≈7 min walk) and nearby sights like the Roman Agora, Anafiotika and the Acropolis.",
             "Πώς θα βρείτε το Γιασεμί στη Μνησικλέους 23 στην Πλάκα: χάρτης, τηλέφωνο, πλησιέστερο μετρό (Μοναστηράκι, ≈7 λεπτά) και αξιοθέατα όπως η Ρωμαϊκή Αγορά, τα Αναφιώτικα και η Ακρόπολη.")
    metro = [(("Monastiraki", "Μοναστηράκι"), ("Lines 1 &amp; 3", "Γραμμές 1 &amp; 3"), "≈ 7 min"),
             (("Syntagma", "Σύνταγμα"), ("Lines 2 &amp; 3", "Γραμμές 2 &amp; 3"), "≈ 14 min"),
             (("Akropoli", "Ακρόπολη"), ("Line 2", "Γραμμή 2"), "≈ 15 min")]
    near = [(("Roman Agora", "Ρωμαϊκή Αγορά"), "≈ 3 min"), (("Anafiotika", "Αναφιώτικα"), "≈ 5 min"),
            (("Monastiraki Square", "Πλατεία Μοναστηρακίου"), "≈ 7 min"), (("Acropolis entrance", "Είσοδος Ακρόπολης"), "≈ 12 min"),
            (("Acropolis Museum", "Μουσείο Ακρόπολης"), "≈ 15 min")]
    mn = lambda m: m.replace("min", T("min", "λεπτά"))
    mlis = "".join(f'<li><span>{T(*a)}<small>{T(*b)}</small></span><span>{mn(m)}</span></li>' for a, b, m in metro)
    nlis = "".join(f'<li><span>{T(*a)}</span><span>{mn(m)}</span></li>' for a, m in near)
    ld = [website_ld(), cafe_ld(), webpage_ld("visit", title, desc, kind="ContactPage"),
          crumbs_ld([(T("Home", "Αρχική"), abs_url("")), (T("Visit", "Επίσκεψη"), abs_url("visit"))])]
    body = f'''
<section class="wrap page-head">
  <p class="eyebrow reveal">{T("Visit", "Επίσκεψη")}</p>
  <h1 class="reveal" data-delay="80">{T("Come up the steps<br>of Mnisikleous.", "Ανεβείτε τα σκαλιά<br>της Μνησικλέους.")}</h1>
  <p class="lead reveal" data-delay="160">{T("In the heart of Plaka, on the stepped street that climbs toward the Acropolis. Look for the cushions on the stairs, then find a spot and settle in.", "Στην καρδιά της Πλάκας, στο σκαλωτό στενό που ανεβαίνει προς την Ακρόπολη. Ψάξτε τα μαξιλάρια στα σκαλιά, βρείτε θέση και χαλαρώστε.")}</p>
</section>
<section class="wrap" style="padding-top:8px">
  <div class="location">
    <div class="info reveal">{info_dl()}
      <div class="actions"><a class="btn btn-solid" href="{GMAPS}" target="_blank" rel="noopener">{T("Get directions", "Οδηγίες")} {ARROW}</a><a class="btn btn-ghost" href="tel:{PHONE}">{T("Call us", "Καλέστε μας")}</a></div>
    </div>
    {map_iframe()}
  </div>
</section>
<section class="wrap" style="padding-top:0">
  <div class="meander" aria-hidden="true" style="margin-bottom:80px"></div>
  <div class="cols">
    <div class="reveal">
      <p class="eyebrow">{T("By metro", "Με το μετρό")}</p>
      <h2 style="margin-bottom:24px">{T("Getting here", "Πώς θα έρθετε")}</h2>
      <ul class="walk">{mlis}</ul>
    </div>
    <div class="reveal" data-delay="120">
      <p class="eyebrow">{T("On foot", "Με τα πόδια")}</p>
      <h2 style="margin-bottom:24px">{T("Nearby", "Κοντά μας")}</h2>
      <ul class="walk">{nlis}</ul>
    </div>
  </div>
  <p class="fine">{T("Walking times are approximate. Mnisikleous is a pedestrian street with steps; cars can't reach the door.", "Οι χρόνοι είναι κατά προσέγγιση. Η Μνησικλέους είναι πεζόδρομος με σκαλιά· τα αυτοκίνητα δεν φτάνουν ως την πόρτα.")}</p>
</section>
<section class="wrap" style="padding-top:0">
  <div class="about">
    {pic("evening-1", "reveal", "c-sea", "(max-width: 960px) 92vw, 500px")}
    <div class="reveal" data-delay="120">
      <p class="eyebrow">{T("After dark", "Το βράδυ")}</p>
      <h2>{T("Plaka is at its best in the evening.", "Η Πλάκα είναι στα καλύτερά της το βράδυ.")}</h2>
      <p class="muted" style="margin-top:20px">{T("When the day-trippers leave, the lights come on along the steps and the air smells of jasmine. Stay for a rakomelo.", "Όταν φεύγει ο κόσμος της ημέρας, τα φώτα ανάβουν στα σκαλιά και ο αέρας μυρίζει γιασεμί. Μείνετε για ένα ρακόμελο.")}</p>
    </div>
  </div>
</section>
'''
    write("visit", head("visit", title, desc, ld) + body + foot())

# ================================================================ CREDITS
def credits():
    title = T("Photo credits | Yiasemi", "Πηγές φωτογραφιών | Γιασεμί")
    desc = T("Credits and licences for the photographs used on the Yiasemi website.", "Πηγές και άδειες των φωτογραφιών του ιστότοπου.")
    lis = ""
    for k, p in PHOTOS.items():
        lis += (f'<li><img src="/images/{p["base"]}-{p["widths"][0]}.jpg" alt="" loading="lazy" width="96" height="72">'
                f'<div><b>{esc(p["alt"][LANG])}</b><br><span class="muted">{T("Photo", "Φωτογραφία")}: {esc(p["author"])} · '
                f'<a href="{esc(p["licurl"])}" target="_blank" rel="noopener license">{esc(p["license"])}</a> · '
                f'<a href="{esc(p["source"])}" target="_blank" rel="noopener">Wikimedia Commons</a> · {T("resized and cropped", "αλλαγή μεγέθους και περικοπή")}</span></div></li>')
    ld = [website_ld(), webpage_ld("credits", title, desc), crumbs_ld([(T("Home", "Αρχική"), abs_url("")), (T("Photo credits", "Πηγές φωτογραφιών"), abs_url("credits"))])]
    body = f'''
<section class="wrap page-head">
  <p class="eyebrow">{T("Thank you", "Ευχαριστούμε")}</p>
  <h1>{T("Photo credits", "Πηγές φωτογραφιών")}</h1>
  <p class="lead">{T("These photographs come from Wikimedia Commons and are used under their Creative Commons licences. Our resized and cropped versions are shared under the same licences.", "Οι φωτογραφίες προέρχονται από το Wikimedia Commons και χρησιμοποιούνται σύμφωνα με τις άδειες Creative Commons. Οι εκδόσεις μας διατίθενται με τις ίδιες άδειες.")}</p>
</section>
<section class="wrap" style="padding-top:0"><ul class="credits">{lis}</ul></section>
'''
    write("credits", head("credits", title, desc, ld, noindex=True) + body + foot())

# ================================================================ 404
def notfound():
    global LANG
    LANG = "en"
    body = f'''
<section class="wrap page-head" style="text-align:center;padding:120px 0">
  {jasmine(style="width:56px;height:56px;color:var(--clay);margin:0 auto 24px;display:block")}
  <h1>Lost on the steps?</h1>
  <p lang="el" class="lead" style="margin:18px auto 0">Χαθήκατε στα σκαλιά; Αυτή η σελίδα δεν υπάρχει.</p>
  <p class="lead" style="margin:8px auto 0">This page doesn't exist, but the coffee does.</p>
  <div class="actions" style="justify-content:center"><a class="btn btn-solid" href="/">Home {ARROW}</a><a class="btn btn-ghost" href="/el/" lang="el">Αρχική</a></div>
</section>
'''
    (OUT / "404.html").write_text(head("404", "Page not found | Yiasemi", "This page could not be found.", [website_ld()], noindex=True) + body + foot(), encoding="utf-8")

# ================================================================ sitemap, robots, manifest
def sitemap():
    pages = [("", "1.0", "weekly"), ("menu", "0.9", "monthly"), ("visit", "0.9", "monthly"), ("photos", "0.7", "monthly")]
    rows = []
    for path, pri, freq in pages:
        for lang in ("en", "el"):
            alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{abs_url(path, l)}"/>' for h, l in (("en", "en"), ("el", "el"), ("x-default", "en")))
            imgs = ""
            if path == "photos":
                imgs = "".join(f'\n    <image:image><image:loc>{img_abs(k)}</image:loc></image:image>' for k, v in PHOTOS.items() if v.get("cat"))
            elif path == "" and "hero" in PHOTOS:
                imgs = f'\n    <image:image><image:loc>{img_abs("hero")}</image:loc></image:image>'
            rows.append(f'  <url>\n    <loc>{abs_url(path, lang)}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>{alts}{imgs}\n  </url>')
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    (OUT / "manifest.webmanifest").write_text(json.dumps({
        "name": "Yiasemi · Γιασεμί", "short_name": "Yiasemi", "description": "Café on the steps of Mnisikleous, Plaka, Athens",
        "start_url": "/", "display": "standalone", "background_color": "#f6f0e6", "theme_color": "#5e6e45", "lang": "en",
        "icons": [{"src": "/images/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/images/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "/images/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    for LANG in ("en", "el"):
        home(); menu(); photos(); visit(); credits()
    notfound()
    sitemap()
    print("built", len(PHOTOS), "photos")
