# Yiasemi — Γιασεμί

A static website for Yiasemi café, Mnisikleous 23, Plaka, Athens. It has no build step and no dependencies: just HTML, CSS and JS.

## Pages
- `index.html`: hero, about, "A day on the steps", signature dishes, how to order Greek coffee, a press quote and the location
- `menu.html`: five tabs (Coffee, Tea & more, Pies & plates, Sweets, Evening), vegetarian marks and a side panel
- `photos.html`: "More photos" gallery with filters (Coffee, Food, The steps, Evening) and a lightbox you can step through with arrows
- `visit.html`: map, address, phone, metro stations and nearby sights, with walking times

## Style
- Plaka limestone, olive, terracotta and Aegean blue. Flat colours only, **no gradients**.
- Arched (neoclassical window) photo frames, a Greek-key border, a rotating address badge, a scrolling ticker, a stepped timeline and a large "Γιασεμί" wordmark in the footer
- Fonts: GFS Didot (Greek display) and Commissioner
- Light and dark mode (follows the visitor's system, with a toggle), and English and Greek (toggle). Both choices are remembered.
- Gentle motion that turns off when the visitor's system asks for reduced motion

## Add your photos
Put JPGs in `images/` using these names, and they replace the coloured jasmine placeholders automatically:

| File | Where |
|---|---|
| `hero.jpg` | Arched photo on the home page hero |
| `about.jpg` | "Named after jasmine" |
| `sig-coffee.jpg`, `sig-orange.jpg`, `sig-pies.jpg` | Signature dishes |
| `menu-side.jpg` | Menu page side photo |
| `photo-01.jpg` … `photo-16.jpg` | More photos page |

## Edit text and prices
Every piece of text appears twice in the HTML: `<span class="en">…</span><span class="el">…</span>`. Edit both.
Prices are shown as `€ —` in `menu.html`. Replace them with real prices.

## Publish
Repo **Settings → Pages → Deploy from branch → `main` / root**.
