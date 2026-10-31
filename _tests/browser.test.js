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

let browser, site, fixture;
const url = (file, root = site) => `${root.origin}/${file}`;

before(async () => {
    execFileSync("python3", [path.join(__dirname, "fixture.py"), path.join(FIXTURE, "site")]);
    site = await serve(SITE);
    fixture = await serve(path.join(FIXTURE, "site"));
    browser = await chromium.launch();
});

after(async () => {
    await browser.close();
    site.server.close();
    fixture.server.close();
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
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (msg) => {
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

test("sin inmuebles, la portada ofrece un camino a propietarios y otro a compradores", async () => {
    const { page, close } = await open("index.html");
    const links = await page.locator(".paths .feature__more a").evaluateAll((a) => a.map((x) => x.getAttribute("href")));
    assert.deepEqual(links, ["#valoracion", "es-inmuebles.html#alerta"]);
    assert.equal(await page.getAttribute(".hero3d__actions a.btn--primary", "href"), "#valoracion");
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
    await page.selectOption("#filtro-zona", "montbui");
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
    for (const file of ["es-inmobiliaria-montbui.html", "ca-immobiliaria-montbui.html", "en-estate-agent-montbui.html"]) {
        assert.ok(fs.existsSync(path.join(root, file)), file);
        assert.match(sitemap, new RegExp(file.replace(".", "\\.")), file);
    }
    const { page, errors, close } = await open("es-inmobiliaria-montbui.html", { fixture: true });
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

test("la escena de la villa avanza por los pasos al desplazarse y es estática sin animaciones", async () => {
    const { page, errors, close } = await open("index.html");
    const scene = page.locator(".villa-scene");
    assert.equal(await page.locator(".villa .vb").count(), 7);
    assert.equal(await scene.locator(".vstep").count(), 4);
    for (const [fraction, step] of [[0.1, "0"], [0.6, "2"], [0.95, "3"]]) {
        await page.evaluate((f) => {
            const s = document.querySelector(".villa-scene");
            window.scrollTo(0, s.offsetTop + (s.offsetHeight - window.innerHeight) * f);
        }, fraction);
        await page.waitForFunction((expected) => document.querySelector(".villa-scene").getAttribute("data-active") === expected, step);
    }
    /* Solo el paso activo muestra su texto. */
    await scene.locator(".vstep:nth-child(4) .vstep__text").waitFor({ state: "visible", timeout: 3000 });
    assert.equal(await page.evaluate(() => getComputedStyle(document.querySelector(".vstep:nth-child(1) .vstep__text")).opacity), "0");
    assert.deepEqual(errors, []);
    await close();

    /* Con «reducir movimiento», la sección es normal y se leen los cuatro pasos. */
    const context = await browser.newContext({ reducedMotion: "reduce" });
    const still = await context.newPage();
    await still.goto(url("index.html"));
    const height = await still.evaluate(() => document.querySelector(".villa-scene").offsetHeight / window.innerHeight);
    assert.ok(height < 2, `la sección no debe alargarse (mide ${height.toFixed(1)} pantallas)`);
    for (let i = 1; i <= 4; i++) {
        assert.equal(await still.locator(`.vstep:nth-child(${i}) .vstep__text`).isVisible(), true);
    }
    await context.close();
});

test("la cabecera flota como cápsula al desplazar y se oscurece sobre la sección oscura", async () => {
    const { page, errors, close } = await open("index.html");
    const header = page.locator(".site-header");
    await page.evaluate(() => window.scrollTo(0, 300));
    await page.waitForFunction(() => document.querySelector(".site-header").classList.contains("is-scrolled"));
    assert.equal(await header.evaluate((h) => h.classList.contains("is-on-dark")), false);
    await page.evaluate(() => {
        const s = document.querySelector(".villa-scene");
        window.scrollTo(0, s.offsetTop + window.innerHeight);
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

test("los paneles de servicios se expanden con el cursor y el foco", async () => {
    const { page, errors, close } = await open("index.html");
    const panels = page.locator(".panel");
    assert.equal(await panels.count(), 4);
    await page.locator(".panels").scrollIntoViewIfNeeded();
    const width = (i) => panels.nth(i).evaluate((el) => el.getBoundingClientRect().width);
    await page.waitForTimeout(1200);
    assert.ok(await width(0) > await width(1) * 1.5, "sin cursor, el primer panel está abierto");
    await panels.nth(2).hover();
    await page.waitForTimeout(1200);
    assert.ok(await width(2) > await width(0) * 1.5, "el panel con el cursor se abre");
    /* Con el teclado: el enlace del cuarto panel lo abre. */
    await page.mouse.move(5, 5);
    await panels.nth(3).locator("a").focus();
    await page.waitForTimeout(1200);
    assert.ok(await width(3) > await width(0) * 1.5, "el panel con el foco se abre");
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

    /* Se aplican antes de pintar en la siguiente página; con movimiento reducido la villa es estática. */
    await page.goto(url("index.html"));
    assert.deepEqual(await attrs(), ["xl", "more", "reduced"]);
    const screens = await page.evaluate(() => document.querySelector(".villa-scene").offsetHeight / window.innerHeight);
    assert.ok(screens < 2, `la escena no debe alargarse (${screens.toFixed(1)} pantallas)`);

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
