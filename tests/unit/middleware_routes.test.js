// Route classification used by the production middleware (node tests/unit/middleware_routes.test.js)
const fs = require("fs"), os = require("os"), path = require("path"), assert = require("assert");
const src = fs.readFileSync(path.join(__dirname, "../../deploy/middleware.js"), "utf8")
  .replace("export default async function middleware", "async function middleware") + "\nmodule.exports = { isKnown };";
const f = path.join(os.tmpdir(), "yiasemi_mw_" + process.pid + ".js"); fs.writeFileSync(f, src);
const { isKnown } = require(f);
const known = ["/", "/el", "/menu", "/photos", "/visit", "/credits", "/privacy", "/el/menu", "/el/photos", "/el/visit", "/el/credits", "/el/privacy",
  "/menu/", "/el/", "/images/og.jpg", "/images/favicon.svg", "/fonts/gfs-didot-greek.woff2", "/css/style.css", "/js/main.js",
  "/sitemap.xml", "/robots.txt", "/manifest.webmanifest", "/favicon.ico"];
const unknown = ["/nope", "/el/nope", "/menu.html", "/index.html", "/el/menu/extra", "/images/../x", "/.env", "/elmenu", "/admin", "/images/", "/404"];
known.forEach((p) => assert.ok(isKnown(p), "should be known: " + p));
unknown.forEach((p) => assert.ok(!isKnown(p), "should be 404: " + p));
fs.unlinkSync(f);
console.log(`middleware routes OK (${known.length} known, ${unknown.length} unknown)`);
