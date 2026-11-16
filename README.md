# Yiasemi — Γιασεμί

Website for Yiasemi café, Mnisikleous 23, Plaka, Athens.
It is a static site in English and Greek, deployed on Vercel from the `public/` folder.

| English | Greek |
|---|---|
| `/` home | `/el` |
| `/menu` | `/el/menu` |
| `/photos` ("More photos") | `/el/photos` |
| `/visit` | `/el/visit` |
| `/credits` (photo licences) | `/el/credits` |

## How it's built
- `build.py` holds **all text** (every string is a pair: English, Greek) and writes every HTML page, plus `sitemap.xml`, `robots.txt`, `manifest.webmanifest` and `404.html`, into `public/`.
- `tools/images.py` takes the photos listed in `tools/photos.config.json`, crops each to the exact shape of its frame, and exports WebP + JPEG at 480/800/1200/1600 px into `public/images/`. It also writes `photos.json` and the 1200×630 social image `og.jpg`.
- `public/css/style.css` and `public/js/main.js` are edited directly.

```bash
python3 tools/images.py   # only when photos change (needs Pillow)
python3 build.py          # after any text change
```
Commit and push. Vercel deploys automatically.

## SEO included
- Separate, crawlable English and Greek URLs with `hreflang` (en, el, x-default) and self-canonicals
- Unique titles and descriptions per page and language, Open Graph and Twitter cards with locale alternates
- Schema.org JSON-LD: `CafeOrCoffeeShop`, `WebSite`, `WebPage`, `BreadcrumbList`, `Menu` (with sections, items and vegetarian diet), `FAQPage`, `ImageGallery` / `ImageObject` (with creator, licence and acquire-licence page), `ContactPage`
- `sitemap.xml` with language alternates and image entries, `robots.txt`, web app manifest and icons
- Performance: responsive WebP with JPEG fallback, width/height on every image (no layout shift), a preloaded high-priority hero image, lazy loading, clean URLs and cache headers (`vercel.json`)

## Replace with your own photos
The photos currently come from Wikimedia Commons (credited on `/credits`). They show Mnisikleous Street and Greek food in general, **not Yiasemi itself**. To use your own:
1. Save your photo as `tools/.cache/<id>.jpg`, e.g. `hero.jpg`, `about.jpg`, `sig-coffee.jpg`, `sig-sweet.jpg` or `sig-pie.jpg`.
2. In `tools/photos.config.json`, set its `author` to your name, its `license` to e.g. `All rights reserved`, and update `alt`.
3. Run `python3 tools/images.py && python3 build.py`.

## To do (needs real info from the café)
- Prices: currently shown as `€ —` in `build.py`
- Opening hours: add them to `info_dl()` and as `openingHoursSpecification` in `cafe_ld()`
- Google Business Profile, Instagram and TripAdvisor links: add them to `sameAs` in `cafe_ld()`
- Custom domain: change `BASE` in `build.py`, rebuild and push
