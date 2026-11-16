// @ts-check
const { test, expect } = require("@playwright/test");
const AxeBuilder = require("@axe-core/playwright").default;

const PAGES = ["/", "/menu", "/photos", "/visit", "/privacy", "/el", "/el/menu", "/el/photos", "/el/visit", "/el/privacy"];

/** Collect console errors and any request leaving our origin. */
function watch(page) {
  const errors = [], external = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("request", (r) => { const u = new URL(r.url()); if (!["127.0.0.1", "localhost"].includes(u.hostname) && !u.hostname.endsWith("vercel.app") && u.protocol.startsWith("http")) external.push(r.url()); });
  return { errors, external };
}

test.describe("routes & metadata", () => {
  for (const path of PAGES) {
    test(`${path} renders with correct metadata and no errors`, async ({ page }) => {
      const w = watch(page);
      const res = await page.goto(path);
      expect(res?.status()).toBe(200);
      const lang = path.startsWith("/el") ? "el" : "en";
      await expect(page.locator("html")).toHaveAttribute("lang", lang);
      await expect(page.locator("h1")).toHaveCount(1);
      expect((await page.title()).length).toBeGreaterThan(10);
      await expect(page.locator('meta[name="description"]')).toHaveAttribute("content", /.{50,}/);
      const canonical = await page.locator('link[rel="canonical"]').getAttribute("href");
      expect(canonical).toMatch(/^https:\/\/[^/]+(\/|\/.+)$/);
      if (!path.includes("privacy")) {
        await expect(page.locator('link[hreflang="en"]')).toHaveCount(1);
        await expect(page.locator('link[hreflang="el"]')).toHaveCount(1);
      }
      for (const s of await page.locator('script[type="application/ld+json"]').allTextContents()) JSON.parse(s);
      await page.waitForLoadState("networkidle");
      expect(w.errors, "console errors").toEqual([]);
      expect(w.external, "no third-party requests before consent").toEqual([]);
    });
  }

  test("unknown route returns the 404 page", async ({ page }) => {
    const res = await page.goto("/does-not-exist");
    expect(res?.status()).toBe(404);
    await expect(page.locator("h1")).toContainText("Lost on the steps");
  });

  test("no clock or placeholder prices anywhere", async ({ page }) => {
    for (const path of ["/", "/menu", "/el/menu", "/visit"]) {
      await page.goto(path);
      const text = await page.locator("body").innerText();
      expect(text).not.toContain("--:--");
      expect(text).not.toContain("€ —");
    }
  });
});

test.describe("menu", () => {
  test("renders every item with a correctly formatted price (EN & EL)", async ({ page }) => {
    await page.goto("/menu");
    const items = page.locator(".mi");
    const n = await items.count();
    expect(n).toBe(90);
    for (const p of await page.locator(".mi .price").allInnerTexts()) expect(p).toMatch(/€\d+\.\d{2}/);
    await page.goto("/el/menu");
    await expect(page.locator(".mi")).toHaveCount(n);
    for (const p of await page.locator(".mi .price").allInnerTexts()) expect(p).toMatch(/\d+,\d{2} €/);
  });

  test("search filters items, is accent-insensitive and shows an empty state", async ({ page }) => {
    await page.goto("/menu");
    await page.fill("#menu-search", "moussaka");
    await expect(page.locator(".mi:visible")).toHaveCount(1);
    await expect(page.locator(".mi:visible .mi-name")).toHaveText("Moussaka");
    await page.fill("#menu-search", "zzzz");
    await expect(page.locator("#menu-empty")).toBeVisible();
    await page.click("[data-clear-search]");
    await expect(page.locator(".mi:visible")).toHaveCount(90);
    await page.goto("/el/menu");
    await page.fill("#menu-search", "σπανακοπιτα");
    await expect(page.locator(".mi:visible .mi-name")).toHaveText(["Σπανακόπιτα"]);
  });

  test("dietary filters show only labelled items", async ({ page }) => {
    await page.goto("/menu");
    await page.click('[data-diet-filter="vegan"]');
    const vegan = page.locator(".mi:visible");
    expect(await vegan.count()).toBeGreaterThan(3);
    for (const d of await vegan.evaluateAll((els) => els.map((e) => e.getAttribute("data-diet")))) expect(d).toMatch(/vegan/);
    await page.click('[data-diet-filter="vegetarian"]');
    for (const d of await page.locator(".mi:visible").evaluateAll((els) => els.map((e) => e.getAttribute("data-diet")))) expect(d).toMatch(/vegetarian|vegan/);
    // the bacon tart must never appear under a dietary filter
    await expect(page.locator("#item-bacon-cheese-tart")).toBeHidden();
  });

  test("category navigation jumps to the section and marks it active", async ({ page }) => {
    await page.goto("/menu");
    await page.locator('.cat-nav a[data-spy="desserts"]').click();
    await expect(page.locator("#desserts h2")).toBeInViewport();
    await expect(page.locator('.cat-nav a[data-spy="desserts"]')).toHaveClass(/active/);
  });
});

test.describe("navigation & language", () => {
  test("language switch keeps the page, changes language and does not reload", async ({ page }) => {
    await page.goto("/menu");
    await page.evaluate(() => { window.__marker = 1; });
    await page.click(".lang-link");
    await expect(page).toHaveURL(/\/el\/menu$/);
    await expect(page.locator("html")).toHaveAttribute("lang", "el");
    expect(await page.evaluate(() => window.__marker)).toBe(1);
    await expect(page).toHaveTitle(/Μενού/);
    await page.goBack();
    await expect(page).toHaveURL(/\/menu$/);
    await expect(page.locator("html")).toHaveAttribute("lang", "en");
  });

  test("main navigation reaches every page", async ({ page, isMobile }) => {
    await page.goto("/");
    for (const [href, h] of [["/menu", /Coffee, pies/], ["/photos", /More photos/], ["/visit", /Half way up/], ["/", /traditional café bistrot/]]) {
      if (await page.locator(".menu-toggle").isVisible()) await page.click(".menu-toggle");
      await page.click(`.links a[href="${href}"]`);
      await expect(page).toHaveURL(new RegExp(href === "/" ? "/$" : href + "$"));
      await expect(page.locator("h1")).toContainText(h);
    }
  });

  test("light mode is default and the choice persists", async ({ page }) => {
    await page.emulateMedia({ colorScheme: "dark" });
    await page.goto("/");
    await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
    await page.click("#theme-toggle");
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await expect(page.locator("#theme-toggle")).toHaveAttribute("aria-pressed", "true");
    await page.reload();
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  });

  test("mobile menu opens, closes with Escape and returns focus", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 800 });
    await page.goto("/");
    await page.click(".menu-toggle");
    await expect(page.locator(".menu-toggle")).toHaveAttribute("aria-expanded", "true");
    await expect(page.locator('.links a[href="/menu"]')).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.locator(".menu-toggle")).toHaveAttribute("aria-expanded", "false");
    await expect(page.locator(".menu-toggle")).toBeFocused();
  });
});

test.describe("gallery", () => {
  test("filters show the right photos", async ({ page }) => {
    await page.goto("/photos");
    const all = await page.locator(".g-item").count();
    await page.click('.filters [data-filter="evening"]');
    const shown = page.locator(".g-item:visible");
    expect(await shown.count()).toBeLessThan(all);
    for (const c of await shown.evaluateAll((els) => els.map((e) => e.getAttribute("data-cat")))) expect(c).toBe("evening");
  });

  test("lightbox opens, navigates, closes with Escape and restores focus", async ({ page }) => {
    await page.goto("/photos");
    const first = page.locator(".g-open").first();
    await first.click();
    const lb = page.locator(".lightbox");
    await expect(lb).toBeVisible();
    await expect(page.locator(".lb-close")).toBeFocused();
    await expect(page.locator(".lb-count")).toHaveText(/^1 \/ \d+$/);
    await page.keyboard.press("ArrowRight");
    await expect(page.locator(".lb-count")).toHaveText(/^2 \//);
    await expect(page.locator(".lb-stage img")).toHaveJSProperty("complete", true);
    await page.keyboard.press("Escape");
    await expect(lb).toBeHidden();
    await expect(first).toBeFocused();
  });

  test("lightbox supports swipe", async ({ page }) => {
    await page.goto("/photos");
    await page.locator(".g-open").first().click();
    const box = await page.locator(".lb-stage").boundingBox();
    await page.locator(".lb-stage").dispatchEvent("pointerdown", { clientX: box.x + box.width * 0.8, clientY: box.y + 50 });
    await page.locator(".lb-stage").dispatchEvent("pointerup", { clientX: box.x + box.width * 0.2, clientY: box.y + 55 });
    await expect(page.locator(".lb-count")).toHaveText(/^2 \//);
  });
});

test.describe("visit & contact", () => {
  test("contact and directions links are correct", async ({ page }) => {
    await page.goto("/visit");
    for (const href of await page.locator('a[href^="tel:"]').evaluateAll((a) => a.map((x) => x.getAttribute("href")))) expect(href).toBe("tel:+302130417937");
    await expect(page.locator('a[href^="https://www.google.com/maps/dir/"]').first()).toHaveAttribute("href", /Mnisikleous%2023/);
    await expect(page.locator('a[href^="https://maps.apple.com/"]').first()).toHaveAttribute("href", /Mnisikleous%2023/);
  });

  test("map is not loaded until requested", async ({ page }) => {
    const google = [];
    page.on("request", (r) => { if (r.url().includes("google.com")) google.push(r.url()); });
    await page.goto("/visit");
    await page.waitForLoadState("networkidle");
    expect(google).toEqual([]);
    await expect(page.locator(".map iframe")).toHaveCount(0);
    await page.click("[data-load-map]");
    await expect(page.locator(".map iframe")).toHaveCount(1);
  });
});

test.describe("quality", () => {
  for (const path of ["/", "/menu", "/photos", "/visit", "/el", "/el/menu"]) {
    test(`${path} has no serious accessibility violations (light & dark)`, async ({ page }) => {
      await page.goto(path);
      await page.evaluate(() => document.querySelectorAll(".reveal").forEach((e) => e.classList.add("in")));
      await page.waitForTimeout(600);
      for (const theme of ["light", "dark"]) {
        await page.evaluate((t) => document.documentElement.setAttribute("data-theme", t), theme);
        await page.waitForTimeout(350);
        const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
        const bad = r.violations.filter((v) => ["serious", "critical"].includes(v.impact || ""));
        expect(bad.map((v) => `${theme}: ${v.id} → ${v.nodes.slice(0, 3).map((n) => n.target.join(" ")).join(" | ")}`)).toEqual([]);
      }
    });
  }

  test("no horizontal overflow from 320px to 1920px", async ({ page }) => {
    for (const w of [320, 360, 390, 430, 768, 1024, 1280, 1920]) {
      await page.setViewportSize({ width: w, height: 900 });
      for (const path of ["/", "/menu", "/el/menu", "/photos", "/visit"]) {
        await page.goto(path);
        const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        expect(over, `${path} @ ${w}px`).toBeLessThanOrEqual(0);
      }
    }
  });

  test("images load, have alt text and declared dimensions", async ({ page }) => {
    for (const path of ["/", "/photos"]) {
      await page.goto(path);
      await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); } });
      await page.waitForLoadState("networkidle");
      const imgs = await page.locator(".frame img").evaluateAll((els) => els.map((i) => ({
        // a gallery thumbnail may use empty alt because its visible <figcaption> carries the description
        desc: i.alt || (i.closest(".g-open") ? i.closest("figure").querySelector("figcaption")?.textContent || "" : ""),
        w: i.getAttribute("width"), ok: i.complete && i.naturalWidth > 0 })));
      for (const i of imgs) { expect(i.desc.length).toBeGreaterThan(5); expect(i.w).toBeTruthy(); expect(i.ok).toBe(true); }
    }
  });

  test("content is visible without JavaScript", async ({ browser }) => {
    const ctx = await browser.newContext({ javaScriptEnabled: false });
    const page = await ctx.newPage();
    await page.goto("/menu");
    await expect(page.locator(".mi").first()).toBeVisible();
    await page.goto("/");
    await expect(page.locator("#about-h")).toBeVisible();
    await ctx.close();
  });
});
