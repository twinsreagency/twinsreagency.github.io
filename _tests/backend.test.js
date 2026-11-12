/**
 * Pruebas del receptor de formularios (_backend/formularios.gs) sin conexión a Google:
 * el script se ejecuta en Node con versiones simuladas de los servicios de Apps Script
 * (hoja de cálculo, Gmail, caché…).
 *
 * Uso: node --test _tests/backend.test.js
 */
"use strict";

const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { execFileSync } = require("node:child_process");

const SOURCE = fs.readFileSync(path.join(__dirname, "..", "_backend", "formularios.gs"), "utf8");

/** Carga el script con servicios simulados y devuelve el contexto y lo que «envía». */
function load() {
    const sheets = {};
    const mails = [];
    const cache = new Map();
    const props = new Map();
    const triggers = [];
    function sheet(name) {
        const rows = [];
        return {
            name, rows,
            appendRow: (row) => rows.push(row.slice()),
            getLastRow: () => rows.length,
            setFrozenRows() {},
            getRange: (r, c) => ({
                insertCheckboxes() {}, setFontWeight() {},
                setFormula(formula) { rows[0] = [formula]; },
            }),
            getDataRange: () => ({ getValues: () => rows.map((r) => r.slice()) }),
            deleteRow: (i) => rows.splice(i - 1, 1),
        };
    }
    const book = {
        getSheetByName: (name) => sheets[name] || null,
        insertSheet: (name) => (sheets[name] = sheet(name)),
    };
    const context = {
        console: { log() {}, error() {} },
        SpreadsheetApp: { getActiveSpreadsheet: () => book },
        MailApp: { sendEmail: (mail) => mails.push(mail) },
        Session: { getEffectiveUser: () => ({ getEmail: () => "agencia@example.com" }) },
        LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
        CacheService: { getScriptCache: () => ({ get: (k) => cache.get(k) || null, put: (k, v) => cache.set(k, v) }) },
        PropertiesService: { getScriptProperties: () => ({ getProperty: (k) => props.get(k) || null, setProperty: (k, v) => props.set(k, v) }) },
        Utilities: { formatDate: (date) => date.toISOString().slice(0, 10) },
        ContentService: { MimeType: { JSON: "json" }, createTextOutput: (text) => ({ setMimeType: () => ({ text }) }) },
        HtmlService: { createHtmlOutput: (html) => ({ setTitle: () => ({ html }) }) },
        ScriptApp: {
            getProjectTriggers: () => triggers,
            deleteTrigger() {},
            newTrigger: (fn) => ({ timeBased: () => ({ everyDays: () => ({ atHour: () => ({ create: () => triggers.push(fn) }) }) }) }),
        },
    };
    vm.createContext(context);
    vm.runInContext(SOURCE, context);
    /* Las fechas deben crearse con el Date del propio script (otro «realm» de JavaScript). */
    return { gs: context, sheets, mails, cache, ScriptDate: vm.runInContext("Date", context) };
}

const VALUATION = {
    formulario: "formulario-valoracion", idioma: "ca", t: 9000, consentimiento: true, web: "",
    pagina: "/ca-inici.html", localidad: "Igualada", direccion: "", tipo: "casa", metros: "180",
    dormitorios: "4", nombre: "Marta Puig", telefono: "+34 600 11 22 33", email: "Marta@Example.com",
};

function post(gs, data) {
    const out = gs.doPost({ postData: { type: "text/plain", contents: JSON.stringify(data) } });
    return JSON.parse(out.text);
}

test("una valoración válida se guarda, avisa a la agencia y responde al cliente", () => {
    const { gs, sheets, mails } = load();
    assert.deepEqual(post(gs, VALUATION), { ok: true });
    const rows = sheets.Contactos.rows;
    assert.equal(rows.length, 2, "cabecera y una fila");
    const row = Object.fromEntries(gs.COLUMNAS.map((name, i) => [name, rows[1][i]]));
    assert.equal(row.Formulario, "Valoración gratuita");
    assert.equal(row.Tipo, "Casa o chalet");
    assert.equal(row["m²"], 180);
    assert.equal(row.Correo, "Marta@Example.com");
    assert.equal(row.Página, "/ca-inici.html");
    assert.equal(row.Conservar, false);

    assert.equal(mails.length, 2);
    const [notice, reply] = mails;
    assert.equal(notice.to, "agencia@example.com");
    assert.equal(notice.replyTo, "Marta@Example.com");
    assert.match(notice.subject, /Valoración gratuita — Igualada — Marta Puig/);
    assert.match(notice.body, /Tipo: Casa o chalet/);
    assert.equal(reply.to, "marta@example.com");
    assert.match(reply.subject, /Hem rebut/, "en el idioma del formulario");
    /* La respuesta automática no repite nada de lo que escribió el visitante. */
    for (const value of ["Marta", "Igualada", "600"]) assert.ok(!reply.body.includes(value), value);
});

test("el campo trampa descarta el envío sin dar pistas", () => {
    const { gs, sheets, mails } = load();
    assert.deepEqual(post(gs, { ...VALUATION, web: "http://spam.example" }), { ok: true });
    assert.equal(sheets.Contactos, undefined);
    assert.equal(mails.length, 0);
});

test("se rechaza lo rellenado demasiado rápido, sin consentimiento o con datos no válidos", () => {
    const { gs, sheets, mails } = load();
    assert.equal(post(gs, { ...VALUATION, t: 800 }).error, "rapido");
    assert.deepEqual(post(gs, { ...VALUATION, consentimiento: false }).campos, ["privacidad"]);
    assert.deepEqual(post(gs, { ...VALUATION, email: "no-es-un-correo" }).campos, ["email"]);
    assert.deepEqual(post(gs, { ...VALUATION, tipo: "castillo", metros: "5" }).campos, ["tipo", "metros"]);
    assert.deepEqual(post(gs, { ...VALUATION, nombre: "x".repeat(101) }).campos, ["nombre"]);
    assert.deepEqual(post(gs, { ...VALUATION, formulario: "otro" }).campos, ["formulario"]);
    assert.equal(sheets.Contactos, undefined);
    assert.equal(mails.length, 0);
});

test("un texto con forma de fórmula se guarda como texto", () => {
    const { gs, sheets } = load();
    post(gs, { ...VALUATION, nombre: "=IMPORTXML(\"http://x\";\"//a\")" });
    assert.equal(sheets.Contactos.rows[1][gs.COLUMNAS.indexOf("Nombre")], "'=IMPORTXML(\"http://x\";\"//a\")");
});

test("límite de envíos por correo y por día; una sola respuesta automática", () => {
    const { gs, mails } = load();
    for (let i = 0; i < 3; i++) assert.equal(post(gs, VALUATION).ok, true);
    assert.equal(post(gs, VALUATION).error, "limite");
    assert.equal(mails.filter((m) => m.to === "marta@example.com").length, 1);
    for (let i = 3; i < gs.AJUSTES.porDia; i++) assert.equal(post(gs, { ...VALUATION, email: `c${i}@example.com` }).ok, true);
    assert.equal(post(gs, { ...VALUATION, email: "otra@example.com" }).error, "limite");
});

test("sin JavaScript, el formulario normal se acepta y se responde con una página", () => {
    const { gs, sheets } = load();
    const { t, consentimiento, ...fields } = VALUATION;
    const out = gs.doPost({ postData: { type: "application/x-www-form-urlencoded", contents: "…" }, parameter: { ...fields, privacidad: "on" } });
    assert.match(out.html, /Hemos recibido su mensaje/);
    assert.equal(sheets.Contactos.rows.length, 2);
});

test("la limpieza borra las consultas de más de un año salvo las marcadas para conservar", () => {
    const { gs, sheets, ScriptDate } = load();
    gs.instalar();
    const rows = sheets.Contactos.rows;
    const old = new ScriptDate(Date.now() - 400 * 86400000);
    const conservar = gs.COLUMNAS.indexOf("Conservar");
    const row = (date, keep) => { const r = new Array(gs.COLUMNAS.length).fill(""); r[0] = date; r[conservar] = keep; return r; };
    rows.push(row(old, false), row(old, true), row(new ScriptDate(), false));
    gs.limpiar();
    assert.equal(rows.length, 3, "cabecera, la conservada y la reciente");
    assert.equal(rows[1][conservar], true);
});

test("los valores permitidos coinciden con los desplegables de la web", () => {
    const site = JSON.parse(execFileSync("python3", ["-c",
        "import json,sys; sys.dont_write_bytecode=True; sys.path.insert(0,'.'); import _build as b; " +
        "print(json.dumps({'tipo': b.SEARCH_VALUES['tipo'], 'precio': b.SEARCH_VALUES['precio'], " +
        "'dormitorios': b.SEARCH_VALUES['dormitorios'], 'operacion': b.SEARCH_VALUES['operacion'], 'asunto': b.SUBJECTS, " +
        "'labels': b._textos_es.C['search']['options'], 'subjects': b._textos_es.C['contacto']['subjects']}))"],
    { cwd: path.join(__dirname, ".."), encoding: "utf8" }));
    const { gs } = load();
    assert.deepEqual(Object.keys(gs.TIPOS), site.tipo);
    assert.deepEqual(Object.keys(gs.PRECIOS), site.precio);
    assert.deepEqual(Object.keys(gs.DORMITORIOS), site.dormitorios);
    assert.deepEqual(Object.keys(gs.OPERACIONES), site.operacion);
    assert.deepEqual(Object.keys(gs.ASUNTOS), site.asunto);
    /* Y con el mismo texto que ve el visitante en castellano. */
    assert.deepEqual(Object.values(gs.TIPOS), site.labels.tipo);
    assert.deepEqual(Object.values(gs.PRECIOS), site.labels.precio);
    assert.deepEqual(Object.values(gs.DORMITORIOS), site.labels.dormitorios);
    assert.deepEqual(Object.values(gs.OPERACIONES), site.labels.operacion);
    assert.deepEqual(Object.values(gs.ASUNTOS), site.subjects);
});
