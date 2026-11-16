# Yiasemi's own photos

Put photos taken at the café here (JPG, at least 1600px wide). For each one, add an entry to `tools/photos.config.json`:

```json
{ "id": "inside-1", "origin": "yiasemi", "approved": true, "file": "inside-1.jpg",
  "cat": "street", "aspect": null, "focal": null, "base": "yiasemi-interior-1",
  "author": "Yiasemi", "license": "© Yiasemi",
  "alt": { "en": "…describe the photo…", "el": "…περιγραφή…" } }
```

- Use `"approved": true` only once the owner has confirmed the photo may be published. Unapproved photos are skipped.
- To replace a licensed photo on the home page, reuse its id (`hero`, `about`, `sig-coffee`, `sig-sweet`, `sig-pie`, `evening-1`) with `"origin": "yiasemi"`.
- Then run `python3 tools/images.py && python3 build.py`. Authentic photos appear first in the gallery, with an "At Yiasemi" filter and "© Yiasemi" credit.
