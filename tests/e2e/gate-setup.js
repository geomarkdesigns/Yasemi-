// Logs in to the pre-launch gate once (production runs only). The code comes from the
// ACCESS_CODE environment variable at run time and is never stored in the repository.
const { request } = require("@playwright/test");
module.exports = async () => {
  const base = process.env.BASE_URL, code = process.env.ACCESS_CODE;
  if (!base || !code) return;
  const ctx = await request.newContext({ baseURL: base, maxRedirects: 0 });
  const res = await ctx.post("/__access", { form: { code, next: "/" } });
  if (res.status() !== 303) throw new Error("gate login failed: HTTP " + res.status());
  await ctx.storageState({ path: "test-results/.gate-state.json" });
  await ctx.dispose();
};
