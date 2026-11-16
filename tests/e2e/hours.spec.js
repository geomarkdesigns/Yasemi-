// @ts-check
// Opening hours UI with SAMPLE data injected only inside this test (the real site has no hours yet).
const { test, expect } = require("@playwright/test");
const { execFileSync } = require("child_process");
const path = require("path");

const SAMPLE = {
  weekly: [{ days: [0, 1, 2, 3, 4, 5, 6], opens: "09:00", closes: "19:00" }],
  seasons: [{ name: { en: "Winter", el: "Χειμώνας" }, from: "11-01", to: "03-31", weekly: [{ days: [0, 1, 2, 3, 4, 5, 6], opens: "10:00", closes: "18:00" }] }],
  special: [{ date: "2099-12-25", closed: true, note: { en: "Christmas", el: "Χριστούγεννα" } }, { date: "2000-01-01", closed: true }],
  notice: { en: "Closed for renovation until Friday", el: "Κλειστά για ανακαίνιση έως την Παρασκευή", until: "2099-01-01" },
};
function render(lang) {
  const py = `import sys, json, datetime; sys.path.insert(0, ".")
import build
build.HOURS = build.validate_hours(json.loads(sys.argv[1])); build.LANG = sys.argv[2]; build.TODAY = "2050-01-01"
print(build.hours_block())`;
  return execFileSync("python3", ["-c", py, JSON.stringify(SAMPLE), lang], { cwd: path.resolve(__dirname, "../.."), encoding: "utf-8" });
}

test.skip(!!process.env.BASE_URL, "uses the local build");

for (const lang of ["el", "en"]) {
  test(`hours (${lang}): seasons, special dates, notice and Athens 'today'`, async ({ page }) => {
    const html = render(lang);
    const url = lang === "el" ? "/el/visit" : "/visit";
    await page.route("**" + url, async (route) => {
      const res = await route.fetch();
      const body = (await res.text()).replace(/<dt>(Opening hours|Ωράριο)<\/dt><dd>[\s\S]*?<\/dd>/, (m) => m.replace(/<dd>[\s\S]*<\/dd>/, `<dd>${html}</dd>`));
      await route.fulfill({ response: res, body });
    });
    // Fix the clock: 2026-12-02 23:30 UTC = 2026-12-03 01:30 in Athens (Thursday) -> winter season, Thursday row.
    await page.clock.setFixedTime(new Date("2026-12-02T23:30:00Z"));
    await page.goto(url);
    await expect(page.locator(".hours")).toHaveCount(2);
    await expect(page.locator('table[data-season="11-01|03-31"]')).not.toHaveAttribute("data-inactive", "");
    await expect(page.locator('table[data-season="base"]')).toHaveAttribute("data-inactive", "");
    const today = page.locator('table[data-season="11-01|03-31"] tr[aria-current="date"]');
    await expect(today).toHaveAttribute("data-dow", "3");           // Thursday in Athens (it is still Wednesday in UTC)
    await expect(today.locator("td")).toHaveText("10:00–18:00");
    await expect(page.locator(".special-hours li")).toHaveCount(1);  // past date (2000) is not rendered
    await expect(page.locator(".special-hours")).toContainText(lang === "el" ? "Κλειστά · Χριστούγεννα" : "Closed · Christmas");
    await expect(page.locator(".hours-notice")).toBeVisible();
  });
}
