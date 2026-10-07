"""Generador del sitio estático multilingüe de Twins Real Estate.

Uso (desde la carpeta del sitio):
    python3 _build.py

Todos los archivos del sitio están en una única carpeta, sin subcarpetas:
    index.html          portada en castellano (idioma principal)
    es-*.html           resto de páginas en castellano
    ca-*.html           páginas en catalán
    en-*.html           páginas en inglés
    styles.css, main.js, imágenes e iconos

Los textos se editan en _textos_es.py, _textos_ca.py y _textos_en.py; este
fichero solo contiene la estructura y los datos comunes. Después de modificar
cualquier texto, vuelva a ejecutar el script. Los archivos que empiezan por
«_» no se publican en GitHub Pages (ver _config.yml).
"""
import hashlib
import html
import json
import os
import re
import sys
from urllib.parse import urlencode, urlparse

sys.dont_write_bytecode = True  # no crear la carpeta __pycache__ en el sitio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _textos_ca  # noqa: E402
import _textos_en  # noqa: E402
import _textos_es  # noqa: E402

# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------
SITE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dirección pública del sitio, sin barra final (p. ej. "https://www.twinsrealestate.es"
# o "https://usuario.github.io/repositorio").
# Mientras esté vacío no se generan las etiquetas canonical ni hreflang, que
# requieren direcciones absolutas.
SITE_URL = "https://twinsreagency.github.io"

# Ruta pública de la raíz del sitio («/» o «/repositorio/»). La usa la página 404,
# que el servidor muestra en cualquier dirección (p. ej. /carpeta/antigua.html),
# donde las rutas relativas no encontrarían styles.css, main.js ni los enlaces.
SITE_PATH = urlparse(SITE_URL).path.rstrip("/") + "/"

LANGS = [_textos_es.C, _textos_ca.C, _textos_en.C]

EMAIL = "twinsreagency@gmail.com"

# Datos del titular para el aviso legal y la política de privacidad (art. 10 LSSI).
# Mientras un dato esté vacío, su fila no se muestra. Complételos cuando los tenga:
# la ley exige el titular, el NIF, el domicilio y, en Cataluña, el número del
# Registro de Agentes Inmobiliarios; los datos registrales, solo si es una sociedad.
OWNER = {
    "titular": "",
    "nif": "",
    "domicilio": "",
    "registro_mercantil": "",
    "registro_agentes": "",
}
OG_IMAGE = "og-image.jpg"  # imagen para compartir en redes (1200 × 630); se genera con _og/make.js
# Agencia en línea con base en Igualada (sin oficina abierta al público).
LOCALITY = "Igualada"
INSTAGRAM_URL = "https://www.instagram.com/twins.real.estate.agency/"
INSTAGRAM_HANDLE = "@twins.real.estate.agency"



# Caducidad de /.well-known/security.txt (RFC 9116 recomienda menos de un año).
# Un test avisa cuando falte menos de un mes: basta con adelantarla y regenerar.
SECURITY_TXT_EXPIRES = "2027-10-01T00:00:00Z"


def form_endpoint():
    """Dirección del servicio de formularios (CONFIG.endpoint de main.js), o "" si los
    formularios abren el programa de correo. main.js es la única fuente de este dato:
    de él dependen la CSP y el texto de la política de privacidad."""
    with open(os.path.join(SITE_DIR, "main.js"), encoding="utf-8") as fh:
        match = re.search(r'^\s*endpoint:\s*"([^"]*)"', fh.read(), re.M)
    if not match:
        raise SystemExit("No se encuentra CONFIG.endpoint en main.js")
    endpoint = match.group(1)
    if endpoint and urlparse(endpoint).scheme != "https":
        raise SystemExit("CONFIG.endpoint debe ser una dirección https://")
    return endpoint

def csp(meta=True):
    """Política de seguridad de contenidos: solo recursos del propio sitio, sin código
    en línea. Se publica como <meta> en cada página (GitHub Pages no permite enviar
    cabeceras) y como cabecera en _headers (Netlify / Cloudflare Pages). Las directivas
    frame-ancestors y upgrade-insecure-requests solo funcionan como cabecera.
    Los bloques JSON-LD no son scripts ejecutables y la CSP no los bloquea."""
    endpoint = form_endpoint()
    service = f" {urlparse(endpoint).scheme}://{urlparse(endpoint).netloc}" if endpoint else ""
    rules = ["default-src 'self'", "script-src 'self'", "style-src 'self'", "img-src 'self' data:",
             "font-src 'self'", f"connect-src 'self'{service}", f"form-action 'self' mailto:{service}",
             "base-uri 'self'", "object-src 'none'"]
    if not meta:
        rules += ["frame-ancestors 'none'", "upgrade-insecure-requests"]
    return "; ".join(rules)


# --------------------------------------------------------------------------
# Iconos (trazo, 24x24, heredan el color del texto)
# --------------------------------------------------------------------------
ICONS = {
    "home": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    "building": '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/><path d="M10 21v-3h4v3"/>',
    "penthouse": '<path d="M4 21V8l8-5 8 5v13"/><path d="M4 12h16"/><path d="M9 16h2M13 16h2"/><path d="M9 21v-2h6v2"/>',
    "villa": '<path d="M2 12 12 4l10 8"/><path d="M4 10.5V20h16v-9.5"/><path d="M2 20h20"/><rect x="7" y="13" width="4" height="4"/><path d="M14 20v-5h3v5"/>',
    "tree": '<path d="M12 21v-6"/><path d="M12 3 6 11h3l-4 5h14l-4-5h3z"/>',
    "loft": '<rect x="3" y="4" width="18" height="17" rx="1"/><path d="M3 10h18"/><path d="M9 4v6M15 4v6"/><path d="M7 15h4v6"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="m10.8 12.2 8.2-8.2"/><path d="m16 6 2 2"/><path d="m14 8 2 2"/>',
    "chart": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "document": '<path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h6"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="17" rx="1"/><path d="M9 4V3h6v1"/><path d="M9 11h6M9 15h4"/>',
    "shield": '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7"/><path d="M21.5 20a6.5 6.5 0 0 0-4-6"/>',
    "award": '<circle cx="12" cy="9" r="6"/><path d="m8.5 14-1.5 7 5-3 5 3-1.5-7"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
    "handshake": '<path d="m11 17 2 2a1.4 1.4 0 0 0 2-2"/><path d="m14 14 2.5 2.5a1.4 1.4 0 0 0 2-2l-3.9-3.9a2 2 0 0 0-2.8 0l-.9.9a1.4 1.4 0 0 1-2-2L11.7 6.7a3 3 0 0 1 3.6-.4l.5.3a3 3 0 0 0 2.1.3L21 6"/><path d="m21 5 1 9-2 2"/><path d="M3 5 2 14l6.5 6.5a1.4 1.4 0 0 0 2-2"/><path d="M3 5h8"/>',
    "pen": '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    "map-pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="m3 7 9 6 9-6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="1"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "bed": '<path d="M3 18V6"/><path d="M3 14h18v4"/><path d="M21 14v-2a3 3 0 0 0-3-3h-7v5"/><circle cx="7" cy="11" r="2"/>',
    "bath": '<path d="M4 12h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4z"/><path d="M6 12V5a2 2 0 0 1 4 0"/><path d="m7 19-1 2M17 19l1 2"/>',
    "area": '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
    "heart": '<path d="M12 20s-7-4.4-9.2-8.6A5 5 0 0 1 12 6a5 5 0 0 1 9.2 5.4C19 15.6 12 20 12 20z"/>',
    "arrow-right": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "arrow-left": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "arrow-up": '<path d="M12 19V5M6 11l6-6 6 6"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
    "lightbulb": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    "sofa": '<path d="M4 11V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v3"/><path d="M2 13a2 2 0 0 1 4 0v2h12v-2a2 2 0 0 1 4 0v5H2z"/><path d="M5 18v2M19 18v2"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "moon": '<path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/>',
    "euro": '<path d="M17 6.5A7 7 0 1 0 17 17.5"/><path d="M4 10h9M4 14h9"/>',
}


def icon(name, extra=""):
    cls = "icon" + (" " + extra if extra else "")
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            f'{ICONS[name]}</svg>')


ARROW = icon("arrow-right", "icon-arrow")

# --------------------------------------------------------------------------
# Datos comunes (no traducibles)
# --------------------------------------------------------------------------
PAGES = ["index.html", "propiedades.html", "servicios.html", "nosotros.html", "blog.html", "contacto.html"]

SEARCH_VALUES = {
    "operacion": ["venta", "alquiler"],
    "tipo": ["piso", "atico", "duplex", "casa", "rustica", "estudio",   # viviendas
             "oficina", "local", "garaje", "trastero", "terreno", "edificio"],
    "zona": None,  # se calcula a partir de los inmuebles publicados (ver places())
    "precio": ["200000", "400000", "700000", "1000000"],
    "dormitorios": ["1", "2", "3", "4", "5"],
}

# Inmuebles publicados. Mientras la lista esté vacía, la web muestra en su lugar
# la invitación a crear una alerta de búsqueda y a solicitar una valoración, y no
# se generan el filtro, el buscador de la portada ni los destacados. En cuanto se
# añada el primer inmueble, todo ello vuelve a aparecer solo. Ejemplo:
#     dict(ref="TRE-001", op="venta", type="piso", zone="igualada", price=185000,
#          beds=3, baths=2, area=90, icon="building"),
# op: "venta" o "alquiler"; type: uno de SEARCH_VALUES["tipo"]; zone: clave de TOWNS;
# icon: "home", "building", "penthouse", "villa", "tree" o "loft". Su título,
# ubicación y etiqueta van en «properties» de los tres archivos de textos.
PROPERTIES = []

# Localidades donde trabajamos, con su nombre oficial (igual en los tres idiomas). La
# clave se usa en la dirección de su página y en el campo «zone» de los inmuebles:
#     "igualada": "Igualada",
#     "santa-margarida-de-montbui": "Santa Margarida de Montbui",
# Cada localidad tiene su página («Vender o comprar vivienda en …») en los tres idiomas,
# con el texto propio que se escriba en «towns» de _textos_*.py, y aparece en el pie,
# en el sitemap y como sugerencia en la valoración y la alerta. El filtro «Localidad»
# de «Inmuebles» solo muestra las que tienen algún inmueble publicado.
TOWNS = {}

# Fotos reales del equipo para «Nosotros» (nunca de bancos de imágenes). Mientras la
# lista esté vacía, la página mantiene su diseño actual. Para añadir una:
#   1. Prepare la foto con «python3 _fotos.py original.jpg equipo», que guarda en fotos/
#      equipo.webp y equipo.jpg optimizadas e indica su tamaño.
#   2. Añádala aquí: ("equipo", ancho, alto).
#   3. Escriba su texto alternativo y su pie en «nosotros» → «photos» de los tres archivos de textos.
TEAM_PHOTOS = []

SERVICES = [("compraventa", "key"), ("alquiler", "home"), ("gestion-alquileres", "clipboard"),
            ("inversion", "chart"), ("valoracion", "search"), ("asesoramiento-juridico", "shield")]

COMMITMENT_ICONS = ["document", "euro", "lock", "pen"]
VALUE_ICONS = ["eye", "award", "handshake", "users"]
PILLAR_ICONS = ["shield", "eye", "users"]

SUBJECTS = ["compra", "venta", "alquiler", "gestion", "valoracion", "inversion", "visita", "otro"]

POSTS = [  # (slug, icono, fecha ISO, minutos de lectura); el primero es el destacado del blog
    ("gastos-impuestos-vender-piso-cataluna", "euro", "2026-10-07", 7),
    ("documentos-vender-vivienda", "document", "2026-10-07", 6),
    ("preparar-vivienda-vender", "home", "2026-10-07", 5),
    ("comprar-o-alquilar-en-2026", "compass", "2026-01-15", 6),
    ("senales-revalorizacion-zona", "chart", "2026-01-12", 5),
    ("guia-primera-vivienda", "document", "2026-01-08", 7),
    ("preparar-vivienda-alquiler", "key", "2026-01-02", 5),
    ("que-revisar-contrato-arras", "shield", "2025-12-28", 6),
    ("tendencias-interiorismo-2026", "sofa", "2025-12-20", 4),
    ("mitos-hipoteca", "euro", "2025-12-14", 6),
]


# --------------------------------------------------------------------------
# Nombres de archivo y contexto de página
# --------------------------------------------------------------------------
def minify_css(css):
    """Versión compacta de styles.css: sin comentarios ni espacios innecesarios. Es
    conservadora a propósito: no toca «:» (en «a :hover» el espacio importa) ni los
    textos entre comillas que contengan comas."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};])\s*", r"\1", css)
    css = re.sub(r",\s+(?=[^\"']*(?:[\"'][^\"']*[\"'][^\"']*)*$)", ",", css)
    return css.replace(";}", "}").strip() + "\n"


def minify_js(js):
    """Versión compacta de main.js: quita los comentarios que ocupan líneas enteras, la
    sangría y las líneas vacías. No reescribe el código, así que no puede alterarlo."""
    out, in_comment = [], False
    for line in js.splitlines():
        stripped = line.strip()
        if in_comment:
            in_comment = "*/" not in stripped
            continue
        if stripped.startswith("/*"):
            in_comment = "*/" not in stripped
            continue
        if not stripped or stripped.startswith("//"):
            continue
        out.append(stripped)
    text = "\n".join(out) + "\n"
    if "`" in text:
        raise SystemExit("main.js: las plantillas con ` no están previstas en minify_js()")
    return text


def build_assets():
    """Genera styles.min.css y main.min.js, que son los que enlazan las páginas.
    Se editan siempre styles.css y main.js."""
    for source, target, minify in (("styles.css", "styles.min.css", minify_css), ("main.js", "main.min.js", minify_js)):
        with open(os.path.join(SITE_DIR, source), encoding="utf-8") as fh:
            text = minify(fh.read())
        with open(os.path.join(SITE_DIR, target), "w", encoding="utf-8") as fh:
            fh.write(text)


def versioned(asset):
    """Añade una huella del contenido para que el navegador no use copias antiguas en caché."""
    with open(os.path.join(SITE_DIR, asset), "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()[:10]
    return f"{asset}?v={digest}"


def filename(lang, page):
    """Nombre del archivo de una página lógica («index.html», «blog/<clave>.html»…) en un idioma."""
    if page == "404.html":
        return page
    name = page[:-len(".html")]
    if name.startswith("blog/"):
        slug = "blog-" + lang["posts"][name[len("blog/"):]]["slug"]
    elif name.startswith("zona/"):  # página de una localidad de TOWNS
        slug = lang["slugs"]["zona"] + "-" + name[len("zona/"):]
    else:
        slug = lang["slugs"][name]
    if lang["code"] == "es" and name == "index":
        return "index.html"
    return f"{lang['code']}-{slug}.html"


class Ctx:
    """Página concreta en un idioma concreto."""

    def __init__(self, lang, page):
        self.L = lang
        self.current = page
        self.is_404 = page == "404.html"
        self.root = SITE_PATH if self.is_404 else ""   # prefijo de enlaces y recursos

    def page(self, name):
        return self.root + filename(self.L, name)

    def asset(self, name):
        return self.root + name

    def translation(self, other):
        return self.root + filename(other, "index.html" if self.is_404 else self.current)

    @property
    def file(self):
        return filename(self.L, self.current)


def url(file):
    """Dirección absoluta de un archivo del sitio; la portada se publica como «/»."""
    return f"{SITE_URL}/" + ("" if file == "index.html" else file)


def form_legal(ctx, purpose):
    """Información básica de protección de datos de un formulario, con su finalidad."""
    return resolve(ctx, ctx.L["contacto"]["legal_html"].replace("%%PURPOSE%%", purpose))


def resolve(ctx, text):
    """Sustituye las marcas de los textos por enlaces y datos reales."""
    return (text.replace("%%PRIVACY%%", ctx.page("privacidad.html"))
                .replace("%%COOKIES%%", ctx.page("cookies.html"))
                .replace("%%EMAIL%%", EMAIL))


# --------------------------------------------------------------------------
# Utilidades de formato
# --------------------------------------------------------------------------
def esc(text):
    return html.escape(text, quote=True)


def json_ld(data):
    """Bloque de datos estructurados. Se escapa «<» para que ningún texto pueda cerrar
    la etiqueta <script> ni abrir otra (p. ej. un «</script>» en un título)."""
    text = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return f'\n    <script type="application/ld+json">{text}</script>'


def price(L, value):
    if L["code"] == "en":
        return f"€{value:,}"
    return f"{value:,}".replace(",", ".") + " €"


def count(n, forms):
    return f"{n} {forms[0] if n == 1 else forms[1]}"


def options(values, labels, placeholder):
    if len(values) != len(labels):
        raise SystemExit(f"Opciones y textos no coinciden: {values} / {labels}")
    out = [f'<option value="">{placeholder}</option>']
    out += [f'<option value="{esc(v)}">{esc(label)}</option>' for v, label in zip(values, labels)]
    return "".join(out)


def place_name(slug):
    """Nombre oficial de una localidad de TOWNS."""
    if slug in TOWNS:
        return TOWNS[slug]
    raise SystemExit(f"Localidad «{slug}» sin nombre: añádala a TOWNS en _build.py")


def places():
    """Localidades con algún inmueble publicado, por orden alfabético."""
    slugs = {p["zone"] for p in PROPERTIES}
    return sorted(((s, place_name(s)) for s in slugs), key=lambda item: item[1].casefold())


def field_options(L, name):
    """Valores y textos de un desplegable del buscador."""
    if name == "zona":
        found = places()
        return [s for s, _ in found], [label for _, label in found]
    return SEARCH_VALUES[name], L["search"]["options"][name]


# --------------------------------------------------------------------------
# Plantilla común
# --------------------------------------------------------------------------
def head(ctx, title, description, noindex=False, extra=""):
    L = ctx.L
    # La marca se añade al final del título salvo que lo haga superar los 60 caracteres
    # que suelen mostrar los buscadores (p. ej. en los títulos largos del blog).
    branded = f"{title} | Twins Real Estate"
    full_title = title if title.startswith("Twins") or len(branded) > 60 else branded
    alternates = ""
    if SITE_URL and not ctx.is_404:
        links = [f'\n    <meta property="og:url" content="{url(ctx.file)}">',
                 f'\n    <link rel="canonical" href="{url(ctx.file)}">']
        for other in LANGS:
            links.append(f'\n    <link rel="alternate" hreflang="{other["lang"]}" href="{url(ctx.translation(other))}">')
        links.append(f'\n    <link rel="alternate" hreflang="x-default" href="{url(ctx.translation(LANGS[0]))}">')
        alternates = "".join(links)
    og_type = "article" if ctx.current.startswith("blog/") else "website"
    og_image = ""
    if SITE_URL:
        og_image = (f'\n    <meta property="og:image" content="{url(OG_IMAGE)}">'
                    '\n    <meta property="og:image:type" content="image/jpeg">'
                    '\n    <meta property="og:image:width" content="1200">'
                    '\n    <meta property="og:image:height" content="630">'
                    f'\n    <meta property="og:image:alt" content="{esc(L["ui"]["og_image_alt"])}">')
    robots = "noindex" if noindex else "index, follow"
    return f"""<!DOCTYPE html>
<html lang="{L['lang']}">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Security-Policy" content="{csp()}">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <title>{esc(full_title)}</title>
    <meta name="description" content="{esc(description)}">
    <meta name="robots" content="{robots}">
    <meta name="theme-color" content="#f2ede4">
    <meta name="color-scheme" content="light dark">
    <meta name="format-detection" content="telephone=no">
    <meta property="og:type" content="{og_type}">
    <meta property="og:locale" content="{L['locale']}">
    <meta property="og:site_name" content="Twins Real Estate">
    <meta property="og:title" content="{esc(full_title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta name="twitter:card" content="summary_large_image">{og_image}{alternates}
    <link rel="icon" href="{ctx.asset('favicon.ico')}" sizes="any">
    <link rel="icon" href="{ctx.asset('favicon-32.png')}" type="image/png" sizes="32x32">
    <link rel="apple-touch-icon" href="{ctx.asset('apple-touch-icon.png')}">
    <link rel="preload" href="{ctx.asset('fonts/inter-latin.woff2')}" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="{ctx.asset('fonts/playfair-display-600-latin.woff2')}" as="font" type="font/woff2" crossorigin>
    <script src="{ctx.asset(versioned('theme.js'))}"></script>
    <link rel="stylesheet" href="{ctx.asset(versioned('styles.min.css'))}">
    <script src="{ctx.asset(versioned('main.min.js'))}" defer></script>{extra}
</head>"""


def logos(ctx, small, extra=""):
    """Logotipo para fondo oscuro y para fondo claro (el CSS muestra el del tema
    activo), en WebP con PNG como alternativa. «small»: versión de 52 px para la
    cabecera y el pie."""
    suffix, size = ("-sm", 'width="26" height="34"') if small else ("", 'width="151" height="200"')
    out = []
    for cls, name in (("logo--on-dark", "logo-icon"), ("logo--on-light", "logo-icon-dark")):
        out.append(f'<picture class="{cls}"><source srcset="{ctx.asset(f"{name}{suffix}.webp")}" type="image/webp">'
                   f'<img src="{ctx.asset(f"{name}{suffix}.png")}" alt="" {size}{extra}></picture>')
    return "".join(out)


def brand(ctx):
    return f"""<a class="brand" href="{ctx.page('index.html')}" aria-label="{esc(ctx.L['ui']['home_aria'])}">
                {logos(ctx, small=True)}
                <span>Twins <span class="brand__sub">Real Estate</span></span>
            </a>"""


def lang_switch(ctx):
    items = []
    for other in LANGS:
        current = ' aria-current="true"' if other["code"] == ctx.L["code"] else ""
        items.append(
            f'<li><a href="{ctx.translation(other)}" hreflang="{other["lang"]}" lang="{other["lang"]}" '
            f'aria-label="{other["label"]}"{current}>{other["abbr"]}</a></li>')
    return (f'<ul class="lang-switch" aria-label="{esc(ctx.L["ui"]["lang_aria"])}">'
            + "".join(items) + "</ul>")


def site_header(ctx, active):
    ui = ctx.L["ui"]
    items = []
    for name in PAGES:
        current = ' aria-current="page"' if name == active else ""
        items.append(f'<li><a class="nav__link" href="{ctx.page(name)}"{current}>{ui["nav"][name]}</a></li>')
    links = "\n                    ".join(items)
    return f"""
<body>
    <a class="skip-link" href="#contenido">{ui['skip']}</a>

    <header class="site-header">
        <div class="container">
            {brand(ctx)}
            <nav class="nav" id="menu-principal" aria-label="{esc(ui['nav_aria'])}">
                <ul class="nav__list">
                    {links}
                </ul>
                {lang_switch(ctx)}
                <a class="btn btn--primary nav__cta" href="{ctx.page('contacto.html')}?asunto=visita#formulario">{ui['cta_nav']}</a>
            </nav>
            <button class="theme-toggle" type="button" aria-label="{esc(ui['theme_to_dark'])}" data-label-light="{esc(ui['theme_to_light'])}" data-label-dark="{esc(ui['theme_to_dark'])}">{icon('sun', 'icon-sun')}{icon('moon', 'icon-moon')}</button>
            <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="menu-principal" aria-label="{esc(ui['menu_open'])}" data-label-open="{esc(ui['menu_open'])}" data-label-close="{esc(ui['menu_close'])}">
                <span></span><span></span><span></span>
            </button>
        </div>
    </header>
"""


def footer_areas(ctx):
    """Enlaces del pie a las páginas de cada localidad."""
    if not TOWNS:
        return ""
    T = ctx.L["town_page"]
    links = "".join(f'\n                    <li><a href="{ctx.page(f"zona/{slug}.html")}">{esc(name)}</a></li>'
                    for slug, name in sorted(TOWNS.items(), key=lambda item: item[1].casefold()))
    return f"""            <nav class="footer-areas" aria-labelledby="zonas-title">
                <h2 class="footer-title" id="zonas-title">{T['footer_title']}</h2>
                <ul>{links}
                </ul>
            </nav>"""


def site_footer(ctx):
    L, ui = ctx.L, ctx.L["ui"]
    nav_links = "".join(f'\n                        <li><a href="{ctx.page(n)}">{ui["nav"][n]}</a></li>' for n in PAGES)
    service_links = "".join(
        f'\n                        <li><a href="{ctx.page("servicios.html")}#{sid}">{label}</a></li>'
        for (sid, _), label in zip(SERVICES, L["footer_services"]))
    legal_links = "".join(f'\n                    <a href="{ctx.page(n)}">{label}</a>' for n, label in ui["legal"].items())
    return f"""
    <footer class="site-footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-brand">
                    {brand(ctx)}
                    <p>{ui['footer_about']}</p>
                    <div class="social">
                        <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer" aria-label="{esc(ui['instagram_aria'])}">{icon('instagram')}</a>
                        <a href="mailto:{EMAIL}" aria-label="{esc(ui['mail_aria'])}">{icon('mail')}</a>
                    </div>
                </div>
                <nav aria-label="{esc(ui['footer_nav_aria'])}">
                    <h2 class="footer-title">{ui['footer_nav_title']}</h2>
                    <ul class="footer-links">{nav_links}
                    </ul>
                </nav>
                <nav aria-label="{esc(ui['footer_services_title'])}">
                    <h2 class="footer-title">{ui['footer_services_title']}</h2>
                    <ul class="footer-links">{service_links}
                    </ul>
                </nav>
                <div>
                    <h2 class="footer-title">{ui['footer_contact_title']}</h2>
                    <ul class="footer-contact">
                        <li>{icon('mail')}<a href="mailto:{EMAIL}">{EMAIL}</a></li>
                        <li>{icon('instagram')}<a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer">{INSTAGRAM_HANDLE}<span class="visually-hidden"> {ui['new_tab']}</span></a></li>
                        <li>{icon('clock')}<span>{ui['hours_html']}</span></li>
                    </ul>
                </div>
            </div>
{footer_areas(ctx)}
            <div class="footer-bottom">
                <p>© <span data-year>2026</span> Twins Real Estate. {ui['rights']}</p>
                <nav class="footer-legal" aria-label="{esc(ui['legal_aria'])}">{legal_links}
                </nav>
            </div>
        </div>
    </footer>

    <button class="back-to-top" type="button" aria-label="{esc(ui['back_top'])}">{icon('arrow-up')}</button>
</body>
</html>
"""


def page_hero(ctx, title, text, crumbs, extra="", obj="rings"):
    """crumbs: lista de (texto, página) tras «Inicio»; el último es la página actual."""
    ui = ctx.L["ui"]
    trail = [f'<li><a href="{ctx.page("index.html")}">{ui["home"]}</a></li>']
    for label, target in crumbs[:-1]:
        trail.append(f'<li><a href="{ctx.page(target)}">{label}</a></li>')
    trail.append(f'<li aria-current="page">{crumbs[-1][0]}</li>')
    ld = ""
    if SITE_URL:
        items = [(ui["home"], ctx.page("index.html"))] + [(label, ctx.page(t)) for label, t in crumbs[:-1]]
        items.append((crumbs[-1][0], ctx.file))
        ld = json_ld({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i, "name": name, "item": url(file)}
                                for i, (name, file) in enumerate(items, start=1)],
        }).replace("\n    ", "\n            ")
    text_html = f'\n            <p class="page-hero__text">{text}</p>' if text else ""
    return f"""
    <section class="page-hero" data-scroll="view">
        <div class="page-hero__panes" aria-hidden="true"><span></span><span></span><span></span></div>
        <div class="container">{object_3d(obj)}
            <nav class="breadcrumb" aria-label="{esc(ui['breadcrumb_aria'])}">
                <ol>{''.join(trail)}</ol>
            </nav>{ld}{extra}
            <h1 class="page-hero__title">{title}</h1>{text_html}
        </div>
    </section>
"""


def cta(ctx, title, text, secondary=None):
    ui = ctx.L["ui"]
    secondary = secondary or (f"mailto:{EMAIL}", ui["cta_mail"])
    return f"""
        <section class="cta" aria-labelledby="cta-title" data-scroll="view">
            <div class="cta__glow" aria-hidden="true"></div>
            <div class="container reveal">
                <h2 class="cta__title" id="cta-title">{title}</h2>
                <p class="cta__text">{text}</p>
                <div class="cta__actions">
                    <a class="btn btn--primary" href="{ctx.page('contacto.html')}?asunto=visita#formulario">{ui['cta_primary']} {ARROW}</a>
                    <a class="btn btn--outline-light" href="{secondary[0]}">{secondary[1]}</a>
                </div>
            </div>
        </section>
"""


def write(ctx, title, description, active, body, extra_head="", noindex=False):
    doc = (head(ctx, title, description, noindex, extra_head) + site_header(ctx, active) +
           f'\n    <main id="contenido" tabindex="-1">{body}\n    </main>\n' + site_footer(ctx))
    with open(os.path.join(SITE_DIR, ctx.file), "w", encoding="utf-8") as fh:
        fh.write(doc)


# --------------------------------------------------------------------------
# Componentes
# --------------------------------------------------------------------------
def valuation_link(ctx):
    """Destino de los botones «Solicitar una valoración»: el formulario de la portada."""
    return "#valoracion" if ctx.current == "index.html" else ctx.page("index.html") + "#valoracion"


def search_fields(ctx, prefix, names=None, indent=20):
    """Desplegables del buscador (todos o solo los indicados en «names»)."""
    S = ctx.L["search"]
    pad = " " * indent
    out = []
    for name in names or SEARCH_VALUES:
        label, placeholder = S["fields"][name]
        values, labels = field_options(ctx.L, name)
        out.append(f"""
{pad}<div class="field">
{pad}    <label for="{prefix}-{name}">{label}</label>
{pad}    <select id="{prefix}-{name}" name="{name}">{options(values, labels, placeholder)}</select>
{pad}</div>""")
    return "".join(out)


def property_card(ctx, p):
    L, P = ctx.L, ctx.L["prop"]
    title, location, badge = L["properties"][p["ref"]]
    badge_html = f'<span class="property__badge">{badge}</span>' if badge else ""
    suffix = f' <small>{P["per_month"]}</small>' if p["op"] == "alquiler" else ""
    operation = P["rent"] if p["op"] == "alquiler" else P["sale"]
    return f"""
                <article class="card property reveal tilt" data-operacion="{p['op']}" data-tipo="{p['type']}" data-zona="{p['zone']}" data-precio="{p['price']}" data-dormitorios="{p['beds']}">
                    <div class="property__media">
                        {icon(p['icon'])}
                        {badge_html}
                        <button class="fav-btn" type="button" data-ref="{p['ref']}" aria-pressed="false" aria-label="{esc(P['fav'].format(title))}">{icon('heart')}</button>
                        <span class="property__ref">{P['ref']} {p['ref']}</span>
                    </div>
                    <div class="property__body">
                        <p class="property__operation">{operation}</p>
                        <p class="property__price">{price(L, p['price'])}{suffix}</p>
                        <h3 class="property__title">{title}</h3>
                        <p class="property__location">{icon('map-pin')}{location}</p>
                        <ul class="property__features" aria-label="{esc(P['features_aria'])}">
                            <li>{icon('bed')}{count(p['beds'], P['bed'])}</li>
                            <li>{icon('bath')}{count(p['baths'], P['bath'])}</li>
                            <li>{icon('area')}{p['area']} m²</li>
                        </ul>
                        <a class="link-arrow property__cta" href="{ctx.page('contacto.html')}?ref={p['ref']}#formulario">{P['request']} {icon('arrow-right')}<span class="visually-hidden"> {ctx.L['ui']['about']} {esc(title)}</span></a>
                    </div>
                </article>"""


def feature_card(icon_name, title, text, extra="", attrs=""):
    return f"""
                <article class="card feature reveal tilt"{attrs}>
                    <div class="feature__icon">{icon(icon_name)}</div>
                    <h3 class="feature__title">{title}</h3>
                    <p class="feature__text">{text}</p>{extra}
                </article>"""


def faces(names, extra=None):
    extra = extra or {}
    return "".join(f'<span class="face face--{n}">{extra.get(n, "")}</span>' for n in names)


WALLS = ["front", "back", "left", "right"]


def house_box():
    """Casa con ventana y tejado a dos aguas (usada en la portada y en «Inmuebles»)."""
    window = '<span class="window"><i></i><i></i><i></i><i></i></span>'
    return (f'<span class="box box--house">{faces(WALLS, {"front": window})}'
            '<span class="gable gable--front"></span><span class="gable gable--back"></span>'
            '<span class="slope slope--left"></span><span class="slope slope--right"></span></span>')


def model_3d():
    """Modelo 3D decorativo del logotipo (torre y casa) construido con CSS."""
    return f"""
                <div class="scene" aria-hidden="true">
                    <div class="scene__float">
                        <div class="model">
                            <span class="orbit orbit--1"></span>
                            <span class="orbit orbit--2"></span>
                            <span class="floor"></span>
                            <span class="box box--tower">{faces(WALLS + ["top"])}</span>
                            {house_box()}
                        </div>
                    </div>
                </div>"""


def object_3d(kind):
    """Objeto 3D decorativo para la cabecera de las páginas interiores."""
    if kind == "house":
        inner = house_box()
    elif kind == "cube":
        inner = (f'<span class="box box--cube">{faces(WALLS + ["top", "bottom"])}</span>'
                 f'<span class="box box--core">{faces(WALLS + ["top", "bottom"])}</span>')
    elif kind == "twins":
        inner = (f'<span class="box box--tower">{faces(WALLS + ["top"])}</span>'
                 f'<span class="box box--tower-b">{faces(WALLS + ["top"])}</span>')
    elif kind == "sale":
        inner = ('<span class="floor"></span>' + house_box() +
                 f'<span class="sign"><span class="sign__post"></span><span class="sign__board">{icon("key")}</span></span>')
    elif kind == "pages":
        inner = '<span class="sheet sheet--1"></span><span class="sheet sheet--2"></span><span class="sheet sheet--3"></span>'
    else:  # rings
        inner = '<span class="ring ring--1"></span><span class="ring ring--2"></span><span class="ring ring--3"></span>'
    core = '<span class="obj3d__core"></span>' if kind == "rings" else ""
    return (f'\n            <div class="obj3d obj3d--{kind}" aria-hidden="true"><span class="obj3d__glow"></span>{core}'
            f'<div class="obj3d__tilt"><div class="obj3d__spin">{inner}</div></div></div>')


def section_header(eyebrow, title, title_id, lead=None):
    eyebrow_html = f'\n                    <span class="eyebrow">{eyebrow}</span>' if eyebrow else ""
    lead_html = f'\n                    <p class="section-lead">{lead}</p>' if lead else ""
    return f"""
                <header class="section-header reveal">{eyebrow_html}
                    <h2 class="section-title" id="{title_id}">{title}</h2>{lead_html}
                    <div class="divider"></div>
                </header>"""


def sell_section(ctx, alt=True):
    """Invitación a los propietarios que quieren vender, con una casa 3D y su cartel."""
    T, ui = ctx.L["sell"], ctx.L["ui"]
    checks = "".join(f'\n                        <li>{icon("check")}{text}</li>' for text in T["checks"])
    return f"""
        <section class="section{' section--alt' if alt else ''} sell" aria-labelledby="vender-title" data-scroll="view">
            <div class="container split">
                <div class="split__visual reveal tilt">
                    <div class="split__frame sell__frame">{object_3d("sale")}
                        <p class="split__quote">{T['badge']}</p>
                    </div>
                </div>
                <div class="reveal">
                    <span class="eyebrow">{T['eyebrow']}</span>
                    <h2 class="section-title" id="vender-title">{T['title']}</h2>
                    <div class="prose-block">
                        <p>{T['text']}</p>
                    </div>
                    <ul class="check-list">{checks}
                    </ul>
                    <div class="sell__actions">
                        <a class="btn btn--primary" href="{valuation_link(ctx)}">{T['btn']} {ARROW}</a>
                        <a class="btn btn--outline" href="mailto:{EMAIL}">{ui['cta_mail']}</a>
                    </div>
                </div>
            </div>
        </section>
"""


def alert_section(ctx):
    """Alerta de búsqueda: el visitante indica la localidad y el inmueble que busca."""
    L = ctx.L
    T, C, ui = L["alert"], L["contacto"], L["ui"]
    lab = C["labels"]
    checks = "".join(f'\n                        <li>{icon("check")}{text}</li>' for text in T["checks"])
    towns = "".join(f'<option value="{esc(name)}"></option>' for name in sorted(TOWNS.values(), key=str.casefold))

    def error(name):
        return f'<p class="field__error" id="alerta-error-{name}" aria-live="polite"></p>'

    return f"""
        <section class="section section--alt" id="alerta" aria-labelledby="alerta-title">
            <div class="container split alert">
                <div class="reveal">
                    <span class="eyebrow">{T['eyebrow']}</span>
                    <h2 class="section-title" id="alerta-title">{T['title']}</h2>
                    <div class="prose-block">
                        <p>{T['text']}</p>
                    </div>
                    <ul class="check-list">{checks}
                    </ul>
                </div>

                <div class="card form-card reveal">
                    <h3 class="form-card__title">{T['form_title']}</h3>
                    <p class="form-card__lead">{C['form_lead']}</p>
                    <form class="lead-form" id="formulario-alerta" action="mailto:{EMAIL}" method="post" enctype="text/plain" novalidate data-mail-subject="{esc(T['mail_subject'])}" data-subject-field="localidad">
                        <div class="form-grid">
                            <div class="field field--full">
                                <label for="alerta-localidad">{T['localidad']}</label>
                                <input id="alerta-localidad" name="localidad" type="text" list="alerta-localidades" autocomplete="address-level2" maxlength="80" required placeholder="{esc(T['localidad_placeholder'])}" aria-describedby="alerta-error-localidad">
                                <datalist id="alerta-localidades">{towns}</datalist>
                                {error('localidad')}
                            </div>{search_fields(ctx, 'alerta', ['operacion', 'tipo', 'precio', 'dormitorios'], indent=28)}
                            <div class="field">
                                <label for="alerta-nombre">{lab['nombre']}</label>
                                <input id="alerta-nombre" name="nombre" type="text" autocomplete="name" maxlength="100" required aria-describedby="alerta-error-nombre">
                                {error('nombre')}
                            </div>
                            <div class="field">
                                <label for="alerta-email">{lab['email']}</label>
                                <input id="alerta-email" name="email" type="email" autocomplete="email" maxlength="120" required aria-describedby="alerta-error-email">
                                {error('email')}
                            </div>
                            <div class="field field--full">
                                <label for="alerta-telefono">{lab['telefono']}</label>
                                <input id="alerta-telefono" name="telefono" type="tel" autocomplete="tel" inputmode="tel" maxlength="20" aria-describedby="alerta-error-telefono">
                                {error('telefono')}
                            </div>
                            <div class="field field--full">
                                <label for="alerta-comentarios">{T['comentarios']}</label>
                                <textarea id="alerta-comentarios" name="comentarios" maxlength="1000" placeholder="{esc(T['comentarios_placeholder'])}"></textarea>
                            </div>
                            <div class="field field--hp" aria-hidden="true">
                                <label for="alerta-web">{C['honeypot']}</label>
                                <input id="alerta-web" name="web" type="text" tabindex="-1" autocomplete="off" maxlength="100">
                            </div>
                            <div class="field field--full">
                                <label class="checkbox" for="alerta-privacidad">
                                    <input id="alerta-privacidad" name="privacidad" type="checkbox" required aria-describedby="alerta-error-privacidad">
                                    <span>{resolve(ctx, C['privacy_html'])}</span>
                                </label>
                                {error('privacidad')}
                            </div>
                        </div>
                        <p class="form-legal">{form_legal(ctx, T['purpose'])}</p>
                        <div class="form-actions">
                            <button class="btn btn--primary btn--block" type="submit">{T['submit']} {ARROW}</button>
                        </div>
                        <p class="form-status" role="status" aria-live="polite"></p>
                    </form>
                </div>
            </div>
        </section>
"""


def valuation_section(ctx):
    """Formulario de valoración gratuita para propietarios (portada)."""
    L = ctx.L
    T, C = L["valuation"], L["contacto"]
    lab, clab = T["labels"], C["labels"]
    checks = "".join(f'\n                        <li>{icon("check")}{text}</li>' for text in T["checks"])
    towns = "".join(f'<option value="{esc(name)}"></option>' for name in sorted(TOWNS.values(), key=str.casefold))
    types = options(SEARCH_VALUES["tipo"], L["search"]["options"]["tipo"], T["tipo_placeholder"])

    def error(name):
        return f'<p class="field__error" id="valoracion-error-{name}" aria-live="polite"></p>'

    return f"""
        <section class="section valuation" id="valoracion" aria-labelledby="valoracion-title">
            <div class="container split">
                <div class="reveal">
                    <span class="eyebrow">{T['eyebrow']}</span>
                    <h2 class="section-title" id="valoracion-title">{T['title']}</h2>
                    <div class="prose-block">
                        <p>{T['text']}</p>
                    </div>
                    <ul class="check-list">{checks}
                    </ul>
                    <p class="valuation__note">{T['note']}</p>
                </div>

                <div class="card form-card reveal">
                    <h3 class="form-card__title">{T['form_title']}</h3>
                    <p class="form-card__lead">{C['form_lead']}</p>
                    <form class="lead-form" id="formulario-valoracion" action="mailto:{EMAIL}" method="post" enctype="text/plain" novalidate data-mail-subject="{esc(T['mail_subject'])}" data-subject-field="localidad">
                        <div class="form-grid">
                            <div class="field">
                                <label for="valoracion-localidad">{lab['localidad']}</label>
                                <input id="valoracion-localidad" name="localidad" type="text" list="valoracion-localidades" autocomplete="address-level2" maxlength="80" required placeholder="{esc(T['localidad_placeholder'])}" aria-describedby="valoracion-error-localidad">
                                <datalist id="valoracion-localidades">{towns}</datalist>
                                {error('localidad')}
                            </div>
                            <div class="field">
                                <label for="valoracion-direccion">{lab['direccion']}</label>
                                <input id="valoracion-direccion" name="direccion" type="text" autocomplete="street-address" maxlength="150" placeholder="{esc(T['direccion_placeholder'])}">
                            </div>
                            <div class="field field--full">
                                <label for="valoracion-tipo">{lab['tipo']}</label>
                                <select id="valoracion-tipo" name="tipo" required aria-describedby="valoracion-error-tipo">{types}</select>
                                {error('tipo')}
                            </div>
                            <div class="field">
                                <label for="valoracion-metros">{lab['metros']}</label>
                                <input id="valoracion-metros" name="metros" type="number" inputmode="numeric" min="10" max="100000" step="1" required aria-describedby="valoracion-error-metros">
                                {error('metros')}
                            </div>
                            <div class="field">
                                <label for="valoracion-dormitorios">{lab['dormitorios']}</label>
                                <input id="valoracion-dormitorios" name="dormitorios" type="number" inputmode="numeric" min="0" max="50" step="1" aria-describedby="valoracion-error-dormitorios">
                                {error('dormitorios')}
                            </div>
                            <div class="field field--full">
                                <label for="valoracion-nombre">{clab['nombre']}</label>
                                <input id="valoracion-nombre" name="nombre" type="text" autocomplete="name" maxlength="100" required aria-describedby="valoracion-error-nombre">
                                {error('nombre')}
                            </div>
                            <div class="field">
                                <label for="valoracion-telefono">{lab['telefono']}</label>
                                <input id="valoracion-telefono" name="telefono" type="tel" autocomplete="tel" inputmode="tel" maxlength="20" required aria-describedby="valoracion-error-telefono">
                                {error('telefono')}
                            </div>
                            <div class="field">
                                <label for="valoracion-email">{clab['email']}</label>
                                <input id="valoracion-email" name="email" type="email" autocomplete="email" maxlength="120" required aria-describedby="valoracion-error-email">
                                {error('email')}
                            </div>
                            <div class="field field--hp" aria-hidden="true">
                                <label for="valoracion-web">{C['honeypot']}</label>
                                <input id="valoracion-web" name="web" type="text" tabindex="-1" autocomplete="off" maxlength="100">
                            </div>
                            <div class="field field--full">
                                <label class="checkbox" for="valoracion-privacidad">
                                    <input id="valoracion-privacidad" name="privacidad" type="checkbox" required aria-describedby="valoracion-error-privacidad">
                                    <span>{resolve(ctx, C['privacy_html'])}</span>
                                </label>
                                {error('privacidad')}
                            </div>
                        </div>
                        <p class="form-legal">{form_legal(ctx, T['purpose'])}</p>
                        <div class="form-actions">
                            <button class="btn btn--primary btn--block" type="submit">{T['submit']} {ARROW}</button>
                        </div>
                        <p class="form-status" role="status" aria-live="polite"></p>
                    </form>
                </div>
            </div>
        </section>
"""


def commitments_strip(ctx):
    items = "".join(f"""
                <div class="commitment">
                    {icon(ic)}
                    <div>
                        <h3>{title}</h3>
                        <p>{text}</p>
                    </div>
                </div>""" for ic, (title, text) in zip(COMMITMENT_ICONS, ctx.L["commitments"]))
    return f"""
        <section class="commitments" aria-labelledby="compromisos-title">
            <div class="container">
                <h2 class="visually-hidden" id="compromisos-title">{ctx.L['ui']['commitments_title']}</h2>
                <div class="grid grid--4 reveal">{items}
                </div>
            </div>
        </section>
"""


def post_meta(ctx, slug, date, minutes, with_category=False):
    post = ctx.L["posts"][slug]
    parts = []
    if with_category:
        parts.append(f'<span>{post["category"]}</span><span aria-hidden="true">·</span>')
    parts.append(f'<time datetime="{date}">{post["date_label"]}</time><span aria-hidden="true">·</span>'
                 f'<span>{ctx.L["ui"]["min_read"].format(minutes)}</span>')
    return f'<p class="post-meta">{"".join(parts)}</p>'


def post_card(ctx, slug, icon_name, date, minutes):
    post = ctx.L["posts"][slug]
    href = ctx.page(f"blog/{slug}.html")
    return f"""
                <article class="card post-card reveal tilt">
                    <div class="post-card__media">
                        {icon(icon_name)}
                        <span class="post-card__category">{post['category']}</span>
                    </div>
                    <div class="post-card__body">
                        {post_meta(ctx, slug, date, minutes)}
                        <h3 class="post-card__title"><a href="{href}">{post['title']}</a></h3>
                        <p class="post-card__excerpt">{post['excerpt']}</p>
                        <a class="link-arrow" href="{href}" aria-hidden="true" tabindex="-1">{ctx.L['ui']['read_article']} {icon('arrow-right')}</a>
                    </div>
                </article>"""


# --------------------------------------------------------------------------
# Páginas
# --------------------------------------------------------------------------
def home_paths(ctx):
    """Portada sin inmuebles: un camino para propietarios (valoración) y otro para
    compradores (alerta de búsqueda), en lugar de los destacados."""
    T = ctx.L["index"]
    targets = [("key", valuation_link(ctx)), ("search", ctx.page("propiedades.html") + "#alerta")]
    cards = "".join(feature_card(
        ic, title, text,
        f'\n                    <p class="feature__more"><a class="btn btn--outline" href="{href}">{btn} {ARROW}</a></p>')
        for (ic, href), (title, text, btn) in zip(targets, T["paths"]))
    return f"""
        <section class="section paths" aria-labelledby="caminos-title">
            <div class="container">{section_header(T['paths_eyebrow'], T['paths_title'], 'caminos-title', T['paths_lead'])}
                <div class="grid grid--2">{cards}
                </div>
            </div>
        </section>
"""


def home_portfolio(ctx):
    """Buscador e inmuebles destacados de la portada. Sin inmuebles publicados no se
    muestran: el buscador llevaría a un listado vacío."""
    L, T = ctx.L, ctx.L["index"]
    if not PROPERTIES:
        return home_paths(ctx)
    featured = "".join(property_card(ctx, p) for p in PROPERTIES[:6])
    return f"""        <section class="search" aria-labelledby="buscador-title">
            <div class="container">
                <div class="search__panel reveal">
                    <h2 class="search__title" id="buscador-title">{L['search']['title_home']}</h2>
                    <form class="search__form" action="{ctx.page('propiedades.html')}" method="get" role="search">{search_fields(ctx, 'buscar')}
                        <button class="btn btn--primary" type="submit">{icon('search')}{L['search']['submit']}</button>
                    </form>
                </div>
            </div>
        </section>

        <section class="section" aria-labelledby="destacados-title">
            <div class="container">{section_header(T['featured_eyebrow'], T['featured_title'], 'destacados-title', T['featured_lead'])}
                <div class="grid grid--3">{featured}
                </div>
                <div class="section-footer">
                    <a class="btn btn--outline" href="{ctx.page('propiedades.html')}">{T['featured_all']} {ARROW}</a>
                </div>
            </div>
        </section>"""


def build_index(L):
    ctx = Ctx(L, "index.html")
    T, ui = L["index"], L["ui"]
    services = "".join(feature_card(
        ic, L["services"][sid][0], L["services"][sid][1],
        f'\n                    <p class="feature__more"><a class="link-arrow" href="{ctx.page("servicios.html")}#{sid}">'
        f'{ui["more_info"]} {icon("arrow-right")}<span class="visually-hidden"> {ui["about"]} {L["services"][sid][0].lower()}</span></a></p>'
    ) for sid, ic in SERVICES[:4])
    checks = "".join(f'\n                        <li>{icon("check")}{text}</li>' for text in T["about_checks"])
    ld = json_ld({
        "@context": "https://schema.org",
        "@type": "RealEstateAgent",
        "name": "Twins Real Estate",
        "slogan": T["slogan"],
        "email": EMAIL,
        "sameAs": [INSTAGRAM_URL],
        **({"url": url(ctx.file), "logo": url("logo-icon.png"), "image": url(OG_IMAGE)} if SITE_URL else {}),
        "address": {"@type": "PostalAddress", "addressLocality": LOCALITY, "addressRegion": "Catalunya", "addressCountry": "ES"},
        "openingHours": ["Mo-Fr 09:00-18:00", "Sa 10:00-14:00"],
        "knowsLanguage": [lang["lang"] for lang in LANGS],
    })

    portfolio = home_portfolio(ctx)
    if PROPERTIES:
        hero_button = f'<a class="btn btn--primary" href="{ctx.page("propiedades.html")}">{T["btn_props"]} {ARROW}</a>'
    else:
        hero_button = f'<a class="btn btn--primary" href="#valoracion">{T["btn_valuation"]} {ARROW}</a>'
    callouts = "".join(
        f'\n                    <li class="callout callout--{i}">{icon(ic)}<span>{text}</span></li>'
        for i, (ic, text) in enumerate(zip(PILLAR_ICONS, T["pillars"]), start=1))

    body = f"""
        <section class="hero3d" data-scroll="sticky" aria-labelledby="hero-title">
            <div class="hero3d__sticky">
                <div class="hero3d__glow" aria-hidden="true"></div>
                <div class="container hero3d__grid">
                    <div class="hero3d__copy">
                        <p class="eyebrow">{T['eyebrow']}</p>
                        <h1 class="hero3d__title" id="hero-title">{T['h1']}</h1>
                        <p class="hero3d__text">{T['text']}</p>
                        <div class="hero3d__actions">
                            {hero_button}
                            <a class="btn btn--glass" href="{ctx.page('contacto.html')}#formulario">{T['btn_advice']}</a>
                        </div>
                    </div>
                    <div class="hero3d__stage">{model_3d()}
                        <ul class="callouts">{callouts}
                        </ul>
                    </div>
                </div>
                <p class="scroll-hint" aria-hidden="true"><span>{ui['scroll_hint']}</span></p>
            </div>
        </section>

{portfolio}{valuation_section(ctx)}
        <section class="statement" data-scroll="sticky" aria-labelledby="nosotros-title">
            <div class="statement__sticky">
                <div class="container">
                    <p class="eyebrow">{T['about_eyebrow']}</p>
                    <h2 class="visually-hidden" id="nosotros-title">{T['about_eyebrow']}</h2>
                    <p class="statement__text" data-words>{T['about_paras'][0]}</p>
                </div>
            </div>
        </section>

        <section class="section section--alt" aria-labelledby="confianza-title">
            <div class="container split">
                <div class="split__visual reveal tilt">
                    <div class="split__frame">
                        {logos(ctx, small=False, extra=' loading="lazy" decoding="async"')}
                        <p class="split__quote">{T['quote']}</p>
                    </div>
                </div>
                <div class="reveal">
                    <h2 class="section-title" id="confianza-title">{T['about_title']}</h2>
                    <div class="prose-block">
                        <p>{T['about_paras'][1]}</p>
                    </div>
                    <ul class="check-list">{checks}
                    </ul>
                    <a class="btn btn--primary" href="{ctx.page('nosotros.html')}">{T['about_btn']} {ARROW}</a>
                </div>
            </div>
        </section>

        <section class="section" aria-labelledby="servicios-title">
            <div class="container">{section_header(T['services_eyebrow'], T['services_title'], 'servicios-title', T['services_lead'])}
                <div class="bento">{services}
                </div>
                <div class="section-footer">
                    <a class="btn btn--outline" href="{ctx.page('servicios.html')}">{T['services_all']} {ARROW}</a>
                </div>
            </div>
        </section>
{sell_section(ctx)}{commitments_strip(ctx)}{cta(ctx, T['cta_title'], T['cta_text'])}"""
    write(ctx, T["title"], T["description"], "index.html", body,
          extra_head=ld)


def build_properties(L):
    ctx = Ctx(L, "propiedades.html")
    T, S = L["propiedades"], L["search"]
    if not PROPERTIES:
        build_properties_soon(ctx)
        return
    cards = "".join(property_card(ctx, p) for p in PROPERTIES)
    body = page_hero(ctx, T["h1"], T["text"], [(L["ui"]["nav"]["propiedades.html"], "propiedades.html")], obj="house") + f"""
        <section class="filters" aria-labelledby="filtros-title">
            <div class="container">
                <div class="search__panel reveal">
                    <h2 class="search__title" id="filtros-title">{S['title_filter']}</h2>
                    <form class="search__form" id="filtro-inmuebles" action="{ctx.page('propiedades.html')}" method="get" role="search">{search_fields(ctx, 'filtro')}
                        <button class="btn btn--outline" type="reset">{S['reset']}</button>
                    </form>
                    <p class="filters__hint">{L['alert']['filter_hint']} <a class="link-arrow" href="#alerta">{L['alert']['filter_link']} {icon('arrow-right')}</a></p>
                </div>
            </div>
        </section>

        <section class="section" aria-labelledby="listado-title">
            <div class="container">
                <h2 class="visually-hidden" id="listado-title">{T['list_title']}</h2>
                <div class="results-bar">
                    <p role="status" aria-live="polite"><strong id="resultados-total">{len(PROPERTIES)}</strong> {T['found']}</p>
                    <p>{T['prices_note']}</p>
                </div>
                <div class="grid grid--3" id="listado-inmuebles">{cards}
                </div>
                <div class="empty-state" id="sin-resultados" hidden>
                    <h2>{T['empty_title']}</h2>
                    <p>{T['empty_text']}</p>
                    <a class="btn btn--primary" href="#alerta">{T['empty_btn']} {ARROW}</a>
                </div>
            </div>
        </section>
{alert_section(ctx)}{sell_section(ctx, alt=False)}"""
    write(ctx, T["title"], T["description"], "propiedades.html", body)


def build_properties_soon(ctx):
    """«Inmuebles» mientras no hay ninguno publicado: invita a crear una alerta de
    búsqueda y a solicitar una valoración. Sin inmuebles no tiene sentido mostrar
    el filtro, así que tampoco se genera el desplegable «Localidad» vacío."""
    L = ctx.L
    T, soon = L["propiedades"], L["propiedades"]["soon"]
    body = page_hero(ctx, T["h1"], soon["text"], [(L["ui"]["nav"]["propiedades.html"], "propiedades.html")], obj="house") + f"""
        <section class="section" aria-labelledby="cartera-title">
            <div class="container">
                <div class="empty-state portfolio-soon reveal">
                    <span class="eyebrow">{soon['eyebrow']}</span>
                    <h2 id="cartera-title">{soon['title']}</h2>
                    <p>{soon['body']}</p>
                    <div class="empty-state__actions">
                        <a class="btn btn--primary" href="#alerta">{soon['btn_alert']} {ARROW}</a>
                        <a class="btn btn--outline" href="{valuation_link(ctx)}">{soon['btn_sell']}</a>
                    </div>
                </div>
            </div>
        </section>
{alert_section(ctx)}{sell_section(ctx, alt=False)}"""
    write(ctx, T["title"], soon["description"], "propiedades.html", body)


def team_photos(ctx):
    """Galería de fotos reales del equipo; no se genera si no hay ninguna."""
    T = ctx.L["nosotros"]
    if not TEAM_PHOTOS:
        return ""
    figures = []
    for name, width, height in TEAM_PHOTOS:
        alt, caption = T["photos"][name]
        figures.append(f"""
                <figure class="photo reveal">
                    <picture>
                        <source srcset="{ctx.asset(f'fotos/{name}.webp')}" type="image/webp">
                        <img src="{ctx.asset(f'fotos/{name}.jpg')}" alt="{esc(alt)}" width="{width}" height="{height}" loading="lazy" decoding="async">
                    </picture>
                    <figcaption>{caption}</figcaption>
                </figure>""")
    return f"""
        <section class="section" aria-labelledby="equipo-title">
            <div class="container">{section_header(T['photos_eyebrow'], T['photos_title'], 'equipo-title')}
                <div class="photos">{''.join(figures)}
                </div>
            </div>
        </section>
"""


def build_about(L):
    ctx = Ctx(L, "nosotros.html")
    T = L["nosotros"]
    values = "".join(feature_card(ic, title, text) for ic, (title, text) in zip(VALUE_ICONS, T["values"]))
    paras = "".join(f"\n                        <p>{p}</p>" for p in T["paras"])
    body = page_hero(ctx, T["h1"], T["text"], [(L["ui"]["nav"]["nosotros.html"], "nosotros.html")], obj="twins") + f"""
        <section class="section" aria-labelledby="historia-title">
            <div class="container split">
                <div class="split__visual reveal">
                    <div class="split__frame">
                        {logos(ctx, small=False, extra=' loading="lazy" decoding="async"')}
                        <p class="split__quote">{L['index']['slogan']}</p>
                    </div>
                </div>
                <div class="reveal">
                    <span class="eyebrow">{T['eyebrow']}</span>
                    <h2 class="section-title" id="historia-title">{T['h2']}</h2>
                    <div class="prose-block">{paras}
                    </div>
                    <a class="btn btn--primary" href="{ctx.page('contacto.html')}#formulario">{T['btn']} {ARROW}</a>
                </div>
            </div>
        </section>

{team_photos(ctx)}
        <section class="section section--alt" aria-labelledby="mision-title">
            <div class="container">{section_header(T['purpose_eyebrow'], T['purpose_title'], 'mision-title')}
                <div class="grid grid--2">{feature_card('compass', *T['mission'])}{feature_card('lightbulb', *T['vision'])}
                </div>
            </div>
        </section>

        <section class="section" aria-labelledby="valores-title">
            <div class="container">{section_header(T['values_eyebrow'], T['values_title'], 'valores-title', T['values_lead'])}
                <div class="grid grid--4">{values}
                </div>
            </div>
        </section>
{commitments_strip(ctx)}{cta(ctx, T['cta_title'], T['cta_text'], (ctx.page('propiedades.html'), T['cta_secondary']))}"""
    write(ctx, T["title"], T["description"], "nosotros.html", body)


def build_services(L):
    ctx = Ctx(L, "servicios.html")
    T = L["servicios"]
    cards = "".join(feature_card(
        ic, L["services"][sid][0], L["services"][sid][1],
        '\n                    <ul class="feature__list">' + "".join(f"<li>{i}</li>" for i in L["services"][sid][2]) + "</ul>",
        f' id="{sid}"') for sid, ic in SERVICES)
    steps = "".join(f"""
                <article class="card step reveal tilt">
                    <h3 class="feature__title">{title}</h3>
                    <p class="feature__text">{text}</p>
                </article>""" for title, text in T["steps"])
    faqs = "".join(f"""
                <details class="faq__item">
                    <summary>{q}</summary>
                    <p class="faq__answer">{a}</p>
                </details>""" for q, a in T["faqs"])
    body = page_hero(ctx, T["h1"], T["text"], [(L["ui"]["nav"]["servicios.html"], "servicios.html")], obj="cube") + f"""
        <section class="section" aria-labelledby="servicios-title">
            <div class="container">
                <h2 class="visually-hidden" id="servicios-title">{T['list_title']}</h2>
                <div class="grid grid--3">{cards}
                </div>
            </div>
        </section>

        <section class="section section--alt" aria-labelledby="proceso-title">
            <div class="container">{section_header(T['process_eyebrow'], T['process_title'], 'proceso-title', T['process_lead'])}
                <div class="grid grid--4 steps">{steps}
                </div>
            </div>
        </section>

        <section class="section" aria-labelledby="faq-title">
            <div class="container">{section_header(T['faq_eyebrow'], T['faq_title'], 'faq-title')}
                <div class="faq reveal">{faqs}
                </div>
            </div>
        </section>
{cta(ctx, T['cta_title'], T['cta_text'])}"""
    write(ctx, T["title"], T["description"], "servicios.html", body)


def build_blog(L):
    ctx = Ctx(L, "blog.html")
    T, ui = L["blog"], L["ui"]
    slug, icon_name, date, minutes = POSTS[0]
    featured = L["posts"][slug]
    href = ctx.page(f"blog/{slug}.html")
    cards = "".join(post_card(ctx, *p) for p in POSTS[1:])
    body = page_hero(ctx, T["h1"], T["text"], [(ui["nav"]["blog.html"], "blog.html")], obj="pages") + f"""
        <section class="section" aria-labelledby="articulos-title">
            <div class="container">
                <h2 class="visually-hidden" id="articulos-title">{T['list_title']}</h2>
                <article class="card post-featured reveal">
                    <div class="post-card__media">
                        {icon(icon_name)}
                        <span class="post-card__category">{ui['featured']}</span>
                    </div>
                    <div class="post-featured__body">
                        {post_meta(ctx, slug, date, minutes, with_category=True)}
                        <h3 class="post-featured__title"><a href="{href}">{featured['title']}</a></h3>
                        <p class="post-card__excerpt">{featured['excerpt']}</p>
                        <p><a class="btn btn--primary" href="{href}" aria-hidden="true" tabindex="-1">{ui['read_article']} {ARROW}</a></p>
                    </div>
                </article>
                <div class="grid grid--3">{cards}
                </div>
            </div>
        </section>
{cta(ctx, T['cta_title'], T['cta_text'])}"""
    write(ctx, T["title"], T["description"], "blog.html", body)

    for index, (slug, icon_name, date, minutes) in enumerate(POSTS):
        ctx = Ctx(L, f"blog/{slug}.html")
        post = L["posts"][slug]
        related = [p for i, p in enumerate(POSTS) if i != index][:3]
        related_html = "".join(post_card(ctx, *p) for p in related)
        ld = json_ld({
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post["title"],
            "description": post["excerpt"],
            "datePublished": date,
            "dateModified": date,
            **({"image": url(OG_IMAGE)} if SITE_URL else {}),
            "inLanguage": L["lang"],
            **({"url": url(ctx.file), "mainEntityOfPage": url(ctx.file)} if SITE_URL else {}),
            "author": {"@type": "Organization", "name": "Twins Real Estate"},
            "publisher": {"@type": "Organization", "name": "Twins Real Estate"},
        })
        meta = "\n            " + post_meta(ctx, slug, date, minutes, with_category=True)
        if slug in OWNER_POSTS:  # artículos para propietarios: llevan a la valoración gratuita
            action = f'<a class="btn btn--primary" href="{valuation_link(ctx)}">{L["sell"]["btn"]} {ARROW}</a>'
        else:
            action = f'<a class="btn btn--primary" href="{ctx.page("contacto.html")}#formulario">{ui["consult"]} {ARROW}</a>'
        body = page_hero(ctx, post["title"], "", [(ui["nav"]["blog.html"], "blog.html"), (post["title"], "")], meta, obj="pages") + f"""
        <article class="article">
            <div class="container">
                <div class="prose">{post['body']}
                    <p class="notice">{ui['article_notice']}</p>
                </div>
                <footer class="article__footer">
                    <a class="link-arrow" href="{ctx.page('blog.html')}">{icon('arrow-left')} {ui['back_blog']}</a>
                    {action}
                </footer>
            </div>
        </article>

        <section class="section section--alt" aria-labelledby="relacionados-title">
            <div class="container">{section_header(None, ui['other_posts'], 'relacionados-title')}
                <div class="grid grid--3">{related_html}
                </div>
            </div>
        </section>"""
        write(ctx, post["title"], post["excerpt"], "blog.html", body,
              extra_head=ld)


def build_towns(L):
    """Una página por localidad: cómo trabajamos allí, servicios, valoración gratuita,
    alerta de búsqueda y, si los hay, los inmuebles publicados en ella."""
    T, ui = L["town_page"], L["ui"]
    for slug, town in TOWNS.items():
        ctx = Ctx(L, f"zona/{slug}.html")

        def f(text):
            return text.replace("{town}", esc(town))

        own = "".join(f"\n                        <p>{p}</p>" for p in L["towns"].get(slug, []))
        paras = own + "".join(f"\n                        <p>{f(p)}</p>" for p in T["paras"])
        query = "?" + urlencode({"localidad": town})
        valuation = ctx.page("index.html") + query + "#valoracion"
        alert = ctx.page("propiedades.html") + query + "#alerta"
        paths = "".join(feature_card(
            ic, f(title), f(text),
            f'\n                    <p class="feature__more"><a class="btn btn--outline" href="{href}">{btn} {ARROW}</a></p>')
            for ic, title, text, btn, href in (
                ("key", T["owners_title"], T["owners_text"], L["sell"]["btn"], valuation),
                ("search", T["buyers_title"], T["buyers_text"], L["propiedades"]["soon"]["btn_alert"], alert)))
        services = "".join(
            f'\n                        <li>{icon("check")}<a href="{ctx.page("servicios.html")}#{sid}">{L["services"][sid][0]}</a></li>'
            for sid, _ in SERVICES)
        listed = [p for p in PROPERTIES if p["zone"] == slug]
        listings = ""
        if listed:
            cards = "".join(property_card(ctx, p) for p in listed)
            listings = f"""
        <section class="section" aria-labelledby="inmuebles-zona-title">
            <div class="container">{section_header(None, f(T['listings_title']), 'inmuebles-zona-title')}
                <div class="grid grid--3">{cards}
                </div>
            </div>
        </section>
"""
        ld = json_ld({
            "@context": "https://schema.org",
            "@type": "RealEstateAgent",
            "name": "Twins Real Estate",
            "description": f(T["description"]),
            "email": EMAIL,
            **({"url": url(filename(L, "index.html")), "image": url(OG_IMAGE)} if SITE_URL else {}),
            "address": {"@type": "PostalAddress", "addressLocality": LOCALITY, "addressRegion": "Catalunya", "addressCountry": "ES"},
            "areaServed": {"@type": "City", "name": town},
            "knowsLanguage": [lang["lang"] for lang in LANGS],
        })
        body = page_hero(ctx, f(T["h1"]), f(T["text"]), [(f(T["h1"]), ctx.current)], obj="house") + f"""
        <section class="section" aria-labelledby="zona-title">
            <div class="container split">
                <div class="reveal">
                    <span class="eyebrow">{T['eyebrow']}</span>
                    <h2 class="section-title" id="zona-title">{f(T['h2'])}</h2>
                    <div class="prose-block">{paras}
                    </div>
                </div>
                <div class="reveal">
                    <h2 class="section-title section-title--sm" id="zona-servicios-title">{f(T['services_title'])}</h2>
                    <ul class="check-list">{services}
                    </ul>
                </div>
            </div>
        </section>

        <section class="section section--alt paths" aria-label="{esc(f(T['h2']))}">
            <div class="container">
                <div class="grid grid--2">{paths}
                </div>
            </div>
        </section>
{listings}{commitments_strip(ctx)}"""
        write(ctx, f(T["title"]), f(T["description"]), "", body, extra_head=ld)


def build_contact(L):
    ctx = Ctx(L, "contacto.html")
    T, ui = L["contacto"], L["ui"]
    lab = T["labels"]

    def error(name):
        return f'<p class="field__error" id="error-{name}" aria-live="polite"></p>'

    # La referencia solo tiene sentido cuando hay inmuebles publicados.
    reference = f"""                            <div class="field field--full">
                                <label for="contacto-referencia">{lab['referencia']}</label>
                                <input id="contacto-referencia" name="referencia" type="text" maxlength="20" placeholder="{esc(T['ref_placeholder'])}" aria-describedby="ayuda-referencia">
                                <p class="field__hint" id="ayuda-referencia">{T['ref_hint']}</p>
                            </div>
""" if PROPERTIES else ""

    body = page_hero(ctx, T["h1"], T["text"], [(ui["nav"]["contacto.html"], "contacto.html")]) + f"""
        <section class="section" aria-label="{esc(T['section_aria'])}">
            <div class="container contact-grid">
                <div class="contact-info reveal">
                    <div class="card contact-item">
                        <div class="feature__icon">{icon('mail')}</div>
                        <div>
                            <h2>{T['email_title']}</h2>
                            <a href="mailto:{EMAIL}">{EMAIL}</a>
                        </div>
                    </div>
                    <div class="card contact-item">
                        <div class="feature__icon">{icon('instagram')}</div>
                        <div>
                            <h2>{T['instagram_title']}</h2>
                            <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer">{INSTAGRAM_HANDLE}<span class="visually-hidden"> {ui['new_tab']}</span></a>
                        </div>
                    </div>
                    <div class="card contact-item">
                        <div class="feature__icon">{icon('clock')}</div>
                        <div>
                            <h2>{T['hours_title']}</h2>
                            <p>{ui['hours_html']}</p>
                        </div>
                    </div>
                    <div class="card contact-item">
                        <div class="feature__icon">{icon('calendar')}</div>
                        <div>
                            <h2>{T['meetings_title']}</h2>
                            <p>{T['meetings_text']}</p>
                        </div>
                    </div>
                </div>

                <div class="card form-card reveal" id="formulario">
                    <h2 class="form-card__title">{T['form_title']}</h2>
                    <p class="form-card__lead">{T['form_lead']}</p>
                    <form class="lead-form" id="formulario-contacto" action="mailto:{EMAIL}" method="post" enctype="text/plain" novalidate>
                        <div class="form-grid">
                            <div class="field">
                                <label for="contacto-nombre">{lab['nombre']}</label>
                                <input id="contacto-nombre" name="nombre" type="text" autocomplete="name" maxlength="100" required aria-describedby="error-nombre">
                                {error('nombre')}
                            </div>
                            <div class="field">
                                <label for="contacto-email">{lab['email']}</label>
                                <input id="contacto-email" name="email" type="email" autocomplete="email" maxlength="120" required aria-describedby="error-email">
                                {error('email')}
                            </div>
                            <div class="field">
                                <label for="contacto-telefono">{lab['telefono']}</label>
                                <input id="contacto-telefono" name="telefono" type="tel" autocomplete="tel" inputmode="tel" maxlength="20" aria-describedby="error-telefono">
                                {error('telefono')}
                            </div>
                            <div class="field">
                                <label for="contacto-asunto">{lab['asunto']}</label>
                                <select id="contacto-asunto" name="asunto">{options(SUBJECTS, T['subjects'], T['subject_placeholder'])}</select>
                            </div>
{reference}                            <div class="field field--full">
                                <label for="contacto-mensaje">{lab['mensaje']}</label>
                                <textarea id="contacto-mensaje" name="mensaje" maxlength="2000" required aria-describedby="error-mensaje"></textarea>
                                {error('mensaje')}
                            </div>
                            <div class="field field--hp" aria-hidden="true">
                                <label for="contacto-web">{T['honeypot']}</label>
                                <input id="contacto-web" name="web" type="text" tabindex="-1" autocomplete="off" maxlength="100">
                            </div>
                            <div class="field field--full">
                                <label class="checkbox" for="contacto-privacidad">
                                    <input id="contacto-privacidad" name="privacidad" type="checkbox" required aria-describedby="error-privacidad">
                                    <span>{resolve(ctx, T['privacy_html'])}</span>
                                </label>
                                {error('privacidad')}
                            </div>
                        </div>
                        <p class="form-legal">{form_legal(ctx, T['purpose'])}</p>
                        <div class="form-actions">
                            <button class="btn btn--primary btn--block" type="submit">{T['submit']} {ARROW}</button>
                        </div>
                        <p class="form-status" role="status" aria-live="polite"></p>
                    </form>
                </div>
            </div>
        </section>
"""
    write(ctx, T["title"], T["description"], "contacto.html", body)


def owner_table(L):
    rows = []
    for label, value in L["owner"]["rows"]:
        if value == "email":
            cell = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
        elif value in OWNER:
            if not OWNER[value]:
                continue
            cell = html.escape(OWNER[value])
        else:
            cell = value
        rows.append(f'<tr><th scope="row">{label}</th><td>{cell}</td></tr>')
    return '<div class="table-scroll">\n<table>\n<tbody>\n' + "\n".join(rows) + "\n</tbody>\n</table>\n</div>"


def build_legal(L):
    ui = L["ui"]
    for filename, page in L["legal"].items():
        ctx = Ctx(L, filename)
        forms = L["privacy_forms"]["endpoint" if form_endpoint() else "mail"]
        content = resolve(ctx, page["body"].replace("%%OWNER%%", owner_table(L)).replace("%%FORMS%%", forms))
        # Las tablas con desplazamiento horizontal deben poder desplazarse con el teclado.
        content = content.replace('<div class="table-scroll">', '<div class="table-scroll" tabindex="0">')
        body = page_hero(ctx, page["title"], ui["updated"].format(ui["updated_date"]), [(page["title"], filename)]) + f"""
        <article class="article">
            <div class="container">
                <div class="prose">{content}
                </div>
            </div>
        </article>"""
        write(ctx, page["title"], page["description"], "", body)


def build_404(L):
    ctx = Ctx(L, "404.html")
    T = L["error404"]
    body = f"""
        <section class="error-page">
            <div>{object_3d("rings")}
                <p class="error-page__code">404</p>
                <h1>{T['h1']}</h1>
                <p>{T['text']}</p>
                <div class="cta__actions">
                    <a class="btn btn--primary" href="{ctx.page('index.html')}">{T['home']} {ARROW}</a>
                    <a class="btn btn--outline-light" href="{ctx.page('propiedades.html')}">{T['props']}</a>
                </div>
            </div>
        </section>"""
    write(ctx, T["title"], T["description"], "", body, noindex=True)


# Artículos dirigidos a propietarios: su botón final lleva a la valoración gratuita.
OWNER_POSTS = {"gastos-impuestos-vender-piso-cataluna", "documentos-vender-vivienda", "preparar-vivienda-vender"}

# Artículos que ya existían con direcciones sin prefijo de idioma (versión anterior del sitio).
LEGACY_POSTS = {"comprar-o-alquilar-en-2026", "senales-revalorizacion-zona", "guia-primera-vivienda",
                "preparar-vivienda-alquiler", "que-revisar-contrato-arras", "tendencias-interiorismo-2026",
                "mitos-hipoteca"}


def build_legacy_redirects(L):
    """Redirige las direcciones antiguas sin prefijo de idioma (p. ej. «propiedades.html»),
    publicadas por una versión anterior del sitio, a su página actual en castellano."""
    pages = [(p, L["ui"]["nav"][p]) for p in PAGES if p != "index.html"]
    pages += [(p, page["title"]) for p, page in L["legal"].items()]
    pages += [(f"blog/{slug}.html", L["posts"][slug]["title"]) for slug, *_ in POSTS if slug in LEGACY_POSTS]
    for page, title in pages:
        old = page[len("blog/"):] if page.startswith("blog/") else page
        target = filename(L, page)
        canonical = url(target) if SITE_URL else target
        doc = f"""<!DOCTYPE html>
<html lang="{L['lang']}">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; base-uri 'none'; form-action 'none'">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)} | Twins Real Estate</title>
    <meta name="robots" content="noindex, follow">
    <link rel="canonical" href="{canonical}">
    <meta http-equiv="refresh" content="0; url={target}">
</head>
<body>
    <p><a href="{target}">{esc(title)}</a></p>
</body>
</html>
"""
        with open(os.path.join(SITE_DIR, old), "w", encoding="utf-8") as fh:
            fh.write(doc)


def logical_pages(L):
    """Todas las páginas indexables de un idioma, con su nombre lógico."""
    return (PAGES + list(L["legal"]) + [f"blog/{slug}.html" for slug, *_ in POSTS]
            + [f"zona/{slug}.html" for slug in TOWNS])


def build_sitemap():
    """sitemap.xml con las versiones de cada página en los tres idiomas, y robots.txt."""
    robots = "User-agent: *\nAllow: /\nDisallow: /404.html\n"
    if SITE_URL:
        dates = {f"blog/{slug}.html": date for slug, _, date, _ in POSTS}
        entries = []
        for L in LANGS:
            for page in logical_pages(L):
                alternates = "".join(
                    f'\n    <xhtml:link rel="alternate" hreflang="{o["lang"]}" href="{url(filename(o, page))}"/>'
                    for o in LANGS)
                alternates += (f'\n    <xhtml:link rel="alternate" hreflang="x-default" '
                               f'href="{url(filename(LANGS[0], page))}"/>')
                lastmod = f"\n    <lastmod>{dates[page]}</lastmod>" if page in dates else ""
                entries.append(f"  <url>\n    <loc>{url(filename(L, page))}</loc>{lastmod}{alternates}\n  </url>")
        sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                   'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(entries) + "\n</urlset>\n")
        with open(os.path.join(SITE_DIR, "sitemap.xml"), "w", encoding="utf-8") as fh:
            fh.write(sitemap)
        robots += f"\nSitemap: {url('sitemap.xml')}\n"
    with open(os.path.join(SITE_DIR, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(robots)


def build_headers():
    """_headers: cabeceras de seguridad y de caché para Netlify o Cloudflare Pages.
    GitHub Pages lo ignora (y no lo publica, porque empieza por «_»)."""
    text = f"""# Generado por _build.py: no lo edite a mano.
# Cabeceras de seguridad para Netlify / Cloudflare Pages. GitHub Pages ignora este
# archivo; allí la política de seguridad (CSP) va en una etiqueta <meta> de cada página.
/*
  Content-Security-Policy: {csp(meta=False)}
  Strict-Transport-Security: max-age=63072000; includeSubDomains
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Resource-Policy: same-origin

# styles.min.css, main.min.js y theme.js se enlazan siempre con «?v=<huella del contenido>»
# (ver versioned()): cada cambio genera una dirección nueva, así que el navegador
# puede guardarlos en caché indefinidamente. Las tipografías no cambian nunca.
/styles.min.css
  Cache-Control: public, max-age=31536000, immutable
/main.min.js
  Cache-Control: public, max-age=31536000, immutable
/theme.js
  Cache-Control: public, max-age=31536000, immutable
/fonts/*
  Cache-Control: public, max-age=31536000, immutable
"""
    with open(os.path.join(SITE_DIR, "_headers"), "w", encoding="utf-8") as fh:
        fh.write(text)


def build_security_txt():
    """/.well-known/security.txt (RFC 9116): a quién avisar de un problema de seguridad.
    _config.yml indica a Jekyll (GitHub Pages) que publique la carpeta .well-known."""
    lines = [f"Contact: mailto:{EMAIL}", f"Expires: {SECURITY_TXT_EXPIRES}", "Preferred-Languages: es, ca, en"]
    if SITE_URL:
        lines.append(f"Canonical: {SITE_URL}/.well-known/security.txt")
    os.makedirs(os.path.join(SITE_DIR, ".well-known"), exist_ok=True)
    with open(os.path.join(SITE_DIR, ".well-known", "security.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def check_translations():
    """Comprueba que todos los idiomas definen exactamente las mismas claves."""
    def keys(value, path=""):
        if isinstance(value, dict):
            found = set()
            for key, item in value.items():
                found |= keys(item, f"{path}.{key}")
            return found
        if isinstance(value, (list, tuple)):
            return {f"{path}[{len(value)}]"}
        return {path}

    reference = keys(LANGS[0])
    for lang in LANGS[1:]:
        diff = reference ^ keys(lang)
        if diff:
            raise SystemExit(f"Traducción «{lang['code']}» incompleta o con claves de más: {sorted(diff)}")


def main():
    check_translations()
    build_assets()
    for lang in LANGS:
        build_index(lang)
        build_properties(lang)
        build_about(lang)
        build_services(lang)
        build_blog(lang)
        build_contact(lang)
        build_legal(lang)
        build_towns(lang)
    build_404(LANGS[0])
    build_legacy_redirects(LANGS[0])
    build_sitemap()
    build_headers()
    build_security_txt()
    print("Sitio generado en", SITE_DIR)


if __name__ == "__main__":
    main()
