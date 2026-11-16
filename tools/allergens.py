#!/usr/bin/env python3
"""Allergen declarations: export a form for the kitchen, import the completed form.

    python3 tools/allergens.py export            # writes docs/allergen-form.csv
    python3 tools/allergens.py import FILE.csv   # updates content/menu.json

Rules (nothing is ever inferred from a dish name):
  * A row left completely blank keeps that dish as "not confirmed" (allergens: null).
  * A row that is filled in must have Y or N in ALL 14 columns, otherwise the
    import stops and lists the problem rows. A partial answer is not accepted.
"""
import csv, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sitegen.core import ALLERGENS, validate_menu  # noqa: E402

MENU_PATH = ROOT / "content/menu.json"
FORM = ROOT / "docs/allergen-form.csv"
YES, NO = {"y", "yes", "ναι", "ν", "x", "1"}, {"n", "no", "οχι", "όχι", "ο", "0"}


def export(path=FORM):
    menu = json.loads(MENU_PATH.read_text(encoding="utf-8"))
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "section", "dish (EN)", "πιάτο (EL)"] + [f'{c} | {v["en"]} | {v["el"]}' for c, v in ALLERGENS.items()])
        for sec in menu["sections"]:
            for it in sec["items"]:
                cur = it.get("allergens")
                cells = [""] * len(ALLERGENS) if cur is None else ["Y" if c in cur else "N" for c in ALLERGENS]
                w.writerow([it["id"], sec["name"]["en"], it["name"]["en"], it["name"]["el"]] + cells)
    return path


def parse(rows):
    """rows: iterable of dicts from the CSV. Returns {id: list|None} and a list of errors."""
    codes = list(ALLERGENS)
    result, errors = {}, []
    for n, row in enumerate(rows, start=2):
        iid = (row.get("id") or "").strip()
        if not iid:
            continue
        vals = []
        for c in codes:
            key = next((k for k in row if k and k.split("|")[0].strip() == c), None)
            vals.append((row.get(key) or "").strip().lower() if key else "")
        if all(v == "" for v in vals):
            result[iid] = None
            continue
        bad = [codes[i] for i, v in enumerate(vals) if v not in YES | NO]
        if bad:
            errors.append(f"row {n} ({iid}): answer Y or N for every allergen; missing/unclear: {', '.join(bad)}")
            continue
        result[iid] = [codes[i] for i, v in enumerate(vals) if v in YES]
    return result, errors


def import_csv(path):
    menu = json.loads(MENU_PATH.read_text(encoding="utf-8"))
    with open(path, newline="", encoding="utf-8-sig") as f:
        data, errors = parse(csv.DictReader(f))
    known = {i["id"] for s in menu["sections"] for i in s["items"]}
    errors += [f"unknown dish id: {i}" for i in data if i not in known]
    if errors:
        raise SystemExit("Import stopped, nothing changed:\n  " + "\n  ".join(errors))
    changed = 0
    for s in menu["sections"]:
        for it in s["items"]:
            if it["id"] in data and data[it["id"]] != it.get("allergens"):
                it["allergens"] = data[it["id"]]; changed += 1
    validate_menu(menu)
    MENU_PATH.write_text(json.dumps(menu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    confirmed = sum(1 for s in menu["sections"] for i in s["items"] if i.get("allergens") is not None)
    print(f"updated {changed} dishes; {confirmed} of {len(known)} now have a confirmed declaration")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "export":
        print("wrote", export())
    elif len(sys.argv) == 3 and sys.argv[1] == "import":
        import_csv(sys.argv[2])
    else:
        sys.exit(__doc__)
