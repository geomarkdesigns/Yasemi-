// @ts-check
const { test, expect } = require("@playwright/test");
test.skip(!process.env.BASE_URL || !process.env.ACCESS_CODE, "production gate only");
test.use({ storageState: { cookies: [], origins: [] } });   // start signed out

test("every URL is gated and noindex without the code", async ({ request }) => {
  for (const u of ["/", "/menu", "/el/visit", "/images/og.jpg", "/sitemap.xml", "/robots.txt"]) {
    const r = await request.get(u, { maxRedirects: 0 });
    expect(r.status(), u).toBe(401);
    expect(r.headers()["x-robots-tag"]).toContain("noindex");
    expect(await r.text()).not.toContain("Moussaka");
  }
});

test("wrong code is refused, right code opens the page you asked for", async ({ page }) => {
  await page.goto("/el/menu");
  await page.fill("#code", "000000"); await page.click("button[type=submit]");
  await expect(page.locator(".err")).toBeVisible();
  await page.fill("#code", process.env.ACCESS_CODE || ""); await page.click("button[type=submit]");
  await expect(page).toHaveURL(/\/el\/menu$/);
  await expect(page.locator(".mi")).toHaveCount(90);
});

test("leaving the site forgets the code", async ({ page, context }) => {
  await page.goto("/");
  await page.fill("#code", process.env.ACCESS_CODE || ""); await page.click("button[type=submit]");
  await expect(page.locator("h1")).toContainText("café bistrot");
  await page.close(); await new Promise((r) => setTimeout(r, 1500));
  const p2 = await context.newPage(); await p2.goto("/menu");
  await expect(p2.locator("#code")).toBeVisible();
});
