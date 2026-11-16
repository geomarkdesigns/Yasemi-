import pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))
from sitegen.core import ALLERGENS, validate_allergens, allergen_text, validate_menu  # noqa: E402
import allergens as tool  # noqa: E402


class Model(unittest.TestCase):
    def test_fourteen_eu_allergens_bilingual(self):
        self.assertEqual(len(ALLERGENS), 14)
        for v in ALLERGENS.values():
            self.assertTrue(v["en"] and v["el"])

    def test_unconfirmed_shows_nothing(self):
        self.assertIsNone(validate_allergens(None))
        self.assertIsNone(allergen_text(None, "en"))

    def test_confirmed_none_vs_some(self):
        self.assertEqual(allergen_text([], "en"), "Contains none of the 14 major allergens")
        self.assertEqual(allergen_text(["milk", "gluten"], "en"), "Contains: Cereals containing gluten, Milk (incl. lactose)")
        self.assertTrue(allergen_text(["eggs"], "el").startswith("Περιέχει: Αυγά"))

    def test_rejects_bad_values(self):
        for bad in ("milk", ["milk", "milk"], ["pollen"]):
            with self.assertRaises(ValueError):
                validate_allergens(bad)

    def test_menu_validation_checks_allergens(self):
        m = {"sections": [{"id": "s", "name": {"en": "S", "el": "Σ"}, "items": [
            {"id": "a", "name": {"en": "A", "el": "Α"}, "price": 1.0, "allergens": ["shellfish"]}]}]}
        with self.assertRaises(ValueError):
            validate_menu(m)


class Import(unittest.TestCase):
    def row(self, iid, values):
        r = {"id": iid}
        for c, v in zip(ALLERGENS, values):
            r[f"{c} | x | y"] = v
        return r

    def test_blank_row_stays_unconfirmed(self):
        data, errors = tool.parse([self.row("a", [""] * 14)])
        self.assertEqual((data, errors), ({"a": None}, []))

    def test_complete_row_imports(self):
        vals = ["N"] * 14; vals[0] = "Y"; vals[6] = "ναι"
        data, errors = tool.parse([self.row("a", vals)])
        self.assertEqual(errors, []); self.assertEqual(data["a"], ["gluten", "milk"])

    def test_partial_row_is_rejected_not_guessed(self):
        vals = [""] * 14; vals[0] = "Y"
        data, errors = tool.parse([self.row("a", vals)])
        self.assertNotIn("a", data); self.assertEqual(len(errors), 1)

    def test_real_menu_has_no_inferred_allergens(self):
        import json
        menu = json.loads((ROOT / "content/menu.json").read_text(encoding="utf-8"))
        # Until the kitchen returns the form, every dish must be "not confirmed".
        self.assertTrue(all(i.get("allergens") is None for s in menu["sections"] for i in s["items"]))


if __name__ == "__main__":
    unittest.main()
