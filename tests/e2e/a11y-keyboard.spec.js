// @ts-check
const { test, expect } = require("@playwright/test");
test.beforeEach(async ({ context }) => { if (process.env.BASE_URL) await context.route("**/__logout", (r) => r.abort()); });

test("skip link is the first Tab stop and moves focus to main content", async ({ page, isMobile }) => {
  test.skip(isMobile, "keyboard test");
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.locator(".skip")).toBeFocused();
  await expect(page.locator(".skip")).toBeInViewport();
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/#main$/);
});

test("keyboard focus is always visible (outline) on interactive elements", async ({ page, isMobile }) => {
  test.skip(isMobile, "keyboard test");
  await page.goto("/menu");
  for (let i = 0; i < 12; i++) {
    await page.keyboard.press("Tab");
    const outline = await page.evaluate(() => {
      let el = document.activeElement;
      if (el.matches(".search input")) el = el.closest(".search");          // the ring is drawn on the field's container
      const cs = getComputedStyle(el); return [el.tagName, cs.outlineStyle, parseFloat(cs.outlineWidth)];
    });
    expect(outline[1], `focused ${outline[0]} must show an outline`).not.toBe("none");
    expect(outline[2]).toBeGreaterThan(0);
  }
});

test("theme and language can be switched with the keyboard", async ({ page, isMobile }) => {
  test.skip(isMobile, "keyboard test");
  await page.goto("/visit");
  await page.locator("#theme-toggle").focus(); await page.keyboard.press("Enter");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.keyboard.press("Space");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await page.locator(".lang-link").focus(); await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/\/el\/visit$/);
  await expect(page.locator("html")).toHaveAttribute("lang", "el");
});

test("gallery photo opens with the keyboard and focus is trapped in the viewer", async ({ page, isMobile }) => {
  test.skip(isMobile, "keyboard test");
  await page.goto("/photos");
  await page.locator(".g-open").first().focus(); await page.keyboard.press("Enter");
  await expect(page.locator(".lb-close")).toBeFocused();
  for (let i = 0; i < 5; i++) {
    await page.keyboard.press("Tab");
    expect(await page.evaluate(() => !!document.activeElement.closest(".lightbox"))).toBe(true);
  }
  await page.keyboard.press("Escape");
  await expect(page.locator(".g-open").first()).toBeFocused();
});

test("mobile menu closes when tapping outside it", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 760 });
  await page.goto("/");
  await page.click(".menu-toggle");
  await expect(page.locator(".menu-toggle")).toHaveAttribute("aria-expanded", "true");
  await page.mouse.click(200, 600);
  await expect(page.locator(".menu-toggle")).toHaveAttribute("aria-expanded", "false");
  await expect(page.locator('.links a[href="/menu"]')).toBeHidden();
});

test("reduced motion: content is visible immediately, no animations or transitions", async ({ browser }) => {
  const ctx = await browser.newContext({ reducedMotion: "reduce", baseURL: test.info().project.use.baseURL, storageState: test.info().project.use.storageState });
  if (process.env.BASE_URL) await ctx.route("**/__logout", (r) => r.abort());
  const page = await ctx.newPage();
  await page.goto("/");
  const slow = await page.evaluate(() => [...document.querySelectorAll(".reveal, .hero-copy > *, .btn, .frame img")].filter((el) => {
    const cs = getComputedStyle(el);
    const t = Math.max(...cs.transitionDuration.split(",").map(parseFloat)), a = Math.max(...cs.animationDuration.split(",").map(parseFloat));
    return t > 0.01 || a > 0.01 || parseFloat(cs.opacity) < 1 && el.classList.contains("reveal");
  }).length);
  expect(slow).toBe(0);
  await ctx.close();
});

test("every icon-only control has an accessible name", async ({ page }) => {
  for (const path of ["/", "/el", "/photos", "/el/menu"]) {
    await page.goto(path);
    const unnamed = await page.evaluate(() => [...document.querySelectorAll("button, a[href], input")].filter((el) => {
      if (el.closest("[hidden]") || el.getAttribute("type") === "hidden") return false;
      const name = (el.getAttribute("aria-label") || el.textContent || el.getAttribute("title") || (el.labels && el.labels[0] && el.labels[0].textContent) || "").trim();
      return !name;
    }).map((el) => el.outerHTML.slice(0, 80)));
    expect(unnamed, path).toEqual([]);
  }
});
