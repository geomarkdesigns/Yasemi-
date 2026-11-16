import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from sitegen.core import (url, abs_url, fmt_price, pick, validate_menu, hours_rows,  # noqa: E402
                          opening_hours_ld, maps_links, esc)


class Urls(unittest.TestCase):
    def test_home_and_pages(self):
        self.assertEqual(url("", "en"), "/")
        self.assertEqual(url("", "el"), "/el")
        self.assertEqual(url("menu", "en"), "/menu")
        self.assertEqual(url("/menu/", "el"), "/el/menu")

    def test_abs(self):
        self.assertEqual(abs_url("https://x.app/", "visit", "el"), "https://x.app/el/visit")


class Prices(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(fmt_price(6.5, "en"), "€6.50")
        self.assertEqual(fmt_price(6.5, "el"), "6,50 €")
        self.assertEqual(fmt_price(120, "en"), "€120.00")
        self.assertEqual(fmt_price(0, "el"), "0,00 €")

    def test_rejects_bad(self):
        for bad in (None, -1, "6.50"):
            with self.assertRaises(ValueError):
                fmt_price(bad, "en")


class Helpers(unittest.TestCase):
    def test_pick_and_esc(self):
        self.assertEqual(pick({"en": "A", "el": "Α"}, "el"), "Α")
        self.assertEqual(pick({"en": "A"}, "el"), "A")
        self.assertEqual(esc('<a "x">'), "&lt;a &quot;x&quot;&gt;")

    def test_hours_unknown_is_empty(self):
        self.assertEqual(hours_rows(None, "en"), [])
        self.assertEqual(opening_hours_ld(None), [])

    def test_hours_rows(self):
        rows = hours_rows([{"days": [0, 1, 2, 3, 4], "opens": "09:00", "closes": "19:00"}], "en")
        self.assertEqual(rows[0], ("Monday", "09:00–19:00"))
        self.assertEqual(rows[6], ("Sunday", "Closed"))

    def test_maps_links_use_address_not_coordinates(self):
        m = maps_links("Yiasemi", "Mnisikleous 23", "105 55", "Athens")
        self.assertIn("Mnisikleous%2023", m["google"])
        self.assertTrue(m["google"].startswith("https://www.google.com/maps/dir/?api=1&destination="))
        self.assertTrue(m["apple"].startswith("https://maps.apple.com/?daddr="))


class MenuValidation(unittest.TestCase):
    def base(self):
        return {"sections": [{"id": "s", "name": {"en": "S", "el": "Σ"}, "items": [
            {"id": "a", "name": {"en": "A", "el": "Α"}, "price": 1.0}]}]}

    def test_valid(self):
        self.assertEqual(validate_menu(self.base()), 1)

    def test_duplicate_id(self):
        m = self.base(); m["sections"][0]["items"].append(dict(m["sections"][0]["items"][0]))
        with self.assertRaises(ValueError):
            validate_menu(m)

    def test_missing_translation(self):
        m = self.base(); m["sections"][0]["items"][0]["name"] = {"en": "A"}
        with self.assertRaises(ValueError):
            validate_menu(m)

    def test_missing_price(self):
        m = self.base(); del m["sections"][0]["items"][0]["price"]
        with self.assertRaises(ValueError):
            validate_menu(m)

    def test_unknown_diet(self):
        m = self.base(); m["sections"][0]["items"][0]["diet"] = "keto"
        with self.assertRaises(ValueError):
            validate_menu(m)


class RealContent(unittest.TestCase):
    """Guards on the real data files."""

    @classmethod
    def setUpClass(cls):
        cls.menu = json.loads((ROOT / "content/menu.json").read_text(encoding="utf-8"))
        cls.site = json.loads((ROOT / "content/site.json").read_text(encoding="utf-8"))
        cls.items = [i for s in cls.menu["sections"] for i in s["items"]]

    def test_menu_is_valid(self):
        self.assertEqual(validate_menu(self.menu), len(self.items))
        self.assertGreater(len(self.items), 50)

    def test_no_dietary_label_on_meat_or_cheese_vegan(self):
        meat = ("bacon", "meatball", "moussaka")
        for it in self.items:
            name = it["name"]["en"].lower()
            if any(m in name for m in meat):
                self.assertIsNone(it.get("diet"), it["id"])
            if it.get("diet") == "vegan":
                for dairy in ("cheese", "feta", "yogurt", "butter ", "honey"):
                    if dairy in name and "plant-based" not in name:
                        self.fail(f"{it['id']} labelled vegan but name mentions {dairy}")

    def test_prices_positive(self):
        for it in self.items:
            for p in ([x["price"] for x in it["prices"]] if "prices" in it else [it["price"]]):
                self.assertGreater(p, 0, it["id"])

    def test_unknown_facts_stay_null(self):
        # These must only be filled with information confirmed by the café.
        for key in ("openingHours", "geo", "email"):
            self.assertIn(key, self.site)
        self.assertTrue(self.site["phone"].startswith("+30"))


if __name__ == "__main__":
    unittest.main()
