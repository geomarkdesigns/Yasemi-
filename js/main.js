// Yiasemi — theme, language, nav, reveal, menu, gallery, lightbox, Athens clock
(function () {
  const root = document.documentElement;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  const setTheme = (t) => { root.setAttribute("data-theme", t); store.set("theme", t); };
  const setLang = (l) => {
    root.lang = l; store.set("lang", l);
    const b = document.getElementById("lang-toggle");
    if (b) { b.textContent = l === "el" ? "EN" : "ΕΛ"; b.setAttribute("aria-label", l === "el" ? "Switch to English" : "Αλλαγή σε Ελληνικά"); }
    updateClock();
  };

  function updateClock() {
    const lang = root.lang === "el" ? "el-GR" : "en-GB";
    let txt;
    try {
      txt = new Intl.DateTimeFormat(lang, { hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZone: "Europe/Athens" }).format(new Date());
    } catch (e) { return; }
    document.querySelectorAll("[data-athens-time]").forEach((el) => (el.textContent = txt));
  }

  document.addEventListener("DOMContentLoaded", () => {
    setLang(root.lang === "el" ? "el" : "en");
    setInterval(updateClock, 20000);

    document.getElementById("theme-toggle")?.addEventListener("click", () =>
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark"));
    document.getElementById("lang-toggle")?.addEventListener("click", () =>
      setLang(root.lang === "el" ? "en" : "el"));

    /* Mobile nav */
    const links = document.querySelector(".links");
    const mt = document.querySelector(".menu-toggle");
    mt?.addEventListener("click", () => mt.setAttribute("aria-expanded", links.classList.toggle("open")));
    links?.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => {
      links.classList.remove("open"); mt?.setAttribute("aria-expanded", "false");
    }));

    /* Header line on scroll */
    const header = document.querySelector(".site-header");
    const onScroll = () => header?.classList.toggle("scrolled", window.scrollY > 8);
    onScroll(); window.addEventListener("scroll", onScroll, { passive: true });

    /* Missing photos -> show the flat jasmine placeholder */
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
      }), { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });
      els.forEach((el) => { if (el.dataset.delay) el.style.transitionDelay = el.dataset.delay + "ms"; io.observe(el); });
    } else els.forEach((el) => el.classList.add("in"));

    /* Menu tabs */
    const tabs = document.querySelectorAll(".menu-tabs button");
    tabs.forEach((b) => b.addEventListener("click", () => {
      tabs.forEach((x) => x.setAttribute("aria-selected", String(x === b)));
      document.querySelectorAll(".menu-group").forEach((g) =>
        g.classList.toggle("active", g.id === b.getAttribute("aria-controls")));
    }));

    /* Gallery filters */
    const filters = document.querySelectorAll(".filters button");
    const shots = [...document.querySelectorAll(".gallery .frame")];
    filters.forEach((b) => b.addEventListener("click", () => {
      filters.forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      const f = b.dataset.filter;
      shots.forEach((s) => s.classList.toggle("hide", f !== "all" && s.dataset.cat !== f));
    }));

    /* Lightbox with prev / next */
    const lb = document.querySelector(".lightbox");
    if (lb) {
      const lbImg = lb.querySelector("img");
      let list = [], idx = 0;
      const show = (i) => { idx = (i + list.length) % list.length; lbImg.src = list[idx].src; lbImg.alt = list[idx].alt; };
      const close = () => lb.classList.remove("open");
      shots.forEach((f) => {
        f.tabIndex = 0;
        const open = () => {
          list = shots.filter((s) => !s.classList.contains("hide"))
            .map((s) => s.querySelector("img")).filter((i) => i && !i.classList.contains("missing"));
          const me = f.querySelector("img");
          if (!list.includes(me)) return;
          show(list.indexOf(me)); lb.classList.add("open");
        };
        f.addEventListener("click", open);
        f.addEventListener("keydown", (e) => { if (e.key === "Enter") open(); });
      });
      lb.querySelector(".lb-close").addEventListener("click", close);
      lb.querySelector(".lb-prev").addEventListener("click", (e) => { e.stopPropagation(); show(idx - 1); });
      lb.querySelector(".lb-next").addEventListener("click", (e) => { e.stopPropagation(); show(idx + 1); });
      lb.addEventListener("click", (e) => { if (e.target === lb) close(); });
      document.addEventListener("keydown", (e) => {
        if (!lb.classList.contains("open")) return;
        if (e.key === "Escape") close();
        if (e.key === "ArrowLeft") show(idx - 1);
        if (e.key === "ArrowRight") show(idx + 1);
      });
    }

    const y = document.getElementById("year");
    if (y) y.textContent = new Date().getFullYear();
  });
})();
