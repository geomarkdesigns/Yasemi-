# Information needed from Yiasemi

The site shows nothing it cannot verify. Each answer below goes into `content/site.json` or `content/menu.json`. Then run `python3 build.py`.

## Must confirm before launch
1. **Address & status.** The site now uses **Mnisikleous 31** (per client). All public listings (This is Athens, TripAdvisor, Wanderlog) still say no. 23, so update those and the Google Business Profile to match. **Is the café open now?** Press reports a closure on 31 March 2025, and yiasemi.gr still says "Back to Plaka very soon…". If not yet open, set `notice` in `site.json` (e.g. "Reopening soon") or delay launch.
2. **Menu & prices (owner approval needed for all 90 items; sign-off sheet: `docs/menu-approval.csv`, 9 items flagged).** All prices on the site are copied exactly from the menu images on yiasemi.gr; none are placeholders and none are invented. The only published menu (yiasemi.gr/menu) is headed **"Thiseio · Yiasemi Cottage"**. Confirm it is the Plaka menu and prices, or send the Plaka menu.
3. **Dietary labels to correct on the official menu**:
   - Bacon & cheese tart: printed as *vegetarian* (label withheld on site)
   - Rusk with cheese & olives: printed as *vegan* (label withheld)
   - Grilled feta with chutney: *vegan* on the Greek menu, *vegetarian* on the English (shown as vegetarian)
   - Stuffed tomatoes & peppers (gemista): *vegetarian* on Greek only (no label shown)
   - Omelet: confirm no meat ingredients are offered
3a. **Allergens (required by EU Regulation 1169/2011 for food sold to the public).** Fill in `docs/allergen-form.csv`: one row per dish, **Y or N for every one of the 14 allergens**. Leave a row completely blank if not yet known; that dish then shows nothing. Partial rows are rejected on import. Return it and run `python3 tools/allergens.py import docs/allergen-form.csv --by "Name, role"`. Until then the site states that allergen details are not listed yet and asks guests to tell staff. Nothing has been inferred from dish names.
4. **Items on one language only**: Patsavouropita (Greek only; English name is our translation); Giannatsi ouzo 45% €12 (English only).
5. **Wording**: "Freddo/Double" under espresso and cappuccino. We show "Freddo espresso / Double espresso".

## Needed for completeness (site works without them)
6. **Opening hours** → `hours` in `site.json`: regular week, seasonal schedules (e.g. winter 1 Nov to 31 Mar), special dates/holiday closures, and temporary notices (e.g. "closed for renovation until…"). The site highlights today in Athens time, hides past special dates, and adds them to Google's structured data. Nothing is shown until the café confirms.
7. Exact map coordinates (from Google Business Profile) → `geo`
8. Official email, if customers may use it → `email`
9. Reservations: accepted or not? If yes, how (phone, booking service)?
10. Allergen information per dish (the EU's 14 allergens), only if the kitchen can confirm it
11. **Real photos of Yiasemi** (exterior, interior, dishes) with written permission to publish. See `content/photos/README.md`. Approved photos automatically appear first in the gallery with an "At Yiasemi" filter and "© Yiasemi" credit, and can replace any home-page photo.
12. Google Business Profile URL, and TripAdvisor URL (for `sameAs`)
13. Custom domain, if any (change `BASE` in `build.py`)
14. Approval before adding any analytics (requires a consent banner)

## Technical action
15. Give the Vercel GitHub app access to the `Yasemi-` repo (github.com/apps/vercel → Configure → add repo). This enables automatic deploys, edge caching, our own 404 page, and a future CMS.
