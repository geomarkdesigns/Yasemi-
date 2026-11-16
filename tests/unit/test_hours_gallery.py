import datetime as dt, json, pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from sitegen.core import validate_hours, has_hours, hours_on, weekly_for, week_rows, hours_ld_full, gallery_order  # noqa: E402

H = {"weekly": [{"days": [0, 1, 2, 3, 4], "opens": "09:00", "closes": "19:00"}, {"days": [5, 6], "opens": "10:00", "closes": "23:00"}],
     "seasons": [{"name": {"en": "Winter", "el": "Χειμώνας"}, "from": "11-01", "to": "03-31",
                  "weekly": [{"days": [0, 1, 2, 3, 4, 5, 6], "opens": "10:00", "closes": "18:00"}]}],
     "special": [{"date": "2026-12-25", "closed": True, "note": {"en": "Christmas", "el": "Χριστούγεννα"}},
                 {"date": "2027-01-01", "opens": "12:00", "closes": "16:00"}]}


class Hours(unittest.TestCase):
    def test_unknown_by_default(self):
        self.assertFalse(has_hours(None))
        self.assertEqual(hours_on(None, dt.date(2026, 6, 1)), ("unknown", None))

    def test_real_site_has_no_invented_hours(self):
        site = json.loads((ROOT / "content/site.json").read_text(encoding="utf-8"))
        self.assertFalse(has_hours(site["hours"]))

    def test_weekly_and_weekend(self):
        self.assertEqual(hours_on(H, dt.date(2026, 6, 1))[:2], ("open", ["09:00–19:00"]))   # Monday
        self.assertEqual(hours_on(H, dt.date(2026, 6, 6))[:2], ("open", ["10:00–23:00"]))   # Saturday

    def test_season_wraps_new_year(self):
        self.assertEqual(weekly_for(H, dt.date(2027, 2, 10)), H["seasons"][0]["weekly"])
        self.assertEqual(weekly_for(H, dt.date(2026, 11, 1)), H["seasons"][0]["weekly"])
        self.assertEqual(weekly_for(H, dt.date(2026, 4, 1)), H["weekly"])

    def test_special_dates_override(self):
        self.assertEqual(hours_on(H, dt.date(2026, 12, 25))[0], "closed")
        self.assertEqual(hours_on(H, dt.date(2027, 1, 1))[:2], ("open", ["12:00–16:00"]))

    def test_week_rows_mark_closed_days(self):
        rows = week_rows([{"days": [0], "opens": "09:00", "closes": "17:00"}], "el")
        self.assertEqual(rows[0], ("Δευτέρα", "09:00–17:00")); self.assertEqual(rows[6], ("Κυριακή", "Κλειστά"))

    def test_schema_includes_seasons_and_specials(self):
        ld = hours_ld_full(H, dt.date(2026, 11, 16))
        self.assertTrue(any(x.get("validFrom") == "2026-12-25" and x["opens"] == "00:00" for x in ld))
        self.assertTrue(any(x.get("validFrom") == "2026-11-01" and x.get("validThrough") == "2027-03-31" for x in ld))

    def test_rejects_bad_data(self):
        for bad in ({"weekly": [{"days": [7], "opens": "09:00", "closes": "19:00"}]},
                    {"weekly": [{"days": [0], "opens": "9am", "closes": "19:00"}]},
                    {"special": [{"date": "2026-13-01", "closed": True}]}):
            with self.assertRaises(ValueError):
                validate_hours(bad)


class Gallery(unittest.TestCase):
    def test_authentic_photos_first(self):
        photos = {"a": {"cat": "street", "origin": "licensed"}, "b": {"cat": "taste", "origin": "yiasemi"},
                  "c": {"cat": None}, "d": {"cat": "street", "origin": "yiasemi"}}
        self.assertEqual(gallery_order(photos), ["b", "d", "a"])


if __name__ == "__main__":
    unittest.main()
