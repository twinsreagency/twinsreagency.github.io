/**
 * Pruebas de comportamiento de main.js en un navegador real (Chromium).
 *
 * Uso (desde la carpeta del sitio; necesita el paquete «playwright»):
 *     node --test _tests/browser.test.js
 *
 * Las páginas se abren directamente desde el disco (file://), igual que al
 * previsualizar el sitio; las fuentes de Google se bloquean para no depender
 * de la red.
 */
"use strict";

const { test, before, after } = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");

const SITE = path.resolve(__dirname, "..");
const url = (file) => pathToFileURL(path.join(SITE, file)).href;

let browser;

before(async () => {
    browser = await chromium.launch();
});

after(async () => {
    await browser.close();
});

/** Abre una página y recoge los errores de JavaScript y de consola. */
async function open(file, { width = 1280, search = "" } = {}) {
    const context = await browser.newContext({ viewport: { width, height: 900 } });
    await context.route(/fonts\.(googleapis|gstatic)\.com/, (route) => route.abort());
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (msg) => {
        if (msg.type() === "error" && !/ERR_FAILED/.test(msg.text())) errors.push(msg.text());
    });
    await page.goto(url(file) + search);
    return { page, errors, close: () => context.close() };
}

const visibleCards = (page) => page.locator("#listado-inmuebles .property:not([hidden])").count();

test("las páginas principales cargan sin errores de JavaScript", async () => {
    for (const file of ["index.html", "es-inmuebles.html", "es-contacto.html", "ca-inici.html", "en-home.html", "es-blog-mitos-hipoteca.html"]) {
        const { errors, close } = await open(file);
        assert.deepEqual(errors, [], file);
        await close();
    }
});

test("el filtro de inmuebles muestra solo los resultados que coinciden", async () => {
    const { page, close } = await open("es-inmuebles.html");
    assert.equal(await visibleCards(page), 9);

    await page.selectOption("#filtro-operacion", "alquiler");
    assert.equal(await visibleCards(page), 2);
    assert.equal(await page.textContent("#resultados-total"), "2");
    assert.match(page.url(), /\?operacion=alquiler$/);

    await page.selectOption("#filtro-dormitorios", "5");
    assert.equal(await visibleCards(page), 0);
    assert.equal(await page.isVisible("#sin-resultados"), true);

    await page.click("#filtro-inmuebles button[type='reset']");
    await page.waitForFunction(() => document.getElementById("resultados-total").textContent === "9");
    assert.equal(await page.isVisible("#sin-resultados"), false);
    await close();
});

test("el filtro lee los parámetros de la URL e ignora valores no permitidos", async () => {
    let { page, close } = await open("es-inmuebles.html", { search: "?dormitorios=5" });
    assert.equal(await visibleCards(page), 1);
    await close();

    ({ page, close } = await open("es-inmuebles.html", { search: "?zona=<script>" }));
    assert.equal(await page.inputValue("#filtro-zona"), "");
    assert.equal(await visibleCards(page), 9);
    await close();
});

test("el formulario de contacto valida los campos obligatorios", async () => {
    const { page, close } = await open("es-contacto.html");
    await page.click("#formulario-contacto button[type='submit']");

    for (const id of ["contacto-nombre", "contacto-email", "contacto-mensaje", "contacto-privacidad"]) {
        assert.equal(await page.getAttribute("#" + id, "aria-invalid"), "true", id);
    }
    assert.equal(await page.getAttribute("#contacto-telefono", "aria-invalid"), "false");
    assert.notEqual((await page.textContent("#error-email")).trim(), "");
    assert.equal(await page.evaluate(() => document.activeElement.id), "contacto-nombre");

    await page.fill("#contacto-email", "correo-no-valido");
    await page.fill("#contacto-telefono", "abc");
    await page.click("#formulario-contacto button[type='submit']");
    assert.equal(await page.getAttribute("#contacto-email", "aria-invalid"), "true");
    assert.equal(await page.getAttribute("#contacto-telefono", "aria-invalid"), "true");

    await page.fill("#contacto-email", "cliente@example.com");
    await page.fill("#contacto-telefono", "+34 600 000 000");
    await page.click("#formulario-contacto button[type='submit']");
    assert.equal(await page.getAttribute("#contacto-email", "aria-invalid"), "false");
    assert.equal(await page.getAttribute("#contacto-telefono", "aria-invalid"), "false");
    await close();
});

test("el formulario se rellena con la referencia del inmueble solo si es válida", async () => {
    let { page, close } = await open("es-contacto.html", { search: "?ref=TRE-003" });
    assert.equal(await page.inputValue("#contacto-referencia"), "TRE-003");
    assert.equal(await page.inputValue("#contacto-asunto"), "compra");
    assert.match(await page.inputValue("#contacto-mensaje"), /TRE-003/);
    await close();

    ({ page, close } = await open("es-contacto.html", { search: "?ref=%3Cimg%3E&asunto=hack" }));
    assert.equal(await page.inputValue("#contacto-referencia"), "");
    assert.equal(await page.inputValue("#contacto-asunto"), "");
    await close();
});

test("la alerta de búsqueda recoge los criterios del filtro y valida la localidad", async () => {
    const { page, close } = await open("es-inmuebles.html");
    await page.selectOption("#filtro-tipo", "casa");
    await page.selectOption("#filtro-zona", "norte");
    assert.equal(await page.inputValue("#alerta-tipo"), "casa");
    assert.equal(await page.inputValue("#alerta-localidad"), "Zona Norte");

    /* Lo que escribe el visitante no se sobrescribe al cambiar el filtro. */
    await page.fill("#alerta-localidad", "Santa Margarida de Montbui");
    await page.selectOption("#filtro-zona", "sur");
    assert.equal(await page.inputValue("#alerta-localidad"), "Santa Margarida de Montbui");

    await page.fill("#alerta-localidad", "");
    await page.click("#formulario-alerta button[type='submit']");
    for (const id of ["alerta-localidad", "alerta-nombre", "alerta-email", "alerta-privacidad"]) {
        assert.equal(await page.getAttribute("#" + id, "aria-invalid"), "true", id);
    }
    assert.notEqual((await page.textContent("#alerta-error-localidad")).trim(), "");
    assert.equal(await page.evaluate(() => document.activeElement.id), "alerta-localidad");
    await close();
});

test("sin resultados, el aviso lleva a la alerta de búsqueda", async () => {
    const { page, close } = await open("es-inmuebles.html", { search: "?dormitorios=5&operacion=alquiler" });
    assert.equal(await page.isVisible("#sin-resultados"), true);
    assert.equal(await page.getAttribute("#sin-resultados a.btn", "href"), "#alerta");
    await close();
});

test("el menú móvil se abre, se cierra con Escape y devuelve el foco", async () => {
    const { page, close } = await open("index.html", { width: 375 });
    const toggle = page.locator(".nav-toggle");
    assert.equal(await toggle.getAttribute("aria-expanded"), "false");
    await toggle.click();
    assert.equal(await toggle.getAttribute("aria-expanded"), "true");
    await page.locator("#menu-principal .nav__link").first().waitFor({ state: "visible", timeout: 3000 });
    await page.keyboard.press("Escape");
    assert.equal(await toggle.getAttribute("aria-expanded"), "false");
    assert.equal(await page.evaluate(() => document.activeElement.classList.contains("nav-toggle")), true);
    await close();
});

test("el tema elegido se guarda y se aplica en la siguiente página", async () => {
    const { page, close } = await open("index.html");
    assert.equal(await page.getAttribute("html", "data-theme"), "light");
    await page.click(".theme-toggle");
    await page.waitForFunction(() => document.documentElement.getAttribute("data-theme") === "dark");
    await page.goto(url("es-blog.html"));
    assert.equal(await page.getAttribute("html", "data-theme"), "dark");
    await close();
});

test("los favoritos se marcan y se recuerdan", async () => {
    const { page, close } = await open("es-inmuebles.html");
    const button = page.locator(".fav-btn[data-ref='TRE-001']");
    assert.equal(await button.getAttribute("aria-pressed"), "false");
    await button.click();
    assert.equal(await button.getAttribute("aria-pressed"), "true");
    await page.reload();
    assert.equal(await page.locator(".fav-btn[data-ref='TRE-001']").getAttribute("aria-pressed"), "true");
    await close();
});

test("ninguna página se desborda horizontalmente en móvil, tableta ni escritorio", async () => {
    for (const width of [320, 768, 1280]) {
        for (const file of ["index.html", "es-inmuebles.html", "es-servicios.html", "es-contacto.html", "es-cookies.html", "ca-blog.html", "en-about.html"]) {
            const { page, close } = await open(file, { width });
            const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
            assert.ok(overflow <= 0, `${file} a ${width}px se desborda ${overflow}px`);
            await close();
        }
    }
});
