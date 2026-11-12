/**
 * Twins Real Estate — recepción de los formularios de la web (Google Apps Script).
 *
 * Qué hace con cada envío de la web (contacto, valoración gratuita y alerta de búsqueda):
 *   1. Lo valida de nuevo en el servidor: campos obligatorios, longitudes, correo,
 *      teléfono, valores permitidos y consentimiento.
 *   2. Lo frena si parece automático: campo trampa relleno, rellenado en menos de 3 s,
 *      más de 3 envíos por correo y hora o más de 40 envíos al día.
 *   3. Lo guarda en la hoja «Contactos» (su base de contactos; se exporta a CSV o Excel).
 *   4. Le avisa por correo, con el del cliente como «Responder a».
 *   5. Envía al cliente una respuesta automática de texto fijo, sin nada de lo que escribió
 *      (así nadie puede usar el formulario para enviar mensajes a terceros).
 *   6. Cada noche borra las consultas de más de un año que no tengan marcada la casilla
 *      «Conservar» (plazo de la política de privacidad).
 *
 * Instalación: _backend/LEEME.md. Si cambia este archivo, vuelva a pegarlo en Apps Script
 * y publique una nueva versión de la implementación.
 */

var AJUSTES = {
  aviso: "",                 // correo que recibe los avisos; vacío = el de esta cuenta de Google
  remitente: "Twins Real Estate",
  web: "https://twinsreagency.github.io",
  hoja: "Contactos",
  tiempoMinimoMs: 3000,      // menos que esto desde que se abrió el formulario = automático
  porCorreoYHora: 3,         // envíos aceptados por dirección de correo y hora
  porDia: 40,                // envíos aceptados al día (Gmail permite 100 correos diarios)
  conservarDias: 365
};

// Valores permitidos y sus textos: los mismos que los desplegables de la web en castellano
// (_build.py y _textos_es.py; un test lo comprueba).
var TIPOS = {
  piso: "Piso o apartamento", atico: "Ático", duplex: "Dúplex", casa: "Casa o chalet", rustica: "Casa rústica",
  estudio: "Estudio o loft", oficina: "Oficina", local: "Local o nave", garaje: "Garaje", trastero: "Trastero",
  terreno: "Terreno", edificio: "Edificio"
};
var ASUNTOS = {
  compra: "Compra de un inmueble", venta: "Venta de un inmueble", alquiler: "Alquiler de un inmueble",
  gestion: "Gestión de alquileres", valoracion: "Valoración de un inmueble", inversion: "Asesoramiento para inversión",
  visita: "Solicitar una cita", otro: "Otra consulta"
};
var OPERACIONES = { venta: "Compra", alquiler: "Alquiler" };
var PRECIOS = { "200000": "Hasta 200.000 €", "400000": "Hasta 400.000 €", "700000": "Hasta 700.000 €", "1000000": "Hasta 1.000.000 €" };
var DORMITORIOS = { "1": "1 o más", "2": "2 o más", "3": "3 o más", "4": "4 o más", "5": "5 o más" };

var CAMPOS = {
  nombre: { etiqueta: "Nombre", min: 2, max: 100 },
  email: { etiqueta: "Correo", tipo: "email", max: 120 },
  telefono: { etiqueta: "Teléfono", tipo: "telefono", max: 20 },
  localidad: { etiqueta: "Localidad", min: 2, max: 80 },
  direccion: { etiqueta: "Dirección", max: 150 },
  asunto: { etiqueta: "Asunto", valores: ASUNTOS },
  tipo: { etiqueta: "Tipo", valores: TIPOS },
  operacion: { etiqueta: "Operación", valores: OPERACIONES },
  metros: { etiqueta: "m²", tipo: "entero", minimo: 10, maximo: 100000 },
  dormitorios: { etiqueta: "Dormitorios", tipo: "entero", minimo: 0, maximo: 50 },
  precio: { etiqueta: "Precio máximo", valores: PRECIOS },
  referencia: { etiqueta: "Referencia", patron: /^TRE-\d{3}$/ },
  mensaje: { etiqueta: "Mensaje", min: 10, max: 2000, multilinea: true },
  comentarios: { etiqueta: "Comentarios", max: 1000, multilinea: true }
};

var FORMULARIOS = {
  "formulario-contacto": {
    titulo: "Contacto",
    obligatorios: ["nombre", "email", "mensaje"],
    opcionales: ["telefono", "asunto", "referencia"]
  },
  "formulario-valoracion": {
    titulo: "Valoración gratuita",
    obligatorios: ["localidad", "tipo", "metros", "nombre", "telefono", "email"],
    opcionales: ["direccion", "dormitorios"]
  },
  "formulario-alerta": {
    titulo: "Alerta de búsqueda",
    obligatorios: ["localidad", "nombre", "email"],
    opcionales: ["operacion", "tipo", "precio", "dormitorios", "telefono", "comentarios"]
  }
};

var COLUMNAS = ["Fecha", "Formulario", "Idioma", "Nombre", "Correo", "Teléfono", "Localidad", "Asunto",
  "Tipo", "Operación", "m²", "Dormitorios", "Precio máximo", "Dirección", "Referencia", "Mensaje",
  "Página", "Conservar"];

var RESPUESTAS = {
  es: {
    asunto: "Hemos recibido su mensaje — Twins Real Estate",
    texto: "Hola:\n\nGracias por escribirnos. Hemos recibido su mensaje y un asesor le responderá en un plazo máximo de 24 horas laborables.\n\nSi no ha sido usted quien ha escrito, puede ignorar este correo.\n\nTwins Real Estate\n"
  },
  ca: {
    asunto: "Hem rebut el vostre missatge — Twins Real Estate",
    texto: "Hola:\n\nGràcies per escriure’ns. Hem rebut el vostre missatge i un assessor us respondrà en un termini màxim de 24 hores laborables.\n\nSi no heu estat vós qui ha escrit, podeu ignorar aquest correu.\n\nTwins Real Estate\n"
  },
  en: {
    asunto: "We have received your message — Twins Real Estate",
    texto: "Hello,\n\nThank you for contacting us. We have received your message and an adviser will reply within 24 working hours.\n\nIf you did not write to us, please ignore this email.\n\nTwins Real Estate\n"
  }
};

var CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
var TELEFONO = /^[+()\d\s.-]{9,20}$/;

/* Entrada ------------------------------------------------------------------ */

/**
 * La web envía los datos como JSON en texto plano (sin la consulta previa de CORS que
 * Apps Script no admite). Sin JavaScript, el navegador envía el formulario normal y se
 * responde con una página en lugar de JSON.
 */
function doPost(e) {
  var json = Boolean(e && e.postData && e.postData.type !== "application/x-www-form-urlencoded" && e.postData.contents);
  var resultado;
  try {
    var datos = json ? JSON.parse(e.postData.contents) : (e && e.parameter) || {};
    resultado = procesar(datos, { json: json });
  } catch (error) {
    console.error(error);
    resultado = { ok: false, error: "servidor" };
  }
  if (json) {
    return ContentService.createTextOutput(JSON.stringify(resultado)).setMimeType(ContentService.MimeType.JSON);
  }
  return paginaRespuesta(resultado);
}

function doGet() {
  return ContentService.createTextOutput("Twins Real Estate: recepción de formularios activa.");
}

/* Proceso ------------------------------------------------------------------ */

function procesar(datos, opciones) {
  if (!datos || typeof datos !== "object") return { ok: false, error: "validacion" };
  var formulario = FORMULARIOS[datos.formulario];
  if (!formulario) return { ok: false, error: "validacion", campos: ["formulario"] };

  // Campo trampa: se responde como si todo fuera bien para no dar pistas al robot.
  if (texto(datos.web)) return { ok: true };
  // Tiempo mínimo de rellenado (solo lo mide la web con JavaScript).
  if (opciones.json && !(Number(datos.t) >= AJUSTES.tiempoMinimoMs)) return { ok: false, error: "rapido" };
  if (!consiente(datos.consentimiento !== undefined ? datos.consentimiento : datos.privacidad)) {
    return { ok: false, error: "validacion", campos: ["privacidad"] };
  }

  var limpio = {};
  var errores = [];
  formulario.obligatorios.concat(formulario.opcionales).forEach(function (nombre) {
    var obligatorio = formulario.obligatorios.indexOf(nombre) !== -1;
    var resultado = validar(nombre, datos[nombre], obligatorio);
    if (resultado.error) errores.push(nombre);
    else if (resultado.valor !== "") limpio[nombre] = resultado.valor;
  });
  if (errores.length) return { ok: false, error: "validacion", campos: errores };

  var idioma = RESPUESTAS[datos.idioma] ? datos.idioma : "es";
  var correo = limpio.email.toLowerCase();

  var bloqueo = LockService.getScriptLock();
  bloqueo.waitLock(10000);
  try {
    if (!dentroDelLimite(correo)) return { ok: false, error: "limite" };
    guardar(datos.formulario, formulario, idioma, limpio, texto(datos.pagina).slice(0, 200));
  } finally {
    bloqueo.releaseLock();
  }

  avisar(formulario, limpio, idioma);
  responderAlCliente(correo, idioma);
  return { ok: true };
}

/** Valor limpio de un campo, o error si no cumple sus reglas. */
function validar(nombre, bruto, obligatorio) {
  var regla = CAMPOS[nombre];
  var valor = texto(bruto);
  valor = regla.multilinea
    ? valor.replace(/[\u0000-\u0008\u000B-\u001F\u007F]/g, "")
    : valor.replace(/[\u0000-\u001F\u007F]+/g, " ");
  valor = valor.trim();
  if (!valor) return obligatorio ? { error: true } : { valor: "" };
  if (regla.max && valor.length > regla.max) return { error: true };
  if (regla.min && valor.length < regla.min) return { error: true };
  if (regla.tipo === "email" && !CORREO.test(valor)) return { error: true };
  if (regla.tipo === "telefono" && !TELEFONO.test(valor)) return { error: true };
  if (regla.tipo === "entero") {
    if (!/^\d{1,6}$/.test(valor) || Number(valor) < regla.minimo || Number(valor) > regla.maximo) return { error: true };
  }
  if (regla.valores && !Object.prototype.hasOwnProperty.call(regla.valores, valor)) return { error: true };
  if (regla.patron && !regla.patron.test(valor)) return { error: true };
  return { valor: valor };
}

function texto(valor) {
  return valor === undefined || valor === null ? "" : String(valor);
}

function consiente(valor) {
  return valor === true || valor === "true" || valor === "on";
}

/** Máximo de envíos por correo y hora y por día (protege la cuota de Gmail). */
function dentroDelLimite(correo) {
  var cache = CacheService.getScriptCache();
  var clave = "correo:" + correo;
  var porCorreo = Number(cache.get(clave) || 0);
  if (porCorreo >= AJUSTES.porCorreoYHora) return false;

  var propiedades = PropertiesService.getScriptProperties();
  var hoy = "dia:" + Utilities.formatDate(new Date(), "Europe/Madrid", "yyyy-MM-dd");
  var delDia = Number(propiedades.getProperty(hoy) || 0);
  if (delDia >= AJUSTES.porDia) return false;

  cache.put(clave, String(porCorreo + 1), 3600);
  propiedades.setProperty(hoy, String(delDia + 1));
  return true;
}

/**
 * Evita que la hoja interprete un texto como fórmula (=, +, -, @): alguien podría
 * escribir «=IMPORTXML(…)» en un campo para que la hoja lo ejecute.
 */
function celda(valor) {
  var t = texto(valor);
  return /^[=+\-@\t\r]/.test(t) ? "'" + t : t;
}

function etiquetaDe(nombre, valor) {
  var regla = CAMPOS[nombre];
  return regla.valores && valor ? regla.valores[valor] : valor || "";
}

function hojaContactos() {
  var libro = SpreadsheetApp.getActiveSpreadsheet();
  var hoja = libro.getSheetByName(AJUSTES.hoja);
  if (!hoja) {
    hoja = libro.insertSheet(AJUSTES.hoja);
    hoja.appendRow(COLUMNAS);
    hoja.setFrozenRows(1);
  }
  return hoja;
}

function guardar(id, formulario, idioma, d, pagina) {
  var hoja = hojaContactos();
  hoja.appendRow([
    new Date(), formulario.titulo, idioma, celda(d.nombre), celda(d.email), celda(d.telefono),
    celda(d.localidad), etiquetaDe("asunto", d.asunto), etiquetaDe("tipo", d.tipo),
    etiquetaDe("operacion", d.operacion), d.metros ? Number(d.metros) : "", d.dormitorios ? Number(d.dormitorios) : "",
    etiquetaDe("precio", d.precio), celda(d.direccion), celda(d.referencia), celda(d.mensaje || d.comentarios),
    celda(pagina), false
  ]);
  hoja.getRange(hoja.getLastRow(), COLUMNAS.length).insertCheckboxes();
}

function destinatario() {
  return AJUSTES.aviso || Session.getEffectiveUser().getEmail();
}

function avisar(formulario, d, idioma) {
  var lineas = [];
  Object.keys(CAMPOS).forEach(function (nombre) {
    if (d[nombre] !== undefined) lineas.push(CAMPOS[nombre].etiqueta + ": " + etiquetaDe(nombre, d[nombre]));
  });
  lineas.push("Idioma: " + idioma, "", "Responda a este correo para contestar directamente al cliente.");
  var detalle = d.localidad || etiquetaDe("asunto", d.asunto) || d.referencia || "";
  MailApp.sendEmail({
    to: destinatario(),
    replyTo: d.email,
    name: AJUSTES.remitente,
    subject: ("[Web] " + formulario.titulo + (detalle ? " — " + detalle : "") + " — " + d.nombre).slice(0, 180),
    body: lineas.join("\n")
  });
}

/** Una sola respuesta automática por correo cada 6 horas, con texto fijo. */
function responderAlCliente(correo, idioma) {
  var cache = CacheService.getScriptCache();
  var clave = "respuesta:" + correo;
  if (cache.get(clave)) return;
  cache.put(clave, "1", 21600);
  var respuesta = RESPUESTAS[idioma];
  MailApp.sendEmail({
    to: correo,
    replyTo: destinatario(),
    name: AJUSTES.remitente,
    subject: respuesta.asunto,
    body: respuesta.texto + AJUSTES.web + "\n"
  });
}

function paginaRespuesta(resultado) {
  var mensaje = resultado.ok
    ? "Gracias. Hemos recibido su mensaje y le responderemos lo antes posible."
    : "No hemos podido enviar su mensaje. Revise los datos o escríbanos por correo.";
  var html = "<!doctype html><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">" +
    "<title>Twins Real Estate</title><body style=\"font-family:sans-serif;max-width:36rem;margin:3rem auto;padding:0 1rem\">" +
    "<h1>Twins Real Estate</h1><p>" + mensaje + "</p><p><a href=\"" + AJUSTES.web + "\" target=\"_top\">Volver a la web</a></p></body>";
  return HtmlService.createHtmlOutput(html).setTitle("Twins Real Estate");
}

/* Mantenimiento ------------------------------------------------------------ */

/** Borra las consultas de más de AJUSTES.conservarDias sin la casilla «Conservar». */
function limpiar() {
  var hoja = hojaContactos();
  var filas = hoja.getDataRange().getValues();
  var limite = new Date(Date.now() - AJUSTES.conservarDias * 86400000);
  var conservar = COLUMNAS.indexOf("Conservar");
  for (var i = filas.length - 1; i >= 1; i--) {
    var fecha = filas[i][0];
    if (fecha instanceof Date && fecha < limite && filas[i][conservar] !== true) hoja.deleteRow(i + 1);
  }
}

/**
 * Ejecútela una vez desde el editor (botón «Ejecutar»): crea la hoja, el resumen de
 * contactos por mes y la limpieza diaria, y pide los permisos necesarios.
 */
function instalar() {
  var hoja = hojaContactos();
  hoja.getRange(1, 1, 1, COLUMNAS.length).setFontWeight("bold");
  var libro = SpreadsheetApp.getActiveSpreadsheet();
  if (!libro.getSheetByName("Resumen")) {
    var resumen = libro.insertSheet("Resumen");
    resumen.getRange("A1").setFormula(
      // Apps Script escribe las fórmulas en inglés y con comas, sea cual sea el idioma de la hoja.
      "=QUERY(" + AJUSTES.hoja + "!A:B, \"select year(A), month(A)+1, B, count(B) where A is not null " +
      "group by year(A), month(A)+1, B label year(A) 'Año', month(A)+1 'Mes', B 'Formulario', count(B) 'Contactos'\", 1)");
  }
  ScriptApp.getProjectTriggers().forEach(function (trigger) {
    if (trigger.getHandlerFunction() === "limpiar") ScriptApp.deleteTrigger(trigger);
  });
  ScriptApp.newTrigger("limpiar").timeBased().everyDays(1).atHour(3).create();
  console.log("Listo. Avisos a: " + destinatario());
}
