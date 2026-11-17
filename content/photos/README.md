# Yiasemi's own photos

Put photos taken at the café here (JPG, at least 1600px wide). For each one, add an entry to `tools/photos.config.json`:

```json
{ "id": "inside-1", "origin": "yiasemi", "approved": true, "file": "inside-1.jpg",
  "cat": "street", "aspect": null, "focal": null, "base": "yiasemi-interior-1",
  "author": "Yiasemi", "license": "© Yiasemi",
  "alt": { "en": "…describe the photo…", "el": "…περιγραφή…" } }
```

- Use `"approved": true` only once the owner has confirmed the photo may be published. Unapproved photos are skipped.
- To replace a licensed photo on the home page, reuse its id (`hero`, `about`, `sig-coffee`, `sig-sweet`, `sig-pie`) with `"origin": "yiasemi"`.
  The photo is **automatically cropped to that section's shape** (hero 3:4, about 4:5, signature dishes 3:4), so the layout cannot break. Use `"focal": [x, y]` (0–1) to choose what stays in frame, e.g. `[0.5, 0.3]` keeps the upper part.
- Optional `"caption": {"en": "…", "el": "…"}`. Without it, the caption reads "At Yiasemi / Στο Γιασεμί". Only photos with `"origin": "yiasemi"` ever get that label.
- Then run `python3 tools/images.py && python3 build.py`. Authentic photos appear first in the gallery, with an "At Yiasemi" filter and "© Yiasemi" credit.
