// Yiasemi — instant navigation, theme, greeting, clock, nav, reveal, menu, gallery, lightbox
(function () {
  const root = document.documentElement;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  const isEl = () => root.lang === "el";

  /* ---------- Theme (light by default) ---------- */
  const setTheme = (t) => {
    root.setAttribute("data-theme", t); store.set("theme", t);
    const m = document.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute("content", t === "dark" ? "#161712" : "#f6f0e6");
  };

  /* ---------- Athens clock + greeting ---------- */
  const athensHour = () => {
    try { return +new Intl.DateTimeFormat("en-GB", { hour: "numeric", hourCycle: "h23", timeZone: "Europe/Athens" }).format(new Date()); }
    catch (e) { return new Date().getHours(); }
  };
  const GREET = {
    en: ["Good morning. The coffee's on.", "Good afternoon. There's a spot on the steps for you.", "Good evening. Come for a rakomelo.", "Still up? See you in the morning."],
    el: ["Καλημέρα. Ο καφές σας περιμένει.", "Καλό απόγευμα. Υπάρχει θέση στα σκαλιά για εσάς.", "Καλησπέρα. Ελάτε για ένα ρακόμελο.", "Ξύπνιοι ακόμα; Τα λέμε το πρωί."]
  };
  const tick = () => {
    try {
      const txt = new Intl.DateTimeFormat(isEl() ? "el-GR" : "en-GB", { hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZone: "Europe/Athens" }).format(new Date());
      document.querySelectorAll("[data-athens-time]").forEach((el) => (el.textContent = txt));
    } catch (e) {}
    const g = document.querySelector("[data-greeting]");
    if (g) {
      const h = athensHour();
      g.textContent = GREET[isEl() ? "el" : "en"][h >= 5 && h < 12 ? 0 : h >= 12 && h < 18 ? 1 : h >= 18 ? 2 : 3];
    }
  };

  /* ---------- Instant navigation (no full reloads) ---------- */
  const pages = new Map();
  const internal = (a) => {
    if (!a || a.target || a.hasAttribute("download") || a.getAttribute("rel") === "external") return null;
    const href = a.getAttribute("href");
    if (!href || href.startsWith("#") || /^(tel|mailto):/.test(href)) return null;
    const u = new URL(a.href, location.href);
    if (u.origin !== location.origin || /\.[a-z0-9]+$/i.test(u.pathname)) return null;
    return u;
  };
  const load = (path) => {
    if (!pages.has(path)) {
      pages.set(path, fetch(path, { credentials: "same-origin" }).then((r) => {
        if (!r.ok || !(r.headers.get("content-type") || "").includes("html")) throw new Error(r.status);
        return r.text();
      }).catch((e) => { pages.delete(path); throw e; }));
    }
    return pages.get(path);
  };
  const HEAD_SEL = 'title, meta[name="description"], meta[name="robots"], link[rel="canonical"], link[rel="alternate"], meta[property^="og:"], meta[name^="twitter:"], meta[name="geo.placename"], script[type="application/ld+json"]';

  async function go(u, { push = true, keepScroll = false } = {}) {
    let html;
    try { html = await load(u.pathname); } catch (e) { location.href = u.href; return; }
    const doc = new DOMParser().parseFromString(html, "text/html");
    const y = window.scrollY;
    const swap = () => {
      root.lang = doc.documentElement.lang;
      document.head.querySelectorAll(HEAD_SEL).forEach((n) => n.remove());
      doc.head.querySelectorAll(HEAD_SEL).forEach((n) => document.head.appendChild(document.importNode(n, true)));
      document.body.replaceWith(document.importNode(doc.body, true));
      if (push) history.pushState({ y: 0 }, "", u.pathname + u.search + u.hash);
      init({ instant: keepScroll });
      root.style.scrollBehavior = "auto";
      if (keepScroll) window.scrollTo({ top: y, behavior: "instant" });
      else if (u.hash && document.querySelector(u.hash)) document.querySelector(u.hash).scrollIntoView({ behavior: "instant" });
      else window.scrollTo({ top: 0, behavior: "instant" });
      requestAnimationFrame(() => (root.style.scrollBehavior = ""));
    };
    if (document.startViewTransition && !matchMedia("(prefers-reduced-motion: reduce)").matches) document.startViewTransition(swap);
    else swap();
  }

  document.addEventListener("click", (e) => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const a = e.target.closest("a");
    const u = internal(a);
    if (!u) return;
    if (u.pathname === location.pathname && u.hash) return;           // same-page anchor: let the browser scroll
    e.preventDefault();
    if (u.pathname === location.pathname && !u.hash) { window.scrollTo({ top: 0, behavior: "smooth" }); return; }
    go(u, { keepScroll: a.classList.contains("lang-link") });
  });
  // Prefetch on intent: hover, touch, keyboard focus
  const intent = (e) => { const u = internal(e.target.closest && e.target.closest("a")); if (u) load(u.pathname).catch(() => {}); };
  document.addEventListener("pointerover", intent, { passive: true });
  document.addEventListener("touchstart", intent, { passive: true });
  document.addEventListener("focusin", intent);
  window.addEventListener("popstate", () => go(new URL(location.href), { push: false }));
  history.replaceState({ y: 0 }, "");

  /* ---------- Global listeners (bound once) ---------- */
  const onScroll = () => {
    document.querySelector(".site-header")?.classList.toggle("scrolled", window.scrollY > 8);
    document.querySelector(".dock")?.classList.toggle("show", window.scrollY > 420);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  let lb = null;
  document.addEventListener("keydown", (e) => {
    if (!lb || !lb.el.classList.contains("open")) return;
    if (e.key === "Escape") lb.close();
    if (e.key === "ArrowLeft") lb.show(lb.idx - 1);
    if (e.key === "ArrowRight") lb.show(lb.idx + 1);
  });
  setInterval(tick, 20000);

  /* ---------- Per-page setup (runs on load and after every swap) ---------- */
  function init({ instant = false } = {}) {
    tick(); onScroll();

    document.getElementById("theme-toggle")?.addEventListener("click", () =>
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark"));

    const links = document.querySelector(".links");
    const mt = document.querySelector(".menu-toggle");
    mt?.addEventListener("click", () => mt.setAttribute("aria-expanded", links.classList.toggle("open")));

    document.querySelectorAll(".frame img").forEach((img) =>
      img.addEventListener("error", () => img.classList.add("missing")));

    const els = document.querySelectorAll(".reveal");
    if (instant || !("IntersectionObserver" in window)) els.forEach((el) => el.classList.add("in"));
    else {
      const io = new IntersectionObserver((entries) => entries.forEach((e) => {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      }), { threshold: 0.05, rootMargin: "0px 0px -24px 0px" });
      els.forEach((el) => { if (el.dataset.delay) el.style.transitionDelay = Math.min(+el.dataset.delay, 120) + "ms"; io.observe(el); });
    }

    const tabs = document.querySelectorAll(".menu-tabs button");
    tabs.forEach((b) => b.addEventListener("click", () => {
      tabs.forEach((x) => x.setAttribute("aria-selected", String(x === b)));
      document.querySelectorAll(".menu-group").forEach((g) => g.classList.toggle("active", g.id === b.getAttribute("aria-controls")));
    }));

    const filters = document.querySelectorAll(".filters button");
    const shots = [...document.querySelectorAll(".gallery .frame")];
    filters.forEach((b) => b.addEventListener("click", () => {
      filters.forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      const f = b.dataset.filter;
      shots.forEach((s) => s.classList.toggle("hide", f !== "all" && s.dataset.cat !== f));
    }));

    lb = null;
    const el = document.querySelector(".lightbox");
    if (el) {
      const img = el.querySelector("img");
      lb = { el, idx: 0, list: [] };
      lb.show = (i) => {
        lb.idx = (i + lb.list.length) % lb.list.length;
        const im = lb.list[lb.idx];
        img.src = im.closest(".frame").dataset.full || im.currentSrc || im.src; img.alt = im.alt;
      };
      lb.close = () => el.classList.remove("open");
      shots.forEach((f) => {
        f.tabIndex = 0;
        const open = () => {
          lb.list = shots.filter((s) => !s.classList.contains("hide")).map((s) => s.querySelector("img")).filter((i) => i && !i.classList.contains("missing"));
          const me = f.querySelector("img");
          if (!lb.list.includes(me)) return;
          lb.show(lb.list.indexOf(me)); el.classList.add("open");
        };
        f.addEventListener("click", open);
        f.addEventListener("keydown", (e) => { if (e.key === "Enter") open(); });
      });
      el.querySelector(".lb-close").addEventListener("click", lb.close);
      el.querySelector(".lb-prev").addEventListener("click", (e) => { e.stopPropagation(); lb.show(lb.idx - 1); });
      el.querySelector(".lb-next").addEventListener("click", (e) => { e.stopPropagation(); lb.show(lb.idx + 1); });
      el.addEventListener("click", (e) => { if (e.target === el) lb.close(); });
    }

    const y = document.getElementById("year");
    if (y) y.textContent = new Date().getFullYear();

    // Warm up the pages people are most likely to open next (incl. the other language)
    const warm = () => document.querySelectorAll(".links a, .lang-link").forEach((a) => { const u = internal(a); if (u && u.pathname !== location.pathname) load(u.pathname).catch(() => {}); });
    ("requestIdleCallback" in window) ? requestIdleCallback(warm, { timeout: 2500 }) : setTimeout(warm, 1200);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => init());
  else init();
})();
