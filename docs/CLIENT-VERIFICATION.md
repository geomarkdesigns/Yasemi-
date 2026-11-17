# Yiasemi: outstanding information & approvals

**Rule:** the website shows nothing that has not been confirmed or published by Yiasemi. Every item below is **unconfirmed** until the owner approves it in writing. Nothing has been filled in with guesses.

Status key: 🔴 must be resolved before public launch · 🟠 needed for completeness · each answer goes into the file shown.

## Summary

| # | Item | Status | What the site shows now | Goes into |
|---|---|---|---|---|
| 1 | Operating status | 🔴 Unconfirmed | Café presented as open (per client instruction) | `content/site.json` → `notice` |
| 2 | Address | 🔴 Unconfirmed | Mnisikleous 31, Plaka, 105 55 Athens (per client instruction) | `site.json` → `address` |
| 3 | Opening hours | 🟠 Unknown | "Not published yet, please call" | `site.json` → `hours` |
| 4 | Menu applies to Plaka | 🔴 Unconfirmed | Official menu shown, labelled "as published by Yiasemi on yiasemi.gr" | `content/menu.json` |
| 5 | Prices & descriptions | 🔴 Owner approval needed | All 90 items with prices from the official menu | `docs/menu-approval.csv` |
| 6 | Dietary labels | 🔴 9 entries flagged | Labels as printed, except where the official menu contradicts itself (withheld) | `menu.json` → `diet` |
| 7 | EU allergen declarations | 🔴 Not provided | Notice: "tell our staff before you order"; no per-dish allergens | `docs/allergen-form.csv` |
| 8 | Official contact information | 🟠 Partly confirmed | Phone +30 213 041 7937, Instagram @yiasemi_bistrot | `site.json` → `phone`, `email` |
| 9 | Reservation policy | 🟠 Unknown | Nothing about reservations | `site.json` (new field when known) |

## 1. Operating status 🔴
- **Evidence:** Protothema, iefimerida and others reported that Yiasemi at Mnisikleous **closed on 31 March 2025** (lease ended, building sold). The owner opened *Yiasemi Cottage* (Irakleidon 7, Thiseio). As of the last check, **yiasemi.gr/contact-us says "Back to Plaka very soon…"**. The client has stated that the café has reopened.
- **Needed:** written confirmation that the Plaka café is open to the public, and from which date.
- **Until then:** keep the access gate on. If it is not yet open, set a `notice` (e.g. "Reopening soon") before launch.

## 2. Address 🔴
- **Site uses:** Mnisikleous 31 (per client). **All public listings found** (This is Athens, TripAdvisor, Wanderlog, press) say **Mnisikleous 23**.
- **Needed:** the confirmed street number. Update the Google Business Profile and the listings to match, since Google trusts consistent addresses.
- **Also:** exact map coordinates from the Google Business Profile (`geo`). They are not guessed; directions currently use the street address.

## 3. Opening hours 🟠
- **Evidence:** none published for Plaka. The menu's service times (breakfast 9:00–13:00, coffee 9:00–19:00) come from the **Thiseio** menu and are shown only as menu service times.
- **Needed:** regular weekly hours, seasonal changes, holiday closures and any temporary closures. The site supports all of these (today highlighted in Athens time, past dates hidden, schema.org for Google).

## 4. Menu applicability 🔴
- The only published menu (yiasemi.gr/menu) is headed **"MENU · Thiseio · Yiasemi Cottage"**.
- **Needed:** confirmation that the same menu and prices apply at Plaka, or the Plaka menu.

## 5. Menu prices & descriptions 🔴
- All **90 items** were transcribed exactly from the official menu (EN and EL pages), checked for bilingual completeness, and validated on every build. Prices use the existing format (`€6.50` EN / `6,50 €` EL).
- **Needed:** owner sign-off on `docs/menu-approval.csv` (one row per item; columns *approved* and *correction*).

## 6. Dietary labels: the 9 flagged entries 🔴

| # | Item (EN · EL) | Price | Label shown | Why it needs confirmation |
|---|---|---|---|---|
| 1 | Omelet with 3 eggs & up to 2 ingredients · Ομελέτα με 3 αυγά έως 2 υλικά | €7.00 | vegetarian | Vegetarian label is printed, but the ingredient choices are not listed. Confirm that no meat options are offered. |
| 2 | Stuffed tomatoes & peppers · Γεμιστά | €9.00 | none shown | Marked vegetarian on the Greek menu only, not on the English one. Confirm. |
| 3 | Patsavouropita with zucchini, carrot, mint & cheeses · Πατσαβουρόπιτα με κολοκύθι, καρότο, δυόσμο & τυριά | €6.50 | vegetarian | Appears on the Greek menu only. The English name is our translation. Confirm it is offered. |
| 4 | Bacon & cheese tart · Τάρτα με μπέικον & τυρί | €6.50 | none shown | The official menu prints a VEGETARIAN mark on this bacon tart. Label withheld until corrected. |
| 5 | Grilled feta cheese with homemade chutney · Ψητή φέτα με σπιτικό τσάτνεϊ | €6.00 | vegetarian | The English menu marks it vegetarian; the Greek menu marks it VEGAN. It contains feta, so vegetarian is shown. |
| 6 | Rusk with cheese & olives · Παξιμάδι με τυρί & ελιές | €4.50 | none shown | The official menu prints a VEGAN mark on a dish with cheese. Label withheld until corrected. |
| 7 | Freddo espresso / Double espresso · Freddo espresso / Διπλός | €4.00 | none shown | Printed as 'Freddo/Double' under Espresso; confirm wording. |
| 8 | Freddo cappuccino / Double cappuccino · Freddo cappuccino / Διπλός | €5.50 | none shown | Printed as 'Freddo/Double' under Cappuccino; confirm wording. |
| 9 | Giannatsi Ouzo Plomariou, premium dry, Lesvos · Γιαννατσή, Ούζο Πλωμαρίου, premium dry, Λέσβος | €12.00 | none shown | Listed on the English menu only. Confirm it is offered. |

## 7. EU allergen declarations 🔴
- Required for food served to the public (EU Regulation 1169/2011, 14 allergens). **None provided.**
- **Needed:** the kitchen completes `docs/allergen-form.csv`: Y or N for **all 14 allergens** for each dish, or leaves the row blank if unknown. Partial rows are rejected. Import: `python3 tools/allergens.py import docs/allergen-form.csv --by "Name, role"`. The site then shows "Contains: …" per dish and "Declared by our kitchen on <date>".
- **Nothing is inferred from dish names.**

## 8. Official contact information 🟠
- **Confirmed by public listings:** phone +30 213 041 7937, Instagram @yiasemi_bistrot, website yiasemi.gr.
- **Needed:** confirm the phone still reaches the Plaka café; an official **email** if guests may use it. A contact form is only added once there is a confirmed recipient.

## 9. Reservation policy 🟠
- **Unknown.** The site does not mention reservations.
- **Needed:** whether reservations or group bookings are accepted, and how (phone, booking service). Nothing is built until this is confirmed.

## Other approvals
- **Photos:** all current photos are openly licensed Wikimedia Commons photos of the street and of Greek dishes (credited, labelled "Illustrative" or with neutral captions). Please supply **photos of Yiasemi itself** with permission to publish (`content/photos/README.md`).
- **Owner quote:** the home page quotes the owner's text from yiasemi.gr/our-vision (attributed and linked). The Greek version is our translation; please approve it.
- **Hosting:** give the Vercel GitHub app access to the repository (see `docs/DEPLOYMENT.md` §4).
