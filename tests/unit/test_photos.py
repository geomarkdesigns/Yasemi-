import json, pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import images  # noqa: E402
from PIL import Image  # noqa: E402


class SlotCaptions(unittest.TestCase):
    def setUp(self):
        self._photos, self._lang = build.PHOTOS, build.LANG

    def tearDown(self):
        build.PHOTOS, build.LANG = self._photos, self._lang

    def test_generic_photo_is_never_labelled_as_yiasemi(self):
        for lang in ("en", "el"):
            build.LANG = lang
            for pid in ("hero", "about", "sig-coffee", "sig-sweet", "sig-pie"):
                cap = build.slot_cap(pid, "Generic", "Γενική")
                self.assertNotIn("At Yiasemi", cap); self.assertNotIn("Στο Γιασεμί", cap); self.assertNotIn("© Yiasemi", cap)
                self.assertIn(build.PHOTOS[pid]["author"], cap)          # licence attribution shown

    def test_owner_photo_is_labelled_and_credited(self):
        build.PHOTOS = dict(build.PHOTOS)
        build.PHOTOS["hero"] = {**build.PHOTOS["hero"], "origin": "yiasemi", "author": "Yiasemi", "license": "© Yiasemi"}
        build.LANG = "el"
        cap = build.slot_cap("hero", "Οδός", "Οδός")
        self.assertIn("Στο Γιασεμί", cap); self.assertIn("© Yiasemi", cap)
        build.PHOTOS["hero"]["caption"] = {"en": "Our terrace", "el": "Η ταράτσα μας"}
        self.assertIn("Η ταράτσα μας", build.slot_cap("hero", "x", "x"))

    def test_every_current_photo_is_licensed_and_attributed(self):
        cfg = json.loads((ROOT / "tools/photos.config.json").read_text(encoding="utf-8"))
        for c in cfg:
            self.assertEqual(c["origin"], "licensed", c["id"])
            self.assertTrue(c["author"] and c["license"] and c["licurl"].startswith("https://creativecommons.org/") and c["source"].startswith("https://commons.wikimedia.org/"), c["id"])


class SlotAspect(unittest.TestCase):
    def test_owner_photo_is_cropped_to_the_slot_shape(self):
        landscape = Image.new("RGB", (4000, 2000))
        for slot, ratio in images.SLOT_ASPECT.items():
            w, h = map(int, ratio.split(":"))
            out = images.crop(landscape, images.SLOT_ASPECT.get(slot), None)
            self.assertAlmostEqual(out.width / out.height, w / h, places=2, msg=slot)


if __name__ == "__main__":
    unittest.main()
