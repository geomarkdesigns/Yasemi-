// Yiasemi — progressive enhancement only: every page works without this file.
// Instant navigation, theme, greeting, mobile nav, reveal, menu search/filter/scrollspy,
// gallery filter + lightbox, click-to-load map.
(function () {
  "use strict";
  const root = document.documentElement;
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  const isEl = () => root.lang === "el";

  /* ---------- Pre-launch gate: sign out when the visitor leaves (no-op once the gate is removed) ---------- */
  if (/(?:^|;\s*)yiasemi_gated=1/.test(document.cookie)) {
    // In-site navigation never unloads the page, so this fires only on closing the tab,
    // going to another website, or reloading.
    addEventListener("pagehide", () => { try { navigator.sendBeacon("/__logout"); } catch (e) {} });
    addEventListener("pageshow", (e) => { if (e.persisted) location.reload(); });   // back-button cache: ask the server again
  }
  const L = (en, el) => (isEl() ? el : en);

  /* ---------- Theme (light by default; stored only after the visitor chooses) ---------- */
  function syncThemeUI() {
    const dark = root.getAttribute("data-theme") === "dark";
    const b = document.getElementById("theme-toggle");
    if (b) b.setAttribute("aria-pressed", String(dark));
    const m = document.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute("content", dark ? "#161712" : "#f6f0e6");
  }
  function setTheme(t) { root.setAttribute("data-theme", t); store.set("theme", t); syncThemeUI(); }

  /* ---------- Greeting by Athens time (static fallback text is in the HTML) ---------- */
  function greet() {
    const el = document.querySelector("[data-greeting]");
    if (!el) return;
    let h;
    try { h = +new Intl.DateTimeFormat("en-GB", { hour: "numeric", hourCycle: "h23", timeZone: "Europe/Athens" }).format(new Date()); }
    catch (e) { return; }
    if (!(h >= 0 && h < 24)) return;
    const i = h >= 5 && h < 12 ? 0 : h >= 12 && h < 18 ? 1 : 2;
    el.textContent = [L("Good morning, and welcome to Yiasemi.", "Καλημέρα και καλώς ήρθατε στο Γιασεμί."),
                      L("Good afternoon, and welcome to Yiasemi.", "Καλό απόγευμα και καλώς ήρθατε στο Γιασεμί."),
                      L("Good evening, and welcome to Yiasemi.", "Καλησπέρα και καλώς ήρθατε στο Γιασεμί.")][i];
  }

  /* ---------- Instant navigation (falls back to normal links on any error) ---------- */
  const pages = new Map();
  function internal(a) {
    if (!a || a.target || a.hasAttribute("download")) return null;
    const href = a.getAttribute("href");
    if (!href || href.startsWith("#") || /^(tel|mailto):/i.test(href)) return null;
    const u = new URL(a.href, location.href);
    if (u.origin !== location.origin || /\.[a-z0-9]+$/i.test(u.pathname)) return null;
    return u;
  }
  function load(path) {
    if (!pages.has(path)) {
      pages.set(path, fetch(path, { credentials: "same-origin", cache: "no-cache" }).then((r) => {   // always revalidate: never show a stale cached page
        if (!r.ok || !(r.headers.get("content-type") || "").includes("html")) throw new Error("HTTP " + r.status);
        return r.text();
      }).catch((e) => { pages.delete(path); throw e; }));
    }
    return pages.get(path);
  }
  const HEAD_SEL = 'title, meta[name="description"], meta[name="robots"], link[rel="canonical"], link[rel="alternate"], meta[property^="og:"], meta[name^="twitter:"], link[rel="preload"][as="image"], script[type="application/ld+json"]';
  async function go(u, { push = true, keepScroll = false } = {}) {
    let html;
    try { html = await load(u.pathname); } catch (e) { location.href = u.href; return; }
    const doc = new DOMParser().parseFromString(html, "text/html");
    if (!doc.body || !doc.querySelector("main")) { location.href = u.href; return; }
    const y = window.scrollY;
    const swap = () => {
      root.lang = doc.documentElement.lang;
      document.head.querySelectorAll(HEAD_SEL).forEach((n) => n.remove());
      doc.head.querySelectorAll(HEAD_SEL).forEach((n) => document.head.appendChild(document.importNode(n, true)));
      document.body.replaceWith(document.importNode(doc.body, true));
      if (push) history.pushState({}, "", u.pathname + u.search + u.hash);
      init({ instant: keepScroll });
      const target = u.hash && document.getElementById(decodeURIComponent(u.hash.slice(1)));
      if (keepScroll) window.scrollTo({ top: y, behavior: "instant" });
      else if (target) target.scrollIntoView({ behavior: "instant" });
      else window.scrollTo({ top: 0, behavior: "instant" });
      if (!keepScroll) document.getElementById("main")?.focus({ preventScroll: true });
    };
    if (document.startViewTransition && !reduced()) document.startViewTransition(swap); else swap();
  }
  document.addEventListener("click", (e) => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const a = e.target.closest("a");
    const u = internal(a);
    if (!u) return;
    if (u.pathname === location.pathname && u.hash) return;                       // same-page anchor
    e.preventDefault();
    if (u.pathname === location.pathname) { window.scrollTo({ top: 0, behavior: reduced() ? "auto" : "smooth" }); return; }
    go(u, { keepScroll: a.classList.contains("lang-link") });
  });
  const intent = (e) => { const a = e.target.closest && e.target.closest("a"); const u = internal(a); if (u && u.pathname !== location.pathname) load(u.pathname).catch(() => {}); };
  document.addEventListener("pointerover", intent, { passive: true });
  document.addEventListener("touchstart", intent, { passive: true });
  document.addEventListener("focusin", intent);
  window.addEventListener("popstate", () => go(new URL(location.href), { push: false }));

  /* ---------- Global listeners (bound once) ---------- */
  let ticking = false;
  window.addEventListener("scroll", () => {
    if (ticking) return; ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      document.querySelector(".site-header")?.classList.toggle("scrolled", scrollY > 8);
      document.querySelector(".dock")?.classList.toggle("show", scrollY > 420);
    });
  }, { passive: true });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const links = document.querySelector(".links.open");
    if (links) { closeNav(true); }
  });
  function closeNav(focusToggle) {
    const links = document.querySelector(".links"), mt = document.querySelector(".menu-toggle");
    if (!links || !mt) return;
    links.classList.remove("open"); mt.setAttribute("aria-expanded", "false");
    if (focusToggle) mt.focus();
  }

  /* ---------- Menu page ---------- */
  const norm = (s) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ς/g, "σ");
  function initMenu() {
    const input = document.getElementById("menu-search");
    if (!input) return;
    const items = [...document.querySelectorAll(".mi")].map((li) => ({ li, text: norm(li.textContent), diet: li.dataset.diet || "" }));
    const secs = [...document.querySelectorAll(".menu-sec")];
    const blocks = [...document.querySelectorAll(".menu-group-block")];
    const empty = document.getElementById("menu-empty");
    const count = document.getElementById("menu-count");
    const dietBtns = [...document.querySelectorAll("[data-diet-filter]")];
    let diet = "all";
    function apply() {
      const q = norm(input.value.trim());
      let shown = 0;
      items.forEach((it) => {
        const dOk = diet === "all" || (diet === "vegetarian" ? /vegetarian|vegan/.test(it.diet) : /vegan/.test(it.diet));
        const ok = dOk && (!q || it.text.includes(q));
        it.li.hidden = !ok; if (ok) shown++;
      });
      document.querySelectorAll(".kind").forEach((h) => { const ul = h.nextElementSibling; h.hidden = !ul.querySelector(".mi:not([hidden])"); });
      secs.forEach((s) => { s.hidden = !s.querySelector(".mi:not([hidden])"); });
      blocks.forEach((b) => { b.hidden = !b.querySelector(".menu-sec:not([hidden])"); });
      document.querySelectorAll(".cat-nav a").forEach((a) => { const s = document.getElementById(a.dataset.spy); a.parentElement.hidden = !s || s.hidden; });
      empty.hidden = shown !== 0;
      count.textContent = q || diet !== "all" ? L(`${shown} items shown`, `Εμφανίζονται ${shown} είδη`) : "";
    }
    let t; input.addEventListener("input", () => { clearTimeout(t); t = setTimeout(apply, 80); });
    input.addEventListener("keydown", (e) => { if (e.key === "Escape") { input.value = ""; apply(); } });
    dietBtns.forEach((b) => b.addEventListener("click", () => {
      diet = b.dataset.dietFilter; dietBtns.forEach((x) => x.setAttribute("aria-pressed", String(x === b))); apply();
    }));
    document.querySelector("[data-clear-search]")?.addEventListener("click", () => {
      input.value = ""; diet = "all"; dietBtns.forEach((x) => x.setAttribute("aria-pressed", String(x.dataset.dietFilter === "all"))); apply(); input.focus();
    });
    // Category nav: smooth jump + active section tracking
    const chips = [...document.querySelectorAll(".cat-nav a")];
    const strip = document.querySelector(".cat-nav ul");
    chips.forEach((a) => a.addEventListener("click", (e) => {
      const s = document.getElementById(a.dataset.spy); if (!s) return;
      e.preventDefault(); s.scrollIntoView({ behavior: reduced() ? "auto" : "smooth", block: "start" });
      history.replaceState(history.state, "", "#" + a.dataset.spy);
    }));
    const setActive = (id) => chips.forEach((a) => {
      const on = a.dataset.spy === id; a.classList.toggle("active", on);
      if (on) { a.setAttribute("aria-current", "true"); const l = a.offsetLeft - strip.clientWidth / 2 + a.clientWidth / 2; strip.scrollTo({ left: l, behavior: reduced() ? "auto" : "smooth" }); }
      else a.removeAttribute("aria-current");
    });
    if ("IntersectionObserver" in window) {
      const bar = document.getElementById("menu-bar");
      const io = new IntersectionObserver((entries) => {
        const vis = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (vis[0]) setActive(vis[0].target.id);
      }, { rootMargin: `-${(bar?.offsetHeight || 0) + 80}px 0px -55% 0px` });
      secs.forEach((s) => io.observe(s));
    }
  }

  /* ---------- Gallery + lightbox ---------- */
  let lb = null;
  function initGallery() {
    const items = [...document.querySelectorAll(".g-item")];
    if (!items.length) return;
    const btns = [...document.querySelectorAll(".filters button")];
    const count = document.getElementById("gallery-count");
    btns.forEach((b) => b.addEventListener("click", () => {
      btns.forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      const f = b.dataset.filter; let n = 0;
      items.forEach((it) => { const show = f === "all" || it.dataset.cat === f; it.hidden = !show; if (show) n++; });
      if (count) count.textContent = L(`${n} photos shown`, `Εμφανίζονται ${n} φωτογραφίες`);
    }));
    const el = document.querySelector(".lightbox");
    if (!el) return;
    const stage = el.querySelector(".lb-stage"), img = stage.querySelector("img"), cap = el.querySelector(".lb-cap"), cnt = el.querySelector(".lb-count");
    let list = [], idx = 0, opener = null;
    const visible = () => items.filter((it) => !it.hidden && it.querySelector("img:not(.missing)"));
    function show(i) {
      idx = (i + list.length) % list.length;
      const fig = list[idx].querySelector(".frame"), src = fig.dataset.full, thumb = fig.querySelector("img");
      stage.classList.add("loading");
      img.onload = () => stage.classList.remove("loading");
      img.onerror = () => { stage.classList.remove("loading"); cap.textContent = L("This photo could not be loaded.", "Η φωτογραφία δεν φορτώθηκε."); };
      img.src = src || thumb.currentSrc || thumb.src; img.alt = fig.dataset.alt || thumb.alt;
      cap.innerHTML = fig.querySelector("figcaption")?.innerHTML || "";
      cnt.textContent = `${idx + 1} / ${list.length}`;
      [idx + 1, idx - 1].forEach((j) => { const f = list[(j + list.length) % list.length].querySelector(".frame"); if (f.dataset.full) { const p = new Image(); p.src = f.dataset.full; } });
    }
    function open(item) {
      list = visible(); if (!list.includes(item)) return;
      opener = item.querySelector("button");
      el.hidden = false; root.style.overflow = "hidden";
      show(list.indexOf(item));
      requestAnimationFrame(() => el.classList.add("open"));
      el.querySelector(".lb-close").focus();
    }
    function close() {
      el.classList.remove("open"); root.style.overflow = "";
      setTimeout(() => { el.hidden = true; img.removeAttribute("src"); }, reduced() ? 0 : 200);
      opener?.focus();
    }
    items.forEach((it) => it.querySelector(".g-open").addEventListener("click", () => open(it)));
    el.querySelector(".lb-close").addEventListener("click", close);
    el.querySelector(".lb-prev").addEventListener("click", () => show(idx - 1));
    el.querySelector(".lb-next").addEventListener("click", () => show(idx + 1));
    el.addEventListener("click", (e) => { if (swiped) { swiped = false; return; } if (e.target === el) close(); });
    el.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { e.preventDefault(); close(); }
      else if (e.key === "ArrowLeft") show(idx - 1);
      else if (e.key === "ArrowRight") show(idx + 1);
      else if (e.key === "Tab") {                                   // keep focus inside the dialog
        const f = [...el.querySelectorAll("button")]; const first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    let sx = null, sy = null, swiped = false;                       // swipe anywhere in the viewer (not only on the image)
    el.addEventListener("pointerdown", (e) => { if (e.target.closest(".lb-btn")) return; sx = e.clientX; sy = e.clientY; swiped = false; });
    el.addEventListener("pointerup", (e) => {
      if (sx === null) return; const dx = e.clientX - sx, dy = e.clientY - sy; sx = null;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) { swiped = true; show(idx + (dx < 0 ? 1 : -1)); }
    });
    el.addEventListener("pointercancel", () => { sx = null; });
    lb = { el, close };
  }

  /* ---------- Click-to-load map (no Google request until asked) ---------- */
  function initMap() {
    document.querySelectorAll("[data-load-map]").forEach((b) => b.addEventListener("click", () => {
      const box = b.closest(".map"); if (!box) return;
      const f = document.createElement("iframe");
      f.src = box.dataset.map; f.title = box.dataset.title; f.loading = "lazy"; f.referrerPolicy = "no-referrer-when-downgrade";
      f.setAttribute("allowfullscreen", "");
      box.replaceChildren(f); f.focus();
    }));
  }

  /* ---------- Per-page setup (initial load and after every swap) ---------- */
  function init({ instant = false } = {}) {
    syncThemeUI(); greet();
    document.getElementById("theme-toggle")?.addEventListener("click", () => setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark"));
    const links = document.querySelector(".links"), mt = document.querySelector(".menu-toggle");
    mt?.addEventListener("click", () => { const o = links.classList.toggle("open"); mt.setAttribute("aria-expanded", String(o)); if (o) links.querySelector("a")?.focus(); });
    document.querySelectorAll(".frame img").forEach((img) => {
      const done = () => img.classList.add("loaded");
      if (img.complete && img.naturalWidth) done(); else img.addEventListener("load", done, { once: true });
      img.addEventListener("error", () => img.classList.add("missing"), { once: true });
    });
    const els = document.querySelectorAll(".reveal");
    if (instant || !("IntersectionObserver" in window)) els.forEach((el) => el.classList.add("in"));
    else {
      const io = new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { rootMargin: "0px 0px -24px 0px" });
      els.forEach((el) => io.observe(el));
    }
    initMenu(); initGallery(); initMap();
    const y = document.getElementById("year"); if (y) y.textContent = new Date().getFullYear();
    const warm = () => document.querySelectorAll(".links a, .lang-link").forEach((a) => { const u = internal(a); if (u && u.pathname !== location.pathname) load(u.pathname).catch(() => {}); });
    // Warm likely next pages only after this page has fully loaded, so it never competes with first paint.
    const later = () => setTimeout(() => ("requestIdleCallback" in window) ? requestIdleCallback(warm, { timeout: 4000 }) : warm(), 1200);
    if (document.readyState === "complete") later(); else window.addEventListener("load", later, { once: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => init()); else init();
})();
