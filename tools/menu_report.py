#!/usr/bin/env python3
"""Write docs/menu-approval.csv: every menu item as shown on the site, for the owner to approve.

    python3 tools/menu_report.py
Columns 'approved' and 'correction' are for the owner. Rows with a 'needs_check' note were
flagged during transcription of the official menu (yiasemi.gr/menu).
"""
import csv, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sitegen.core import fmt_price  # noqa: E402

menu = json.loads((ROOT / "content/menu.json").read_text(encoding="utf-8"))
out = ROOT / "docs/menu-approval.csv"
flagged = 0
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "section", "name (EN)", "όνομα (EL)", "description (EN)", "περιγραφή (EL)", "price as shown", "dietary label shown", "needs_check", "approved (Y/N)", "correction"])
    for s in menu["sections"]:
        for it in s["items"]:
            price = " / ".join(f'{p["label"]["en"]} {fmt_price(p["price"], "en")}' for p in it["prices"]) if "prices" in it else fmt_price(it["price"], "en")
            note = it.get("verify", "")
            flagged += bool(note)
            w.writerow([it["id"], s["name"]["en"], it["name"]["en"], it["name"]["el"], (it.get("desc") or {}).get("en", ""), (it.get("desc") or {}).get("el", ""),
                        price, it.get("diet") or "-", note, "", ""])
print(f"wrote {out} ({flagged} items flagged)")
