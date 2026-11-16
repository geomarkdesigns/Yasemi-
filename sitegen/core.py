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


# The 14 allergens of EU Regulation 1169/2011, Annex II (order as in the regulation).
ALLERGENS = {
    "gluten":      {"en": "Cereals containing gluten", "el": "Δημητριακά που περιέχουν γλουτένη"},
    "crustaceans": {"en": "Crustaceans", "el": "Καρκινοειδή"},
    "eggs":        {"en": "Eggs", "el": "Αυγά"},
    "fish":        {"en": "Fish", "el": "Ψάρια"},
    "peanuts":     {"en": "Peanuts", "el": "Αράπικα φιστίκια"},
    "soy":         {"en": "Soybeans", "el": "Σόγια"},
    "milk":        {"en": "Milk (incl. lactose)", "el": "Γάλα (και λακτόζη)"},
    "nuts":        {"en": "Tree nuts", "el": "Καρποί με κέλυφος"},
    "celery":      {"en": "Celery", "el": "Σέλινο"},
    "mustard":     {"en": "Mustard", "el": "Μουστάρδα"},
    "sesame":      {"en": "Sesame seeds", "el": "Σουσάμι"},
    "sulphites":   {"en": "Sulphur dioxide & sulphites", "el": "Διοξείδιο του θείου & θειώδη"},
    "lupin":       {"en": "Lupin", "el": "Λούπινο"},
    "molluscs":    {"en": "Molluscs", "el": "Μαλάκια"},
}


def validate_allergens(value, item_id="item"):
    """None = not yet confirmed by the kitchen (nothing is shown or implied).
    A list = the kitchen's confirmed declaration; [] means it contains none of the 14."""
    if value is None:
        return None
    if not isinstance(value, list):
        raise ValueError(f"{item_id}: allergens must be null or a list")
    unknown = [a for a in value if a not in ALLERGENS]
    if unknown:
        raise ValueError(f"{item_id}: unknown allergen code(s) {unknown}")
    if len(set(value)) != len(value):
        raise ValueError(f"{item_id}: duplicate allergen codes")
    return [a for a in ALLERGENS if a in value]          # canonical order


def allergen_text(value, lang):
    """Human text for a confirmed declaration, or None when unconfirmed."""
    v = validate_allergens(value)
    if v is None:
        return None
    if not v:
        return {"en": "Contains none of the 14 major allergens", "el": "Δεν περιέχει κανένα από τα 14 κύρια αλλεργιογόνα"}[lang]
    return {"en": "Contains: ", "el": "Περιέχει: "}[lang] + ", ".join(ALLERGENS[a][lang] for a in v)


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
            validate_allergens(it.get("allergens"), iid)
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


# ------------------------------------------------------------------ opening hours
# site.json "hours":
#   weekly:  [{"days":[0..6], "opens":"09:00", "closes":"19:00"}]            (0 = Monday) or null = unknown
#   seasons: [{"name":{en,el}, "from":"MM-DD", "to":"MM-DD", "weekly":[...]}] (may wrap the year end)
#   special: [{"date":"YYYY-MM-DD", "closed":true, "note":{en,el}}  or  {"date":..., "opens":..., "closes":..., "note":...}]
#   notice:  null or {"en":..., "el":..., "until":"YYYY-MM-DD"}            (temporary message)
import datetime as _dt
import re as _re

_TIME = _re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
DAY_NAMES = {"en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
             "el": ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]}
SCHEMA_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _check_spans(spans, where):
    if spans is None:
        return
    if not isinstance(spans, list):
        raise ValueError(f"{where}: must be a list")
    for s in spans:
        if not s.get("days") or any(d not in range(7) for d in s["days"]):
            raise ValueError(f"{where}: days must be 0-6 (Mon-Sun)")
        for k in ("opens", "closes"):
            if not _TIME.match(str(s.get(k, ""))):
                raise ValueError(f"{where}: {k} must be HH:MM")


def validate_hours(h):
    """Validate the hours block; returns it normalised (missing keys filled)."""
    h = dict(h or {})
    h.setdefault("weekly", None); h.setdefault("seasons", []); h.setdefault("special", []); h.setdefault("notice", None)
    _check_spans(h["weekly"], "hours.weekly")
    for s in h["seasons"]:
        for k in ("from", "to"):
            _dt.datetime.strptime("2000-" + s[k], "%Y-%m-%d")
        _check_spans(s["weekly"], f"season {s['from']}..{s['to']}")
    for sp in h["special"]:
        _dt.date.fromisoformat(sp["date"])
        if not sp.get("closed"):
            _check_spans([{"days": [0], "opens": sp.get("opens"), "closes": sp.get("closes")}], f"special {sp['date']}")
    if h["notice"] and h["notice"].get("until"):
        _dt.date.fromisoformat(h["notice"]["until"])
    return h


def has_hours(h):
    h = validate_hours(h)
    return bool(h["weekly"] or h["seasons"])


def _in_season(season, d):
    md = d.strftime("%m-%d")
    a, b = season["from"], season["to"]
    return a <= md <= b if a <= b else (md >= a or md <= b)      # wraps the new year


def weekly_for(h, d):
    h = validate_hours(h)
    for s in h["seasons"]:
        if _in_season(s, d):
            return s["weekly"]
    return h["weekly"]


def hours_on(h, d):
    """('closed', note) | ('open', ['09:00–19:00', ...], note) | ('unknown', None) for a date."""
    h = validate_hours(h)
    for sp in h["special"]:
        if sp["date"] == d.isoformat():
            note = sp.get("note")
            return ("closed", note) if sp.get("closed") else ("open", [f'{sp["opens"]}–{sp["closes"]}'], note)
    w = weekly_for(h, d)
    if w is None:
        return ("unknown", None)
    spans = [f'{s["opens"]}–{s["closes"]}' for s in w if d.weekday() in s["days"]]
    return ("open", spans, None) if spans else ("closed", None)


def week_rows(spans, lang):
    closed = {"en": "Closed", "el": "Κλειστά"}[lang]
    return [(DAY_NAMES[lang][d], ", ".join(f'{s["opens"]}–{s["closes"]}' for s in spans if d in s["days"]) or closed) for d in range(7)]


def hours_ld_full(h, today):
    """schema.org OpeningHoursSpecification incl. seasonal validity and special days (next 12 months)."""
    h = validate_hours(h)
    out = [{"@type": "OpeningHoursSpecification", "dayOfWeek": [SCHEMA_DAYS[d] for d in s["days"]], "opens": s["opens"], "closes": s["closes"]}
           for s in (h["weekly"] or [])]
    for season in h["seasons"]:
        for year in (today.year, today.year + 1):
            start = _dt.date.fromisoformat(f"{year}-{season['from']}")
            end = _dt.date.fromisoformat(f"{year if season['from'] <= season['to'] else year + 1}-{season['to']}")
            if end < today:
                continue
            out += [{"@type": "OpeningHoursSpecification", "dayOfWeek": [SCHEMA_DAYS[d] for d in s["days"]], "opens": s["opens"], "closes": s["closes"],
                     "validFrom": start.isoformat(), "validThrough": end.isoformat()} for s in season["weekly"]]
    for sp in h["special"]:
        d = _dt.date.fromisoformat(sp["date"])
        if today <= d <= today + _dt.timedelta(days=366):
            o, c = ("00:00", "00:00") if sp.get("closed") else (sp["opens"], sp["closes"])
            out.append({"@type": "OpeningHoursSpecification", "opens": o, "closes": c, "validFrom": sp["date"], "validThrough": sp["date"]})
    return out


# ------------------------------------------------------------------ gallery
def gallery_order(photos):
    """Authentic Yiasemi photos first (in config order), then licensed photos."""
    ids = [k for k, v in photos.items() if v.get("cat")]
    return [k for k in ids if photos[k].get("origin") == "yiasemi"] + [k for k in ids if photos[k].get("origin") != "yiasemi"]
