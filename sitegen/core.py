"""Pure, unit-tested helpers used by build.py (no file I/O here)."""
import html
import re

LANGS = ("en", "el")


def esc(s):
    """HTML-escape text for element content and attribute values."""
    return html.escape("" if s is None else str(s), quote=True)


def pick(value, lang):
    """Return the string for `lang` from a {"en":..,"el":..} dict, or the value itself."""
    if isinstance(value, dict):
        return value.get(lang) or value.get("en") or ""
    return "" if value is None else value


def url(path, lang):
    """Clean, root-relative URL for a page path in a language. '' is the home page."""
    p = path.strip("/")
    pre = "/el" if lang == "el" else ""
    return f"{pre}/{p}" if p else (pre or "/")


def abs_url(base, path, lang):
    return base.rstrip("/") + url(path, lang)


def fmt_price(amount, lang):
    """Format a EUR amount the way each language expects: en '€6.50', el '6,50 €'."""
    if amount is None:
        raise ValueError("price missing")
    if not isinstance(amount, (int, float)) or amount < 0:
        raise ValueError(f"invalid price: {amount!r}")
    s = f"{amount:.2f}"
    return f"{s.replace('.', ',')} €" if lang == "el" else f"€{s}"


def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "item"


DIETS = {
    "vegetarian": {"en": "Vegetarian", "el": "Χορτοφαγικό", "short": "V"},
    "vegan": {"en": "Vegan", "el": "Vegan", "short": "VG"},
}


def validate_menu(menu):
    """Raise ValueError if the menu data is malformed. Returns item count."""
    seen, count = set(), 0
    if not menu.get("sections"):
        raise ValueError("menu has no sections")
    for sec in menu["sections"]:
        for k in ("id", "name", "items"):
            if k not in sec:
                raise ValueError(f"section missing {k}")
        for lang in LANGS:
            if not pick(sec["name"], lang):
                raise ValueError(f"section {sec['id']} missing {lang} name")
        for it in sec["items"]:
            iid = it.get("id")
            if not iid or iid in seen:
                raise ValueError(f"missing or duplicate item id: {iid}")
            seen.add(iid)
            for lang in LANGS:
                if not (isinstance(it.get("name"), dict) and it["name"].get(lang)):
                    raise ValueError(f"item {iid} missing {lang} name")
            if "prices" in it:
                if not it["prices"]:
                    raise ValueError(f"item {iid} has empty prices")
                for p in it["prices"]:
                    fmt_price(p["price"], "en")
            else:
                fmt_price(it.get("price"), "en")
            if it.get("diet") not in (None, "vegetarian", "vegan"):
                raise ValueError(f"item {iid} has unknown diet {it.get('diet')}")
            count += 1
    return count


def hours_rows(opening_hours, lang):
    """opening_hours: list of {"days":[0..6], "opens":"09:00", "closes":"19:00"} (0=Mon).
    Returns [(day label, 'HH:MM–HH:MM' or closed text)] for Mon..Sun, or [] if unknown."""
    if not opening_hours:
        return []
    names = {"en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
             "el": ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]}
    closed = {"en": "Closed", "el": "Κλειστά"}[lang]
    rows = []
    for d in range(7):
        spans = [f'{h["opens"]}–{h["closes"]}' for h in opening_hours if d in h["days"]]
        rows.append((names[lang][d], ", ".join(spans) if spans else closed))
    return rows


def opening_hours_ld(opening_hours):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return [{"@type": "OpeningHoursSpecification", "dayOfWeek": [days[d] for d in h["days"]],
             "opens": h["opens"], "closes": h["closes"]} for h in (opening_hours or [])]


def maps_links(name, street, postal, city):
    """Directions links that use the verified street address (no guessed coordinates)."""
    from urllib.parse import quote
    q = f"{name}, {street}, {postal} {city}, Greece"
    return {
        "google": "https://www.google.com/maps/dir/?api=1&destination=" + quote(q),
        "apple": "https://maps.apple.com/?daddr=" + quote(q) + "&dirflg=w",
        "embed": "https://www.google.com/maps?q=" + quote(q) + "&z=17&output=embed",
    }
