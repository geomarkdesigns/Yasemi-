// @ts-check
const { defineConfig, devices } = require("@playwright/test");

const BASE = process.env.BASE_URL || "http://127.0.0.1:8765";

const GATED = !!(process.env.BASE_URL && process.env.ACCESS_CODE);

module.exports = defineConfig({
  globalSetup: require.resolve("./tests/e2e/gate-setup.js"),
  testDir: "tests/e2e",
  timeout: 45_000,
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"]],
  use: { baseURL: BASE, trace: "off", ...(GATED ? { storageState: "test-results/.gate-state.json" } : {}) },
  webServer: process.env.BASE_URL ? undefined : {
    command: "python3 tools/serve.py 8765",
    url: BASE,
    reuseExistingServer: true,
  },
  projects: [
    { name: "desktop-chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile-chromium", use: { ...devices["Pixel 7"] } },
    { name: "mobile-webkit-viewport", use: { ...devices["Desktop Chrome"], viewport: { width: 390, height: 844 }, isMobile: false, hasTouch: true } },
  ],
});
