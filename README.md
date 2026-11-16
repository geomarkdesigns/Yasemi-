# Yiasemi — Γιασεμί

Website for Yiasemi café, Mnisikleous 31, Plaka, Athens.
It is a static site in English and Greek, deployed on Vercel from the `public/` folder.

| English | Greek |
|---|---|
| `/` home | `/el` |
| `/menu` | `/el/menu` |
| `/photos` ("More photos") | `/el/photos` |
| `/visit` | `/el/visit` |
| `/credits` (photo licences) | `/el/credits` |

## How it's built
- `content/site.json`: café facts (address, phone, hours, links). **The single source of truth.** Unknown facts stay `null` and the site handles them.
- `content/menu.json`: the official menu (bilingual, prices in EUR, dietary labels). Validated on every build; a bad entry fails the build.
- `build.py` + `sitegen/core.py`: generate every page, `sitemap.xml`, `robots.txt`, manifest, `404.html` and `vercel.json` (security headers) into `public/`.
- `tools/images.py`: crops photos to their frames and exports WebP + JPEG (360–1600px).
- `public/css/style.css`, `public/css/fonts.css` (self-hosted fonts) and `public/js/main.js` are edited directly. CSS is inlined into pages at build time.

```bash
python3 build.py          # after any content or design change
npm install && npm test   # build + unit tests + Playwright end-to-end tests
npm run serve             # local preview at http://127.0.0.1:8765
```

## Docs
- `docs/AUDIT.md`: audit, defect list, test results, Lighthouse, security
- `docs/CLIENT-REQUIREMENTS.md`: information still needed from the café

## Editing the menu
Edit `content/menu.json`: each item has `name.en`/`name.el`, optional `desc`, `price` (number, e.g. `6.5`) or `prices` (sizes), and `diet` (`"vegetarian"`, `"vegan"` or `null`). Only add a dietary label the kitchen has confirmed. Run `python3 build.py && npm test`, then push.

## Pre-launch access gate
Until the café approves going live, every URL (pages, images, sitemap, robots.txt) answers **401** with a code form, plus `X-Robots-Tag: noindex`.
- `deploy/middleware.js`: the gate (Vercel Routing Middleware, runs before anything is served). The code is **not** in the repo. It is the `ACCESS_CODE` environment variable (type *sensitive*) on the Vercel project. Change the code by changing that variable and redeploying.
- After entering the code, a secure HttpOnly cookie keeps you signed in for 30 days. `/__logout` signs out.
- **To go live:** deploy without `middleware.js` and remove the `X-Robots-Tag` header (see `deploy/vercel.proxy.json`).
