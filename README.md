# Yiasemi — Γιασεμί

A static website for Yiasemi café, Mnisikleous 23, Plaka, Athens. It has no build step and no dependencies.

- `index.html`: home page, about section and location (map, address, phone)
- `menu.html`: menu with Coffee, Food, Sweets and Drinks tabs
- `photos.html`: "More photos" gallery with a lightbox
- Light and dark mode, which follows the visitor's system setting and can be switched with a toggle
- English and Greek, switched with a toggle and remembered for next time
- Flat colours with no gradients; small fade and lift animations that turn off when the visitor's system asks for reduced motion

## Add your photos
Put JPGs in `images/` using these names, and they replace the placeholders automatically:

| File | Where it shows |
|---|---|
| `hero.jpg` | Large photo on the home page |
| `about.jpg` | "Named after jasmine" section |
| `photo-01.jpg` … `photo-12.jpg` | More photos page |

## Edit text and prices
All text for both languages is in `js/main.js`, in the `T` object (`en` / `el`).
Prices are shown as `€ —` in `menu.html`. Replace them with real prices.

## Run locally
Open `index.html` in a browser, or run `python3 -m http.server` in this folder.

## Publish
Repo **Settings → Pages → Deploy from branch → `main` / root**.
