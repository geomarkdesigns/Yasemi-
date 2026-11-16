// Yiasemi — theme, greeting, Athens clock, nav, reveal, menu, gallery, lightbox
(function () {
  const root = document.documentElement;
  const isEl = root.lang === "el";
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  const setTheme = (t) => {
    root.setAttribute("data-theme", t); store.set("theme", t);
    const m = document.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute("content", t === "dark" ? "#161712" : "#f6f0e6");
  };

  const athensHour = () => {
    try { return +new Intl.DateTimeFormat("en-GB", { hour: "numeric", hourCycle: "h23", timeZone: "Europe/Athens" }).format(new Date()); }
    catch (e) { return new Date().getHours(); }
  };
  const updateClock = () => {
    let txt;
    try { txt = new Intl.DateTimeFormat(isEl ? "el-GR" : "en-GB", { hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZone: "Europe/Athens" }).format(new Date()); }
    catch (e) { return; }
    document.querySelectorAll("[data-athens-time]").forEach((el) => (el.textContent = txt));
  };
  const GREET = {
    en: ["Good morning. The coffee's on.", "Good afternoon. There's a spot on the steps for you.", "Good evening. Come for a rakomelo.", "Still up? See you in the morning."],
    el: ["Καλημέρα. Ο καφές σας περιμένει.", "Καλό απόγευμα. Υπάρχει θέση στα σκαλιά για εσάς.", "Καλησπέρα. Ελάτε για ένα ρακόμελο.", "Ξύπνιοι ακόμα; Τα λέμε το πρωί."]
  };
  const updateGreeting = () => {
    const el = document.querySelector("[data-greeting]");
    if (!el) return;
    const h = athensHour();
    const i = h >= 5 && h < 12 ? 0 : h >= 12 && h < 18 ? 1 : h >= 18 && h < 24 ? 2 : 3;
    el.textContent = GREET[isEl ? "el" : "en"][i];
  };

  document.addEventListener("DOMContentLoaded", () => {
    updateClock(); updateGreeting();
    setInterval(() => { updateClock(); updateGreeting(); }, 20000);

    document.getElementById("theme-toggle")?.addEventListener("click", () =>
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark"));

    /* Mobile nav */
    const links = document.querySelector(".links");
    const mt = document.querySelector(".menu-toggle");
    mt?.addEventListener("click", () => mt.setAttribute("aria-expanded", links.classList.toggle("open")));
    links?.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => {
      links.classList.remove("open"); mt?.setAttribute("aria-expanded", "false");
    }));

    /* Header line + mobile dock on scroll */
    const header = document.querySelector(".site-header");
    const dock = document.querySelector(".dock");
    const onScroll = () => {
      header?.classList.toggle("scrolled", window.scrollY > 8);
      dock?.classList.toggle("show", window.scrollY > 420);
    };
    onScroll(); window.addEventListener("scroll", onScroll, { passive: true });

    /* Missing photos -> flat jasmine placeholder */
    document.querySelectorAll(".frame img").forEach((img) => {
      const miss = () => img.classList.add("missing");
      img.addEventListener("error", miss);   // only hide on a real load error (lazy images load later)
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

    /* Lightbox (uses the large image from data-full) */
    const lb = document.querySelector(".lightbox");
    if (lb) {
      const lbImg = lb.querySelector("img");
      let list = [], idx = 0;
      const show = (i) => {
        idx = (i + list.length) % list.length;
        const img = list[idx];
        lbImg.src = img.closest(".frame").dataset.full || img.currentSrc || img.src;
        lbImg.alt = img.alt;
      };
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
