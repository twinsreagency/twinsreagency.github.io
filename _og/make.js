/** Genera og-image.jpg (1200 × 630) a partir de _og/og.html. Uso: node _og/make.js */
"use strict";
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");

(async () => {
    const browser = await chromium.launch({ args: ["--allow-file-access-from-files"] });
    const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
    await page.goto(pathToFileURL(path.join(__dirname, "og.html")).href);
    await page.evaluate(() => document.fonts.ready);
    /* JPEG: la imagen solo tiene degradados y texto, y así pesa unas ocho veces menos que en PNG. */
    await page.locator(".card").screenshot({ path: path.join(__dirname, "..", "og-image.jpg"), type: "jpeg", quality: 88 });
    await browser.close();
})();
