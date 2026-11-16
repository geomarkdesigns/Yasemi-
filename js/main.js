// Yiasemi — theme, language, nav, reveal, menu tabs, lightbox
(function () {
  const root = document.documentElement;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------- Translations ---------- */
  const T = {
    en: {
      "nav.home": "Home", "nav.menu": "Menu", "nav.photos": "More photos", "nav.visit": "Visit",
      "hero.eyebrow": "Café · Plaka, Athens",
      "hero.title": "Slow coffee on the steps of Plaka.",
      "hero.lead": "Greek coffee, homemade pies and sweets, served on the old stepped street of Mnisikleous, just below the Acropolis.",
      "hero.cta1": "See the menu", "hero.cta2": "Find us",
      "about.eyebrow": "Our place",
      "about.title": "Named after jasmine.",
      "about.p1": "Yiasemi means jasmine in Greek. Cushions on the steps, small tables, and an easy pace from morning until late.",
      "about.p2": "Sit, order a coffee, and watch the neighbourhood go by.",
      "f1.t": "Greek coffee", "f1.p": "Brewed slowly in a briki, served with a glass of cold water.",
      "f2.t": "Homemade", "f2.p": "Pies, cakes and sweets made in our kitchen every day.",
      "f3.t": "On the steps", "f3.p": "Seating along Mnisikleous, one of Plaka's best-known streets.",
      "loc.eyebrow": "Visit", "loc.title": "Find us",
      "loc.address": "Address", "loc.addressVal": "Mnisikleous 23, Plaka, 105 55 Athens",
      "loc.phone": "Phone", "loc.directions": "Directions", "loc.open": "Open in Google Maps",
      "menu.eyebrow": "Menu", "menu.title": "Coffee, pies and sweets.",
      "menu.tab.coffee": "Coffee", "menu.tab.food": "Food", "menu.tab.sweets": "Sweets", "menu.tab.drinks": "Drinks",
      "m.greek": "Greek coffee", "m.greek.d": "Traditional, brewed in a briki",
      "m.freddo": "Freddo espresso", "m.freddo.d": "Double espresso, shaken over ice",
      "m.cappuccino": "Freddo cappuccino", "m.cappuccino.d": "With cold milk foam",
      "m.frappe": "Frappé", "m.frappe.d": "The classic Greek iced coffee",
      "m.espresso": "Espresso", "m.espresso.d": "Single or double",
      "m.tea": "Mountain tea", "m.tea.d": "Greek herbal tea with honey",
      "m.spinach": "Spinach pie", "m.spinach.d": "Homemade spanakopita",
      "m.cheese": "Cheese pie", "m.cheese.d": "Tiropita with feta",
      "m.meze": "Meze plate", "m.meze.d": "Small plates for sharing",
      "m.salad": "Greek salad", "m.salad.d": "Tomato, cucumber, onion, olives, feta",
      "m.orange": "Orange cake", "m.orange.d": "Portokalopita with a scoop of mastic ice cream",
      "m.yogurt": "Yogurt with honey", "m.yogurt.d": "Greek yogurt, thyme honey, walnuts",
      "m.galak": "Galaktoboureko", "m.galak.d": "Semolina custard in filo, syrup",
      "m.cake": "Cake of the day", "m.cake.d": "Ask us what's fresh",
      "m.lemonade": "Homemade lemonade", "m.lemonade.d": "Fresh lemon, mint",
      "m.wine": "House wine", "m.wine.d": "White, red or rosé, by the glass",
      "m.raki": "Rakomelo", "m.raki.d": "Warm raki with honey and spices",
      "m.juice": "Fresh orange juice", "m.juice.d": "Squeezed to order",
      "menu.note": "Prices and items are indicative and may change. Please ask our staff about allergens.",
      "photos.eyebrow": "Gallery", "photos.title": "More photos",
      "photos.lead": "A few moments from the steps of Mnisikleous.",
      "photo": "Photo",
      "footer.rights": "Yiasemi · Mnisikleous 23, Plaka, Athens"
    },
    el: {
      "nav.home": "Αρχική", "nav.menu": "Μενού", "nav.photos": "Περισσότερες φωτογραφίες", "nav.visit": "Επίσκεψη",
      "hero.eyebrow": "Καφέ · Πλάκα, Αθήνα",
      "hero.title": "Αργός καφές στα σκαλιά της Πλάκας.",
      "hero.lead": "Ελληνικός καφές, σπιτικές πίτες και γλυκά, στο παλιό σκαλωτό στενό της Μνησικλέους, κάτω από την Ακρόπολη.",
      "hero.cta1": "Δείτε το μενού", "hero.cta2": "Βρείτε μας",
      "about.eyebrow": "Ο χώρος μας",
      "about.title": "Πήραμε το όνομα από το γιασεμί.",
      "about.p1": "Μαξιλάρια στα σκαλιά, μικρά τραπεζάκια και χαλαρός ρυθμός από το πρωί μέχρι αργά.",
      "about.p2": "Καθίστε, παραγγείλτε έναν καφέ και δείτε τη γειτονιά να περνά.",
      "f1.t": "Ελληνικός καφές", "f1.p": "Ψημένος αργά στο μπρίκι, με ένα ποτήρι κρύο νερό.",
      "f2.t": "Σπιτικά", "f2.p": "Πίτες, κέικ και γλυκά από την κουζίνα μας, κάθε μέρα.",
      "f3.t": "Στα σκαλιά", "f3.p": "Θέσεις κατά μήκος της Μνησικλέους, ενός από τους πιο γνωστούς δρόμους της Πλάκας.",
      "loc.eyebrow": "Επίσκεψη", "loc.title": "Βρείτε μας",
      "loc.address": "Διεύθυνση", "loc.addressVal": "Μνησικλέους 23, Πλάκα, 105 55 Αθήνα",
      "loc.phone": "Τηλέφωνο", "loc.directions": "Οδηγίες", "loc.open": "Άνοιγμα στο Google Maps",
      "menu.eyebrow": "Μενού", "menu.title": "Καφές, πίτες και γλυκά.",
      "menu.tab.coffee": "Καφές", "menu.tab.food": "Φαγητό", "menu.tab.sweets": "Γλυκά", "menu.tab.drinks": "Ποτά",
      "m.greek": "Ελληνικός καφές", "m.greek.d": "Παραδοσιακός, στο μπρίκι",
      "m.freddo": "Freddo espresso", "m.freddo.d": "Διπλός espresso, χτυπημένος με πάγο",
      "m.cappuccino": "Freddo cappuccino", "m.cappuccino.d": "Με αφρόγαλα",
      "m.frappe": "Φραπέ", "m.frappe.d": "Ο κλασικός ελληνικός κρύος καφές",
      "m.espresso": "Espresso", "m.espresso.d": "Μονός ή διπλός",
      "m.tea": "Τσάι του βουνού", "m.tea.d": "Με μέλι",
      "m.spinach": "Σπανακόπιτα", "m.spinach.d": "Σπιτική",
      "m.cheese": "Τυρόπιτα", "m.cheese.d": "Με φέτα",
      "m.meze": "Πιατέλα μεζέδων", "m.meze.d": "Μικρά πιάτα για μοίρασμα",
      "m.salad": "Χωριάτικη σαλάτα", "m.salad.d": "Ντομάτα, αγγούρι, κρεμμύδι, ελιές, φέτα",
      "m.orange": "Πορτοκαλόπιτα", "m.orange.d": "Με μπάλα παγωτό μαστίχα",
      "m.yogurt": "Γιαούρτι με μέλι", "m.yogurt.d": "Θυμαρίσιο μέλι, καρύδια",
      "m.galak": "Γαλακτομπούρεκο", "m.galak.d": "Κρέμα σιμιγδαλιού σε φύλλο, σιρόπι",
      "m.cake": "Γλυκό ημέρας", "m.cake.d": "Ρωτήστε μας τι είναι φρέσκο",
      "m.lemonade": "Σπιτική λεμονάδα", "m.lemonade.d": "Φρέσκο λεμόνι, δυόσμος",
      "m.wine": "Κρασί χύμα", "m.wine.d": "Λευκό, κόκκινο ή ροζέ, στο ποτήρι",
      "m.raki": "Ρακόμελο", "m.raki.d": "Ζεστή ρακή με μέλι και μπαχαρικά",
      "m.juice": "Φρέσκος χυμός πορτοκάλι", "m.juice.d": "Στυμμένος τη στιγμή",
      "menu.note": "Τα είδη και οι τιμές είναι ενδεικτικά και μπορεί να αλλάξουν. Ρωτήστε το προσωπικό για αλλεργιογόνα.",
      "photos.eyebrow": "Γκαλερί", "photos.title": "Περισσότερες φωτογραφίες",
      "photos.lead": "Λίγες στιγμές από τα σκαλιά της Μνησικλέους.",
      "photo": "Φωτογραφία",
      "footer.rights": "Γιασεμί · Μνησικλέους 23, Πλάκα, Αθήνα"
    }
  };

  /* ---------- Theme ---------- */
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const applyTheme = (t) => { root.setAttribute("data-theme", t); store.set("theme", t); };
  applyTheme(store.get("theme") || (prefersDark ? "dark" : "light"));

  /* ---------- Language ---------- */
  const applyLang = (lang) => {
    const dict = T[lang] || T.en;
    root.lang = lang;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const v = dict[el.dataset.i18n];
      if (v) el.textContent = v;
    });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
      const v = dict[el.dataset.i18nAria];
      if (v) el.setAttribute("aria-label", v);
    });
    const btn = document.getElementById("lang-toggle");
    if (btn) btn.textContent = lang === "el" ? "EN" : "ΕΛ";
    store.set("lang", lang);
  };

  document.addEventListener("DOMContentLoaded", () => {
    applyLang(store.get("lang") || "en");

    document.getElementById("theme-toggle")?.addEventListener("click", () =>
      applyTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark"));
    document.getElementById("lang-toggle")?.addEventListener("click", () =>
      applyLang(root.lang === "el" ? "en" : "el"));

    /* Mobile nav */
    const links = document.querySelector(".links");
    const mt = document.querySelector(".menu-toggle");
    mt?.addEventListener("click", () => {
      const open = links.classList.toggle("open");
      mt.setAttribute("aria-expanded", open);
    });
    links?.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => {
      links.classList.remove("open"); mt?.setAttribute("aria-expanded", "false");
    }));

    /* Header border on scroll */
    const header = document.querySelector(".site-header");
    const onScroll = () => header?.classList.toggle("scrolled", window.scrollY > 8);
    onScroll(); window.addEventListener("scroll", onScroll, { passive: true });

    /* Hide broken images so the flat placeholder shows */
    document.querySelectorAll(".frame img").forEach((img) => {
      const miss = () => img.classList.add("missing");
      if (img.complete && img.naturalWidth === 0) miss();
      img.addEventListener("error", miss);
      img.addEventListener("load", () => img.classList.remove("missing"));
    });

    /* Reveal on scroll */
    const els = document.querySelectorAll(".reveal");
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver((entries) => entries.forEach((e) => {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      }), { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
      els.forEach((el, i) => { el.style.transitionDelay = (el.dataset.delay || 0) + "ms"; io.observe(el); });
    } else els.forEach((el) => el.classList.add("in"));

    /* Menu tabs */
    const tabs = document.querySelectorAll(".menu-tabs button");
    tabs.forEach((b) => b.addEventListener("click", () => {
      tabs.forEach((x) => x.setAttribute("aria-selected", x === b));
      document.querySelectorAll(".menu-group").forEach((g) =>
        g.classList.toggle("active", g.id === b.getAttribute("aria-controls")));
    }));

    /* Lightbox */
    const lb = document.querySelector(".lightbox");
    if (lb) {
      const lbImg = lb.querySelector("img");
      const close = () => lb.classList.remove("open");
      document.querySelectorAll(".gallery .frame").forEach((f) => f.addEventListener("click", () => {
        const img = f.querySelector("img");
        if (!img || img.classList.contains("missing")) return;
        lbImg.src = img.src; lbImg.alt = img.alt; lb.classList.add("open");
      }));
      lb.addEventListener("click", (e) => { if (e.target !== lbImg) close(); });
      document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
    }

    const y = document.getElementById("year");
    if (y) y.textContent = new Date().getFullYear();
  });
})();
