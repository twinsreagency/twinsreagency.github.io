/**
 * Pruebas de comportamiento de main.js en un navegador real (Chromium).
 *
 * Uso (desde la carpeta del sitio; necesita el paquete «playwright»):
 *     node --test _tests/browser.test.js
 *
 * Las páginas se sirven con un pequeño servidor HTTP local, como en GitHub Pages
 * (algunas funciones del navegador, como la precarga de las tipografías, no
 * funcionan al abrir los archivos desde el disco). Las pruebas del listado, el
 * filtro y los favoritos usan una copia del sitio con inmuebles de prueba
 * (_tests/fixture.py), porque la cartera real puede estar vacía.
 */
"use strict";

const { test, before, after } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const http = require("node:http");
const os = require("node:os");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { chromium } = require("playwright");

const SITE = path.resolve(__dirname, "..");
const FIXTURE = fs.mkdtempSync(path.join(os.tmpdir(), "twins-fixture-"));
const TYPES = {
    ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
    ".png": "image/png", ".webp": "image/webp", ".ico": "image/x-icon", ".woff2": "font/woff2",
    ".xml": "application/xml", ".txt": "text/plain; charset=utf-8", ".svg": "image/svg+xml",
    ".webmanifest": "application/manifest+json", ".jpg": "image/jpeg",
};

/** Servidor estático mínimo de una carpeta; devuelve su dirección. */
function serve(root) {
    const server = http.createServer((req, res) => {
        const file = path.join(root, decodeURIComponent(new URL(req.url, "http://x").pathname));
        if (!file.startsWith(root) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
            res.writeHead(404).end();
            return;
        }
        res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
        fs.createReadStream(file).pipe(res);
    });
    return new Promise((resolve) => server.listen(0, "127.0.0.1", () => {
        resolve({ server, origin: `http://127.0.0.1:${server.address().port}` });
    }));
}

const APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbPRUEBA/exec";
let browser, site, fixture, google;
const url = (file, root = site) => `${root.origin}/${file}`;

before(async () => {
    execFileSync("python3", [path.join(__dirname, "fixture.py"), path.join(FIXTURE, "site")]);
    execFileSync("python3", [path.join(__dirname, "fixture.py"), path.join(FIXTURE, "google"), APPS_SCRIPT]);
    site = await serve(SITE);
    fixture = await serve(path.join(FIXTURE, "site"));
    google = await serve(path.join(FIXTURE, "google"));
    browser = await chromium.launch();
});

after(async () => {
    await browser.close();
    site.server.close();
    fixture.server.close();
    google.server.close();
    fs.rmSync(FIXTURE, { recursive: true, force: true });
});

/** Abre una página y recoge los errores de JavaScript y de consola. */
async function open(file, { width = 1280, search = "", fixture: useFixture = false } = {}) {
    const root = useFixture ? fixture : site;
    const context = await browser.newContext({ viewport: { width, height: 900 } });
    /* Ninguna página debe pedir nada fuera del sitio. */
    const external = [];
    await context.route((target) => !target.href.startsWith(root.origin) && /^https?:/.test(target.href), (route) => {
        external.push(route.request().url());
        route.abort();
    });
    const page = await context.newPage();
    const errors = [];
    /* Chromium avisa (como consola o como error de página) cuando aborta la animación entre
       páginas porque se navega otra vez antes de que termine (las pruebas navegan muy
       rápido): no es un error de la web. */
    const aborted = (text) => /Transition was aborted/.test(text);
    page.on("pageerror", (error) => aborted(error.message) || errors.push(error.message));
    page.on("console", (msg) => {
        if (aborted(msg.text())) return;
        if (msg.type() === "error" || (msg.type() === "warning" && /preload|Content Security Policy/i.test(msg.text()))) {
            errors.push(msg.text());
        }
    });
    await page.goto(url(file, root) + search);
    return { page, errors, external, close: () => context.close() };
}

const visibleCards = (page) => page.locator("#listado-inmuebles .property:not([hidden])").count();

test("todas las páginas cargan sin errores, sin bloqueos de la CSP y sin recursos externos", async () => {
    /* Todas las páginas con contenido (las redirecciones antiguas solo llevan a otra). */
    const pages = fs.readdirSync(SITE).filter((f) => f.endsWith(".html") &&
        !fs.readFileSync(path.join(SITE, f), "utf8").includes('http-equiv="refresh"'));
    assert.ok(pages.length > 50);
    for (const file of pages) {
        const { page, errors, external, close } = await open(file);
        await page.waitForLoadState("load");
        assert.deepEqual(errors, [], file);
        assert.deepEqual(external, [], file);
        assert.ok(await page.evaluate(() => document.fonts.check("16px Inter") && document.fonts.check("600 16px 'Playfair Display'")), `${file}: tipografías`);
        await close();
    }
});

test("la CSP bloquea el código en línea y los recursos de otros dominios", async () => {
    const { page, close } = await open("index.html");
    const result = await page.evaluate(() => new Promise((resolve) => {
        const blocked = [];
        document.addEventListener("securitypolicyviolation", (e) => blocked.push(e.violatedDirective));
        const script = document.createElement("script");
        try {
            script.textContent = "window.__inline = true;";
            document.body.appendChild(script);
        } catch (error) {
            /* Trusted Types rechaza el código antes incluso de que lo vea script-src. */
            blocked.push("trusted-types:" + error.name);
        }
        const img = document.createElement("img");
        img.src = "https://example.com/pixel.png";
        document.body.appendChild(img);
        setTimeout(() => resolve({ inline: Boolean(window.__inline), blocked }), 300);
    }));
    assert.equal(result.inline, false);
    assert.ok(result.blocked.some((d) => d.startsWith("script-src") || d.startsWith("trusted-types") ||
        d === "require-trusted-types-for"), JSON.stringify(result.blocked));
    assert.ok(result.blocked.some((d) => d.startsWith("img-src")), JSON.stringify(result.blocked));
    await close();
});

test("Trusted Types impide escribir HTML desde JavaScript", async () => {
    const { page, errors, close } = await open("index.html");
    const result = await page.evaluate(() => {
        try {
            document.body.insertAdjacentHTML("beforeend", "<img src=x>");
            return "permitido";
        } catch (error) {
            return error.name;
        }
    });
    assert.equal(result, "TypeError");
    assert.deepEqual(errors.filter((e) => !/Trusted/i.test(e)), []);
    await close();
});

test("otra web no puede mostrar la página dentro de un marco", async () => {
    /* Una página en blanco, ajena al sitio, que intenta mostrar la portada en un marco. */
    const context = await browser.newContext();
    const page = await context.newPage();
    const target = url("index.html");
    await page.setContent(`<iframe src="${target}" width="800" height="600"></iframe>`);
    await page.waitForTimeout(1000);
    const framed = page.frames().find((f) => f.url() === target);
    assert.ok(framed, "la página debía cargarse dentro del marco");
    assert.equal(await framed.evaluate(() => getComputedStyle(document.body).display), "none");
    await context.close();
});

test("sin inmuebles publicados, la web invita a crear una alerta y a vender", async () => {
    let { page, errors, close } = await open("es-inmuebles.html");
    assert.equal(await page.locator("#filtro-inmuebles").count(), 0);
    assert.equal(await page.locator(".property").count(), 0);
    assert.equal(await page.isVisible("#cartera-title"), true);
    assert.equal(await page.getAttribute(".portfolio-soon a.btn--primary", "href"), "#alerta");
    assert.equal(await page.isVisible("#formulario-alerta"), true);
    assert.deepEqual(errors, []);
    await close();

    ({ page, close } = await open("index.html"));
    assert.equal(await page.locator(".property, .search__form").count(), 0);
    await close();

    /* Una referencia en la URL no rompe el formulario aunque no haya campo de referencia. */
    ({ page, errors, close } = await open("es-contacto.html", { search: "?ref=TRE-003&asunto=venta" }));
    assert.equal(await page.locator("#contacto-referencia").count(), 0);
    assert.equal(await page.inputValue("#contacto-asunto"), "venta");
    assert.deepEqual(errors, []);
    await close();
});

test("la valoración rápida de la portada rellena el formulario completo y lleva a él", async () => {
    const { page, errors, close } = await open("index.html");
    await page.fill("#rapida-localidad", "Òdena");
    await page.selectOption("#rapida-tipo", "casa");
    await page.click("#valoracion-rapida button[type='submit']");
    await page.waitForFunction(() => document.activeElement && document.activeElement.id === "valoracion-metros");
    assert.equal(await page.inputValue("#valoracion-localidad"), "Òdena");
    assert.equal(await page.inputValue("#valoracion-tipo"), "casa");
    const top = await page.evaluate(() => document.getElementById("valoracion").getBoundingClientRect().top);
    assert.ok(Math.abs(top) < 200, `la sección de valoración queda a la vista (${top})`);
    /* El tipo también llega por la URL (enlaces de otras páginas). */
    await page.goto(url("index.html?tipo=piso&localidad=Igualada"));
    assert.equal(await page.inputValue("#valoracion-tipo"), "piso");
    assert.equal(await page.inputValue("#valoracion-localidad"), "Igualada");
    assert.deepEqual(errors, []);
    await close();
});

test("al publicar inmuebles vuelven el listado, el buscador y los destacados", async () => {
    let { page, close } = await open("index.html", { fixture: true });
    assert.equal(await page.locator(".property").count(), 4);
    assert.equal(await page.locator(".paths").count(), 0);
    assert.equal(await page.locator(".search__form").count(), 1);
    await close();

    ({ page, close } = await open("es-inmuebles.html", { fixture: true }));
    assert.equal(await page.locator("#cartera-title").count(), 0);
    assert.deepEqual(await page.locator("#filtro-zona option").allTextContents(), ["Todas", "Igualada", "Santa Margarida de Montbui"]);
    await close();
});

test("el filtro de inmuebles muestra solo los resultados que coinciden", async () => {
    const { page, close } = await open("es-inmuebles.html", { fixture: true });
    assert.equal(await visibleCards(page), 4);

    await page.selectOption("#filtro-operacion", "alquiler");
    assert.equal(await visibleCards(page), 1);
    assert.equal(await page.textContent("#resultados-total"), "1");
    assert.match(page.url(), /\?operacion=alquiler$/);

    await page.selectOption("#filtro-dormitorios", "5");
    assert.equal(await visibleCards(page), 0);
    assert.equal(await page.isVisible("#sin-resultados"), true);

    await page.click("#filtro-inmuebles button[type='reset']");
    await page.waitForFunction(() => document.getElementById("resultados-total").textContent === "4");
    assert.equal(await page.isVisible("#sin-resultados"), false);
    await close();
});

test("el filtro lee los parámetros de la URL e ignora valores no permitidos", async () => {
    let { page, close } = await open("es-inmuebles.html", { search: "?dormitorios=5", fixture: true });
    assert.equal(await visibleCards(page), 1);
    await close();

    ({ page, close } = await open("es-inmuebles.html", { search: "?zona=<script>", fixture: true }));
    assert.equal(await page.inputValue("#filtro-zona"), "");
    assert.equal(await visibleCards(page), 4);
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

test("la valoración gratuita valida sus campos y prepara el correo", async () => {
    const { page, errors, close } = await open("index.html");
    await page.click("#formulario-valoracion button[type='submit']");
    for (const id of ["localidad", "tipo", "metros", "nombre", "telefono", "email", "privacidad"]) {
        assert.equal(await page.getAttribute("#valoracion-" + id, "aria-invalid"), "true", id);
    }
    assert.equal(await page.getAttribute("#valoracion-dormitorios", "aria-invalid"), "false");
    assert.equal(await page.locator("#valoracion-direccion[aria-invalid]").count(), 0);
    assert.equal(await page.evaluate(() => document.activeElement.id), "valoracion-localidad");

    await page.fill("#valoracion-metros", "5");
    await page.fill("#valoracion-dormitorios", "99");
    await page.click("#formulario-valoracion button[type='submit']");
    assert.equal(await page.getAttribute("#valoracion-metros", "aria-invalid"), "true");
    assert.equal(await page.getAttribute("#valoracion-dormitorios", "aria-invalid"), "true");

    /* El correo se prepara con el texto escrito, codificado, sin interpretarlo como HTML. */
    await page.fill("#valoracion-localidad", "Igualada<img src=x onerror=alert(1)>");
    await page.fill("#valoracion-direccion", "Carrer Major, 1\r\nBcc: spam@example.com");
    await page.selectOption("#valoracion-tipo", "piso");
    await page.fill("#valoracion-metros", "90");
    await page.fill("#valoracion-dormitorios", "3");
    await page.fill("#valoracion-nombre", "Persona de Prueba");
    await page.fill("#valoracion-telefono", "+34 600 000 000");
    await page.fill("#valoracion-email", "cliente@example.com");
    /* Clic por script: la cabecera fija puede tapar la casilla tras desplazarse. */
    await page.$eval("#valoracion-privacidad", (box) => box.click());
    await page.waitForTimeout(3100);
    /* Se captura la dirección mailto: (Chromium la anuncia por CDP) sin abrir el correo. */
    let mailtoUrl = "";
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("Page.enable");
    cdp.on("Page.frameRequestedNavigation", (event) => {
        if (event.url.startsWith("mailto:")) mailtoUrl = event.url;
    });
    await page.$eval("#formulario-valoracion button[type='submit']", (b) => b.click());
    await page.waitForFunction(() => /correo/.test(document.querySelector("#formulario-valoracion .form-status").textContent), null, { timeout: 3000 });
    assert.ok(mailtoUrl, "No se ha preparado el enlace mailto:");
    assert.equal(await page.locator("img[src='x']").count(), 0);
    const mail = new URL(mailtoUrl);
    assert.equal(mail.pathname, "twinsreagency@gmail.com");
    assert.deepEqual([...mail.searchParams.keys()], ["subject", "body"]);
    assert.match(mail.searchParams.get("subject"), /^Valoración gratuita — Igualada/);
    /* Los saltos de línea de un campo de una línea no pueden crear líneas ni cabeceras nuevas. */
    assert.match(mail.searchParams.get("body"), /Dirección \(opcional\): Carrer Major, 1 Bcc: spam@example\.com/);
    assert.match(mail.searchParams.get("body"), /Tipo de inmueble: Piso o apartamento/);
    assert.deepEqual(errors, []);
    await close();
});

test("los botones de valoración llevan al formulario de la portada", async () => {
    const { page, close } = await open("es-inmuebles.html");
    for (const href of await page.locator(".sell__actions a.btn--primary").evaluateAll((a) => a.map((x) => x.getAttribute("href")))) {
        assert.equal(href, "index.html#valoracion");
    }
    await close();
});

test("el campo trampa bloquea el envío", async () => {
    const { page, close } = await open("es-contacto.html");
    await page.fill("#contacto-nombre", "Persona de Prueba");
    await page.fill("#contacto-email", "cliente@example.com");
    await page.fill("#contacto-mensaje", "Mensaje de prueba suficientemente largo.");
    await page.$eval("#contacto-privacidad", (box) => box.click());
    await page.evaluate(() => { document.getElementById("contacto-web").value = "spam"; });
    await page.waitForTimeout(3100);
    await page.click("#formulario-contacto button[type='submit']");
    assert.match(await page.textContent("#formulario-contacto .form-status"), /No ha sido posible enviar/);
    await close();
});

test("el formulario se rellena con la referencia del inmueble solo si es válida", async () => {
    let { page, close } = await open("es-contacto.html", { search: "?ref=TRE-003", fixture: true });
    assert.equal(await page.inputValue("#contacto-referencia"), "TRE-003");
    assert.equal(await page.inputValue("#contacto-asunto"), "compra");
    assert.match(await page.inputValue("#contacto-mensaje"), /TRE-003/);
    await close();

    ({ page, close } = await open("es-contacto.html", { search: "?ref=%3Cimg%3E&asunto=hack", fixture: true }));
    assert.equal(await page.inputValue("#contacto-referencia"), "");
    assert.equal(await page.inputValue("#contacto-asunto"), "");
    await close();
});

test("la alerta de búsqueda recoge los criterios del filtro y valida la localidad", async () => {
    const { page, close } = await open("es-inmuebles.html", { fixture: true });
    await page.selectOption("#filtro-tipo", "casa");
    await page.selectOption("#filtro-zona", "igualada");
    assert.equal(await page.inputValue("#alerta-tipo"), "casa");
    assert.equal(await page.inputValue("#alerta-localidad"), "Igualada");

    /* Lo que escribe el visitante no se sobrescribe al cambiar el filtro. */
    await page.fill("#alerta-localidad", "Òdena");
    await page.selectOption("#filtro-zona", "santa-margarida-de-montbui");
    assert.equal(await page.inputValue("#alerta-localidad"), "Òdena");

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
    const { page, close } = await open("es-inmuebles.html", { search: "?dormitorios=5&operacion=alquiler", fixture: true });
    assert.equal(await page.isVisible("#sin-resultados"), true);
    assert.equal(await page.getAttribute("#sin-resultados a.btn", "href"), "#alerta");
    await close();
});

test("cada localidad tiene su página en los tres idiomas, enlazada desde el pie y el sitemap", async () => {
    const root = path.join(FIXTURE, "site");
    const sitemap = fs.readFileSync(path.join(root, "sitemap.xml"), "utf8");
    for (const file of ["es-inmobiliaria-santa-margarida-de-montbui.html", "ca-immobiliaria-santa-margarida-de-montbui.html", "en-estate-agent-santa-margarida-de-montbui.html"]) {
        assert.ok(fs.existsSync(path.join(root, file)), file);
        assert.match(sitemap, new RegExp(file.replace(".", "\\.")), file);
    }
    const { page, errors, close } = await open("es-inmobiliaria-santa-margarida-de-montbui.html", { fixture: true });
    assert.match(await page.textContent("h1"), /Santa Margarida de Montbui/);
    assert.equal(await page.locator(".footer-areas a[href='es-inmobiliaria-igualada.html']").count(), 1);
    const areas = await page.$$eval("script[type='application/ld+json']", (nodes) => nodes.map((n) => JSON.stringify(JSON.parse(n.textContent))));
    assert.ok(areas.some((json) => /"areaServed":\{"@type":"City","name":"Santa Margarida de Montbui"/.test(json)));
    /* Solo los inmuebles de la localidad. */
    assert.equal(await page.locator(".property").count(), 2);

    /* Los dos caminos llevan la localidad a la valoración y a la alerta. */
    await page.click("a[href^='index.html?localidad=']");
    await page.waitForURL(/#valoracion$/);
    assert.equal(await page.inputValue("#valoracion-localidad"), "Santa Margarida de Montbui");
    await page.goto(url("es-inmuebles.html?localidad=Igualada#alerta", fixture));
    assert.equal(await page.inputValue("#alerta-localidad"), "Igualada");
    assert.deepEqual(errors, []);
    await close();

    /* Una localidad que no está en la lista no se copia en el formulario. */
    const other = await open("index.html", { search: "?localidad=%3Cb%3EX%3C%2Fb%3E", fixture: true });
    assert.equal(await other.page.inputValue("#valoracion-localidad"), "");
    await other.close();
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
    const { page, close } = await open("es-inmuebles.html", { fixture: true });
    const button = page.locator(".fav-btn[data-ref='TRE-001']");
    assert.equal(await button.getAttribute("aria-pressed"), "false");
    await button.click();
    assert.equal(await button.getAttribute("aria-pressed"), "true");
    await page.reload();
    assert.equal(await page.locator(".fav-btn[data-ref='TRE-001']").getAttribute("aria-pressed"), "true");
    await close();
});

test("ninguna página se desborda horizontalmente en móvil, tableta ni escritorio", async () => {
    for (const width of [320, 375, 768, 1280]) {
        for (const file of ["index.html", "ca-inici.html", "en-home.html", "es-inmuebles.html", "es-servicios.html", "es-contacto.html", "es-cookies.html", "ca-blog.html", "en-about.html"]) {
            const { page, close } = await open(file, { width });
            const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
            assert.ok(overflow <= 0, `${file} a ${width}px se desborda ${overflow}px`);
            /* Nada visible se sale por la derecha (aunque el desbordamiento esté oculto). */
            const outside = await page.evaluate(() => Array.from(document.querySelectorAll("header *, main a, main button, main input, main select"))
                .filter((el) => el.getClientRects().length && getComputedStyle(el).visibility !== "hidden" && !el.closest(".nav:not(.is-open)") && !el.closest(".field--hp") &&
                    /* Las tarjetas de una galería horizontal quedan fuera a propósito: se deslizan. */
                    !el.closest(".gallery__track"))
                .filter((el) => el.getBoundingClientRect().right > document.documentElement.clientWidth + 0.5)
                .map((el) => el.className || el.tagName));
            assert.deepEqual(outside, [], `${file} a ${width}px`);
            await close();
        }
    }
});

test("la cabecera flota como cápsula al desplazar y se oscurece sobre la sección oscura", async () => {
    const { page, errors, close } = await open("index.html");
    const header = page.locator(".site-header");
    await page.evaluate(() => window.scrollTo(0, 300));
    await page.waitForFunction(() => document.querySelector(".site-header").classList.contains("is-scrolled"));
    assert.equal(await header.evaluate((h) => h.classList.contains("is-on-dark")), false);
    /* La galería del blog es una sección oscura (azul marino). */
    await page.evaluate(() => {
        const s = document.querySelector(".gallery.dusk");
        window.scrollTo(0, s.offsetTop + 120);
    });
    await page.waitForFunction(() => document.querySelector(".site-header").classList.contains("is-on-dark"));
    /* El menú del móvil sigue ocupando toda la pantalla aunque la cabecera sea una cápsula. */
    await page.setViewportSize({ width: 390, height: 844 });
    await page.click(".nav-toggle");
    const nav = await page.locator("#menu-principal").boundingBox();
    assert.equal(Math.round(nav.width), 390);
    assert.deepEqual(errors, []);
    await close();
});

test("la galería del blog avanza con las flechas y actualiza el contador", async () => {
    const { page, errors, close } = await open("index.html");
    const gallery = page.locator(".gallery");
    await gallery.scrollIntoViewIfNeeded();
    assert.equal(await gallery.locator("[data-gallery-current]").textContent(), "01");
    assert.equal(await gallery.locator("[data-gallery-prev]").isDisabled(), true);
    await gallery.locator("[data-gallery-next]").click();
    await page.waitForFunction(() => document.querySelector("[data-gallery-current]").textContent === "02");
    assert.equal(await gallery.locator("[data-gallery-prev]").isDisabled(), false);
    assert.ok(await gallery.locator(".post-card").count() >= 10);
    assert.deepEqual(errors, []);
    await close();
});

test("las cifras de la portada terminan en su valor real", async () => {
    const { page, errors, close } = await open("index.html");
    await page.locator(".figures").scrollIntoViewIfNeeded();
    /* La cuenta empieza al aparecer y dura 1,4 s. */
    await page.waitForTimeout(2500);
    assert.deepEqual(await page.locator("[data-count]").allTextContents(), ["0", "4", "6", "3"]);
    assert.deepEqual(errors, []);
    await close();
});

test("el cambio de tema marca su transición y la retira al terminar", async () => {
    const { page, errors, close } = await open("index.html");
    await page.click(".theme-toggle");
    await page.waitForFunction(() => document.documentElement.getAttribute("data-theme") === "dark");
    await page.waitForFunction(() => !document.documentElement.classList.contains("is-theme-switch"), null, { timeout: 4000 });
    assert.deepEqual(errors, []);
    await close();
});

test("los ajustes cambian el texto, el contraste y el movimiento, y se recuerdan", async () => {
    const { page, errors, close } = await open("index.html");
    const toggle = page.locator(".settings-toggle");
    assert.equal(await toggle.isVisible(), true);
    await toggle.click();
    const panel = page.locator("#ajustes");
    assert.equal(await panel.isVisible(), true);
    assert.equal(await toggle.getAttribute("aria-expanded"), "true");

    await page.click("label[for='ajuste-texto-xl']");
    await page.click("label[for='ajuste-contraste-more']");
    await page.click("label[for='ajuste-movimiento-reduced']");
    const attrs = () => page.evaluate(() => ["data-text", "data-contrast", "data-motion"].map((a) => document.documentElement.getAttribute(a)));
    assert.deepEqual(await attrs(), ["xl", "more", "reduced"]);

    /* Escape cierra el panel y devuelve el foco al botón. */
    await page.keyboard.press("Escape");
    assert.equal(await panel.isVisible(), false);
    assert.equal(await page.evaluate(() => document.activeElement.classList.contains("settings-toggle")), true);

    /* Se aplican antes de pintar en la siguiente página; con movimiento reducido el 3D no se mueve. */
    await page.goto(url("index.html"));
    assert.deepEqual(await attrs(), ["xl", "more", "reduced"]);
    const duration = await page.evaluate(() => parseFloat(getComputedStyle(document.querySelector(".gem__cube")).animationDuration));
    assert.ok(duration < 0.01, `animación detenida (${duration}s)`);

    /* «Restablecer» vuelve a los valores de fábrica. */
    await page.click(".settings-toggle");
    await page.click(".settings__reset");
    assert.deepEqual(await attrs(), [null, null, null]);
    assert.equal(await page.evaluate(() => localStorage.getItem("twins:ajustes")), null);
    assert.deepEqual(errors, []);
    await close();
});

test("el tema automático sigue al sistema", async () => {
    const context = await browser.newContext({ colorScheme: "dark" });
    const page = await context.newPage();
    await page.goto(url("index.html"));
    assert.equal(await page.getAttribute("html", "data-theme"), "light");
    await page.click(".settings-toggle");
    await page.click("label[for='ajuste-tema-auto']");
    await page.waitForFunction(() => document.documentElement.getAttribute("data-theme") === "dark");
    await page.emulateMedia({ colorScheme: "light" });
    await page.waitForFunction(() => document.documentElement.getAttribute("data-theme") === "light");
    await page.goto(url("es-servicios.html"));
    assert.equal(await page.getAttribute("html", "data-theme"), "light");
    assert.equal(await page.evaluate(() => document.documentElement.hasAttribute("data-theme-auto")), true);
    await context.close();
});

test("se sugiere el idioma del navegador una sola vez", async () => {
    const context = await browser.newContext({ locale: "ca-ES" });
    const page = await context.newPage();
    await page.goto(url("index.html"));
    const toast = page.locator(".lang-toast");
    await toast.waitFor({ state: "visible", timeout: 4000 });
    assert.equal(await toast.getAttribute("lang"), "ca");
    assert.match(await toast.locator("a").getAttribute("href"), /ca-inici\.html$/);
    await toast.locator("button").click();
    await page.goto(url("es-servicios.html"));
    await page.waitForTimeout(1600);
    assert.equal(await page.locator(".lang-toast").count(), 0, "tras cerrarla no se vuelve a sugerir");
    /* En la versión catalana no se sugiere nada a un navegador en catalán. */
    const fresh = await browser.newContext({ locale: "ca-ES" });
    const ca = await fresh.newPage();
    await ca.goto(url("ca-inici.html"));
    await ca.waitForTimeout(1600);
    assert.equal(await ca.locator(".lang-toast").count(), 0);
    await fresh.close();
    await context.close();
});

test("en el móvil: botón de menú completo, zonas de toque cómodas y cristal que desenfoca", async () => {
    /* Sin animaciones: la aparición de los bloques los escala un instante (97 %). */
    const context = await browser.newContext({ viewport: { width: 360, height: 780 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
    const page = await context.newPage();
    await page.goto(url("index.html"));
    /* El botón del menú no se aplasta aunque haya otros botones en la cabecera. */
    const toggle = await page.locator(".nav-toggle").boundingBox();
    assert.ok(toggle.width >= 44 && toggle.height >= 44, `menú de ${toggle.width}×${toggle.height}`);
    /* Enlaces sueltos y del pie con al menos 44 px de alto (recomendación de Apple). */
    const heights = await page.evaluate(() => [...document.querySelectorAll(".footer-links a, .footer-legal a, .link-arrow")]
        .filter((a) => a.getClientRects().length && !a.closest("[hidden]"))
        .map((a) => a.getBoundingClientRect().height));
    assert.ok(heights.length > 10);
    assert.ok(Math.min(...heights) >= 43.5, `zona de toque mínima: ${Math.min(...heights)} px`);
    /* Un view-transition-name en la cabecera impediría que su cristal desenfoque la página. */
    assert.equal(await page.evaluate(() => getComputedStyle(document.querySelector(".site-header")).viewTransitionName), "none");
    /* Ningún campo del formulario por debajo de 16 px: el iPhone ampliaría la pantalla al tocarlo. */
    const small = await page.evaluate(() => [...document.querySelectorAll("input:not([type=checkbox]):not([type=radio]), select, textarea")]
        .filter((el) => el.getClientRects().length && parseFloat(getComputedStyle(el).fontSize) < 16).map((el) => el.id));
    assert.deepEqual(small, []);
    await context.close();
});

test("la casilla de consentimiento mide al menos 24 px de alto (WCAG 2.5.8)", async () => {
    for (const file of ["es-contacto.html", "index.html", "es-inmuebles.html"]) {
        const { page, close } = await open(file);
        /* offsetHeight: el tamaño real, sin la animación de entrada (que inclina y reduce
           un instante los bloques que aún no se han mostrado). */
        const heights = await page.evaluate(() => [...document.querySelectorAll("label.checkbox")]
            .filter((label) => label.getClientRects().length).map((label) => label.offsetHeight));
        assert.ok(heights.length > 0, file);
        assert.ok(Math.min(...heights) >= 24, `${file}: ${Math.min(...heights)} px`);
        await close();
    }
});

test("el manifiesto se carga sin errores y declara los iconos de 192 y 512 px", async () => {
    const { page, errors, close } = await open("ca-inici.html");
    const cdp = await page.context().newCDPSession(page);
    const { url: manifestUrl, errors: problems, manifest } = await cdp.send("Page.getAppManifest");
    assert.match(manifestUrl, /site\.webmanifest$/);
    assert.deepEqual(problems, []);
    assert.equal(manifest.name, "Twins Real Estate");
    assert.deepEqual(manifest.icons.map((icon) => icon.sizes), ["192x192", "512x512"]);
    for (const icon of manifest.icons) {
        const response = await page.request.get(icon.url);
        assert.equal(response.status(), 200, icon.url);
    }
    assert.deepEqual(errors, []);
    await close();
});

test("la web no crea cookies: tema, ajustes, idioma y favoritos van al almacenamiento local", async () => {
    const context = await browser.newContext({ locale: "ca-ES" });
    const page = await context.newPage();
    await page.goto(url("index.html"));
    await page.click(".theme-toggle");
    await page.click(".settings-toggle");
    await page.click("label[for='ajuste-texto-l']");
    await page.keyboard.press("Escape");
    await page.locator(".lang-toast a").click();
    await page.waitForURL(/ca-inici\.html$/);
    await page.goto(url("es-inmuebles.html", fixture));
    await page.locator(".fav-btn").first().click();
    for (const file of ["es-contacto.html", "es-blog.html", "es-cookies.html"]) await page.goto(url(file));
    assert.deepEqual(await context.cookies(), []);
    assert.equal(await page.evaluate(() => document.cookie), "");
    /* Solo las claves que describe la política de cookies (twins:…). */
    const keys = await page.evaluate(() => Object.keys(localStorage));
    assert.ok(keys.every((key) => /^twins:(tema|ajustes|idioma)$/.test(key)), keys.join(", "));
    await context.close();
});

test("con Google Apps Script, los formularios envían los datos y muestran la respuesta", async () => {
    const context = await browser.newContext();
    const sent = [];
    let reply = { ok: true };
    await context.route(`${APPS_SCRIPT}**`, async (route) => {
        sent.push({ type: route.request().headers()["content-type"], body: JSON.parse(route.request().postData()) });
        await route.fulfill({ status: 200, contentType: "application/json", headers: { "Access-Control-Allow-Origin": "*" }, body: JSON.stringify(reply) });
    });
    const page = await context.newPage();
    const errors = [];
    page.on("console", (msg) => msg.type() === "error" && errors.push(msg.text()));
    await page.goto(url("index.html", google));
    const fill = async () => {
        await page.fill("#valoracion-localidad", "Igualada");
        await page.selectOption("#valoracion-tipo", "casa");
        await page.fill("#valoracion-metros", "180");
        await page.fill("#valoracion-nombre", "Persona de Prueba");
        await page.fill("#valoracion-telefono", "+34 600 000 000");
        await page.fill("#valoracion-email", "cliente@example.com");
        await page.$eval("#valoracion-privacidad", (box) => { if (!box.checked) box.click(); });
    };
    const status = () => page.locator("#formulario-valoracion .form-status");
    await fill();
    await page.waitForTimeout(3100);
    await page.$eval("#formulario-valoracion button[type='submit']", (b) => b.click());
    await page.waitForFunction(() => document.querySelector("#formulario-valoracion .form-status").classList.contains("form-status--success") &&
        !document.querySelector("#formulario-valoracion button[type='submit']").disabled);
    assert.equal(sent.length, 1);
    /* Petición «simple» (sin consulta previa de CORS) con el JSON en el cuerpo. */
    assert.match(sent[0].type, /^text\/plain/);
    const body = sent[0].body;
    assert.equal(body.formulario, "formulario-valoracion");
    assert.equal(body.idioma, "es");
    assert.equal(body.tipo, "casa", "los desplegables van con su valor, que el servidor valida");
    assert.equal(body.web, "");
    assert.equal(body.consentimiento, true);
    assert.equal(body.pagina, "/index.html");
    assert.ok(body.t >= 3000, `tiempo de rellenado: ${body.t}`);
    assert.equal(await page.inputValue("#valoracion-localidad"), "", "el formulario se vacía al enviarse");

    /* Si el servidor rechaza los datos, se pide revisarlos y no se borra nada. */
    reply = { ok: false, error: "validacion", campos: ["email"] };
    await fill();
    await page.waitForTimeout(3100);
    await page.$eval("#formulario-valoracion button[type='submit']", (b) => b.click());
    await page.waitForFunction(() => document.querySelector("#formulario-valoracion .form-status").classList.contains("form-status--error"));
    assert.match(await status().textContent(), /revise|campos/i);
    assert.equal(await page.inputValue("#valoracion-localidad"), "Igualada");
    assert.deepEqual(errors, []);
    await context.close();
});

test("cada inmueble tiene su ficha: galería, datos, certificado, ubicación aproximada y visita", async () => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    await context.grantPermissions(["clipboard-read", "clipboard-write"], { origin: fixture.origin });
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (msg) => msg.type() === "error" && errors.push(msg.text()));
    await page.goto(url("es-inmueble-tre-001.html", fixture));
    assert.match(await page.textContent("h1"), /Casa con jardín en Les Comes/);
    assert.equal(await page.getAttribute(".nav__link[aria-current='page']", "href"), "es-inmuebles.html");

    /* Galería: la primera foto con prioridad, el resto diferidas; las flechas avanzan. */
    const imgs = page.locator(".photo-slide img");
    assert.equal(await imgs.count(), 2);
    assert.equal(await imgs.nth(0).getAttribute("fetchpriority"), "high");
    assert.equal(await imgs.nth(1).getAttribute("loading"), "lazy");
    assert.match(await imgs.nth(1).getAttribute("alt"), /foto 2 de 2/);
    assert.equal(await page.locator("link[rel='preload'][as='image']").count(), 1);
    await page.click(".listing-gallery [data-gallery-next]");
    await page.waitForFunction(() => document.querySelector(".listing-gallery [data-gallery-current]").textContent === "02");

    /* Certificado energético obligatorio, con la letra marcada en la escala. */
    assert.deepEqual(await page.$$eval(".energy__bar[aria-current='true']", (bars) => bars.map((b) => b.textContent)), ["C", "D"]);
    /* Ubicación aproximada: coordenadas redondeadas (unos 1 km), nunca la dirección. */
    const map = await page.getAttribute("a[href*='openstreetmap.org']", "href");
    assert.match(map, /mlat=41\.58&mlon=1\.62/);
    assert.equal(await page.locator("a[href*='youtube.com']").count(), 1);
    assert.equal(await page.locator(".listing-plan img").count(), 1);

    /* Similares: misma operación, sin el propio inmueble ni los de alquiler. */
    const similar = await page.$$eval("#similares-title ~ .grid .property, .section--alt .property", (c) => c.map((x) => x.dataset.ref));
    assert.ok(similar.length >= 1 && !similar.includes("TRE-001") && !similar.includes("TRE-003"), similar.join());

    /* Datos estructurados del anuncio. */
    const listing = (await page.$$eval("script[type='application/ld+json']", (n) => n.map((x) => JSON.parse(x.textContent))))
        .find((d) => d["@type"] === "RealEstateListing");
    assert.equal(listing.offers.price, 485000);
    assert.equal(listing.offers.priceCurrency, "EUR");
    assert.equal(listing.about["@type"], "House");
    assert.equal(listing.about.address.addressLocality, "Igualada");

    /* Compartir (copia el enlace si el sistema no tiene menú de compartir) y favorito. */
    await page.click(".share-btn");
    await page.waitForFunction(() => document.querySelector(".share-status").textContent === "Enlace copiado");
    const fav = page.locator(".listing-card .fav-btn");
    await fav.click();
    assert.equal(await fav.getAttribute("aria-pressed"), "true");

    /* «Solicitar visita» abre el contacto con la referencia y el motivo ya elegidos. */
    await page.click(".listing-card .btn--primary");
    await page.waitForURL(/es-contacto\.html/);
    assert.equal(await page.inputValue("#contacto-referencia"), "TRE-001");
    assert.equal(await page.inputValue("#contacto-asunto"), "visita");
    assert.deepEqual(errors, []);
    await context.close();

    /* Sin fotos: aviso en su lugar; certificado «en trámite»; traducción o castellano. */
    const other = await open("es-inmueble-tre-002.html", { fixture: true });
    assert.equal(await other.page.locator(".listing-gallery__placeholder").count(), 1);
    assert.match(await other.page.textContent(".energy__state"), /En trámite/);
    await other.page.goto(url("ca-immoble-tre-001.html", fixture));
    assert.match(await other.page.textContent("h1"), /Casa amb jardí a Les Comes/);
    await other.page.goto(url("en-property-tre-002.html", fixture));
    assert.match(await other.page.textContent("h1"), /Ático con terraza/);
    await other.close();
});

test("el listado filtra por superficie y se ordena por precio, con todo en la URL", async () => {
    const { page, close } = await open("es-inmuebles.html", { search: "?orden=precio-asc", fixture: true });
    const refs = () => page.$$eval("#listado-inmuebles .property:not([hidden])", (c) => c.map((x) => x.dataset.ref));
    assert.deepEqual(await refs(), ["TRE-003", "TRE-002", "TRE-001", "TRE-004"]);
    await page.selectOption("#filtro-superficie", "200");
    assert.deepEqual(await refs(), ["TRE-001", "TRE-004"]);
    assert.match(page.url(), /superficie=200&orden=precio-asc$/);
    await page.selectOption("#filtro-orden", "novedad");
    assert.deepEqual(await refs(), ["TRE-001", "TRE-004"], "novedades: la más reciente primero");
    assert.doesNotMatch(page.url(), /orden=/);
    /* Las tarjetas enlazan a su ficha. */
    assert.equal(await page.getAttribute(".property[data-ref='TRE-004'] .property__title a", "href"), "es-inmueble-tre-004.html");
    await close();
});

test("la calculadora de hipoteca calcula la cuota al escribir", async () => {
    const { page, errors, close } = await open("index.html");
    const value = (name) => page.textContent(`[data-calc='${name}']`);
    /* 250.000 €, 20 % de entrada, 3 % a 30 años: 200.000 € a 843 €/mes. */
    assert.match(await value("cuota"), /843/);
    assert.match(await value("prestamo"), /200\.000/);
    await page.fill("#calc-interes", "0");
    assert.match(await value("cuota"), /556/, "sin intereses, 200.000 / 360 meses");
    assert.match(await value("intereses"), /^0/);
    await page.fill("#calc-plazo", "99");
    assert.equal((await value("cuota")).trim(), "—", "un plazo fuera de rango no se calcula");
    assert.deepEqual(errors, []);
    await close();
});

test("las zonas enlazan a su página y las preguntas frecuentes se despliegan", async () => {
    const { page, errors, close } = await open("index.html");
    const zones = await page.$$eval(".zones .zone", (a) => a.map((x) => x.getAttribute("href")));
    assert.ok(zones.length >= 4);
    assert.ok(zones.includes("es-inmobiliaria-igualada.html"), zones.join());
    const first = page.locator(".faq__item").first();
    assert.equal(await first.getAttribute("open"), null);
    await first.locator("summary").click();
    assert.equal(await first.getAttribute("open"), "");
    assert.ok(await first.locator(".faq__answer").isVisible());
    await page.goto(url(zones[0]));
    assert.match(await page.textContent("h1"), /Igualada/);
    assert.deepEqual(errors, []);
    await close();
});
