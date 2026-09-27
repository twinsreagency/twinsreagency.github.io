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
«_» no se publican en GitHub Pages ni se sirven con la configuración .htaccess.
"""
import hashlib
import html
import json
import os
import sys

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
SITE_URL = ""

LANGS = [_textos_es.C, _textos_ca.C, _textos_en.C]

EMAIL = "twinsreagency@gmail.com"
INSTAGRAM_URL = "https://www.instagram.com/twins.real.estate.agency/"
INSTAGRAM_HANDLE = "@twins.real.estate.agency"

# La política de seguridad (CSP) se envía como cabecera HTTP desde .htaccess
# (Apache) o _headers (Netlify / Cloudflare Pages). No se incluye como <meta>
# en el HTML porque bloquearía styles.css y main.js al abrir las páginas desde
# el disco (file://) o desde previsualizadores externos.

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
    "tipo": ["piso", "atico", "casa", "terreno", "oficina", "local"],
    "zona": ["centro", "norte", "sur", "este", "oeste", "periferia"],
    "precio": ["200000", "400000", "700000", "1000000"],
    "dormitorios": ["1", "2", "3", "4", "5"],
}

PROPERTIES = [
    dict(ref="TRE-001", op="venta", type="casa", zone="norte", price=485000, beds=4, baths=3, area=320, icon="home"),
    dict(ref="TRE-002", op="venta", type="atico", zone="centro", price=320000, beds=3, baths=2, area=180, icon="penthouse"),
    dict(ref="TRE-003", op="alquiler", type="piso", zone="sur", price=1350, beds=2, baths=2, area=95, icon="building"),
    dict(ref="TRE-004", op="venta", type="casa", zone="este", price=1200000, beds=5, baths=4, area=550, icon="villa"),
    dict(ref="TRE-005", op="venta", type="piso", zone="oeste", price=195000, beds=1, baths=1, area=75, icon="loft"),
    dict(ref="TRE-006", op="venta", type="casa", zone="periferia", price=410000, beds=3, baths=2, area=240, icon="tree"),
    dict(ref="TRE-007", op="venta", type="piso", zone="centro", price=650000, beds=3, baths=3, area=210, icon="building"),
    dict(ref="TRE-008", op="alquiler", type="casa", zone="norte", price=2900, beds=4, baths=3, area=280, icon="home"),
    dict(ref="TRE-009", op="venta", type="casa", zone="este", price=890000, beds=4, baths=4, area=390, icon="villa"),
]

SERVICES = [("compraventa", "key"), ("alquiler", "home"), ("gestion-alquileres", "clipboard"),
            ("inversion", "chart"), ("valoracion", "search"), ("asesoramiento-juridico", "shield")]

COMMITMENT_ICONS = ["document", "euro", "lock", "pen"]
VALUE_ICONS = ["eye", "award", "handshake", "users"]
PILLAR_ICONS = ["shield", "eye", "users"]

SUBJECTS = ["compra", "venta", "alquiler", "gestion", "valoracion", "inversion", "visita", "otro"]

POSTS = [  # (slug, icono, fecha ISO, minutos de lectura)
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

    def page(self, name):
        return filename(self.L, name)

    def translation(self, other):
        return filename(other, "index.html" if self.is_404 else self.current)

    @property
    def file(self):
        return filename(self.L, self.current)


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


def price(L, value):
    if L["code"] == "en":
        return f"€{value:,}"
    return f"{value:,}".replace(",", ".") + " €"


def count(n, forms):
    return f"{n} {forms[0] if n == 1 else forms[1]}"


def options(values, labels, placeholder):
    out = [f'<option value="">{placeholder}</option>']
    out += [f'<option value="{v}">{label}</option>' for v, label in zip(values, labels)]
    return "".join(out)


# --------------------------------------------------------------------------
# Plantilla común
# --------------------------------------------------------------------------
def head(ctx, title, description, noindex=False, extra=""):
    L = ctx.L
    full_title = title if title.startswith("Twins") else f"{title} | Twins Real Estate"
    alternates = ""
    if SITE_URL and not ctx.is_404:
        links = [f'\n    <link rel="canonical" href="{SITE_URL}/{ctx.file}">']
        for other in LANGS:
            links.append(f'\n    <link rel="alternate" hreflang="{other["lang"]}" href="{SITE_URL}/{ctx.translation(other)}">')
        links.append(f'\n    <link rel="alternate" hreflang="x-default" href="{SITE_URL}/{ctx.translation(LANGS[0])}">')
        alternates = "".join(links)
    robots = "noindex" if noindex else "index, follow"
    return f"""<!DOCTYPE html>
<html lang="{L['lang']}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <title>{esc(full_title)}</title>
    <meta name="description" content="{esc(description)}">
    <meta name="robots" content="{robots}">
    <meta name="theme-color" content="#000000">
    <meta name="color-scheme" content="dark light">
    <meta name="format-detection" content="telephone=no">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="{L['locale']}">
    <meta property="og:site_name" content="Twins Real Estate">
    <meta property="og:title" content="{esc(full_title)}">
    <meta property="og:description" content="{esc(description)}">{alternates}
    <link rel="icon" href="favicon.ico" sizes="any">
    <link rel="icon" href="favicon-32.png" type="image/png" sizes="32x32">
    <link rel="apple-touch-icon" href="apple-touch-icon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&amp;family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&amp;display=swap">
    <script src="{versioned('theme.js')}"></script>
    <link rel="stylesheet" href="{versioned('styles.css')}">
    <script src="{versioned('main.js')}" defer></script>{extra}
</head>"""


def brand(ctx):
    return f"""<a class="brand" href="{ctx.page('index.html')}" aria-label="{esc(ctx.L['ui']['home_aria'])}">
                <img class="logo--on-dark" src="logo-icon.png" alt="" width="26" height="34"><img class="logo--on-light" src="logo-icon-dark.png" alt="" width="26" height="34">
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
            <button class="theme-toggle" type="button" aria-label="{esc(ui['theme_to_light'])}" data-label-light="{esc(ui['theme_to_light'])}" data-label-dark="{esc(ui['theme_to_dark'])}">{icon('sun', 'icon-sun')}{icon('moon', 'icon-moon')}</button>
            <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="menu-principal" aria-label="{esc(ui['menu_open'])}" data-label-open="{esc(ui['menu_open'])}" data-label-close="{esc(ui['menu_close'])}">
                <span></span><span></span><span></span>
            </button>
        </div>
    </header>
"""


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


def page_hero(ctx, title, text, crumbs, extra=""):
    """crumbs: lista de (texto, página) tras «Inicio»; el último es la página actual."""
    ui = ctx.L["ui"]
    trail = [f'<li><a href="{ctx.page("index.html")}">{ui["home"]}</a></li>']
    for label, target in crumbs[:-1]:
        trail.append(f'<li><a href="{ctx.page(target)}">{label}</a></li>')
    trail.append(f'<li aria-current="page">{crumbs[-1][0]}</li>')
    text_html = f'\n            <p class="page-hero__text">{text}</p>' if text else ""
    return f"""
    <section class="page-hero" data-scroll="view">
        <div class="page-hero__panes" aria-hidden="true"><span></span><span></span><span></span></div>
        <div class="container">
            <nav class="breadcrumb" aria-label="{esc(ui['breadcrumb_aria'])}">
                <ol>{''.join(trail)}</ol>
            </nav>{extra}
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
def search_fields(ctx, prefix):
    S = ctx.L["search"]
    out = []
    for name, values in SEARCH_VALUES.items():
        label, placeholder = S["fields"][name]
        out.append(f"""
                    <div class="field">
                        <label for="{prefix}-{name}">{label}</label>
                        <select id="{prefix}-{name}" name="{name}">{options(values, S['options'][name], placeholder)}</select>
                    </div>""")
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


def model_3d():
    """Modelo 3D decorativo del logotipo (torre y casa) construido con CSS."""
    window = '<span class="window"><i></i><i></i><i></i><i></i></span>'
    walls = ["front", "back", "left", "right"]
    return f"""
                <div class="scene" aria-hidden="true">
                    <div class="scene__float">
                        <div class="model">
                            <span class="orbit orbit--1"></span>
                            <span class="orbit orbit--2"></span>
                            <span class="floor"></span>
                            <span class="box box--tower">{faces(walls + ["top"])}</span>
                            <span class="box box--house">{faces(walls, {"front": window})}<span class="gable gable--front"></span><span class="gable gable--back"></span><span class="slope slope--left"></span><span class="slope slope--right"></span></span>
                        </div>
                    </div>
                </div>"""


def section_header(eyebrow, title, title_id, lead=None):
    eyebrow_html = f'\n                    <span class="eyebrow">{eyebrow}</span>' if eyebrow else ""
    lead_html = f'\n                    <p class="section-lead">{lead}</p>' if lead else ""
    return f"""
                <header class="section-header reveal">{eyebrow_html}
                    <h2 class="section-title" id="{title_id}">{title}</h2>{lead_html}
                    <div class="divider"></div>
                </header>"""


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
def build_index(L):
    ctx = Ctx(L, "index.html")
    T, ui = L["index"], L["ui"]
    featured = "".join(property_card(ctx, p) for p in PROPERTIES[:6])
    services = "".join(feature_card(
        ic, L["services"][sid][0], L["services"][sid][1],
        f'\n                    <p class="feature__more"><a class="link-arrow" href="{ctx.page("servicios.html")}#{sid}">'
        f'{ui["more_info"]} {icon("arrow-right")}<span class="visually-hidden"> {ui["about"]} {L["services"][sid][0].lower()}</span></a></p>'
    ) for sid, ic in SERVICES[:4])
    checks = "".join(f'\n                        <li>{icon("check")}{text}</li>' for text in T["about_checks"])
    ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "RealEstateAgent",
        "name": "Twins Real Estate",
        "slogan": T["slogan"],
        "email": EMAIL,
        "sameAs": [INSTAGRAM_URL],
        "openingHours": ["Mo-Fr 09:00-18:00", "Sa 10:00-14:00"],
        "knowsLanguage": [lang["lang"] for lang in LANGS],
    }, ensure_ascii=False)

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
                            <a class="btn btn--primary" href="{ctx.page('propiedades.html')}">{T['btn_props']} {ARROW}</a>
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

        <section class="search" aria-labelledby="buscador-title">
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
        </section>

        <section class="statement" data-scroll="sticky" aria-labelledby="nosotros-title">
            <div class="statement__sticky">
                <div class="container">
                    <p class="eyebrow">{T['about_eyebrow']}</p>
                    <h2 class="visually-hidden" id="nosotros-title">{T['about_title']}</h2>
                    <p class="statement__text" data-words>{T['about_paras'][0]}</p>
                </div>
            </div>
        </section>

        <section class="section section--alt" aria-labelledby="confianza-title">
            <div class="container split">
                <div class="split__visual reveal tilt">
                    <div class="split__frame">
                        <img class="logo--on-dark" src="logo-icon.png" alt="" width="151" height="200"><img class="logo--on-light" src="logo-icon-dark.png" alt="" width="151" height="200">
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
{commitments_strip(ctx)}{cta(ctx, T['cta_title'], T['cta_text'])}"""
    write(ctx, T["title"], T["description"], "index.html", body,
          extra_head=f'\n    <script type="application/ld+json">{ld}</script>')


def build_properties(L):
    ctx = Ctx(L, "propiedades.html")
    T, S = L["propiedades"], L["search"]
    cards = "".join(property_card(ctx, p) for p in PROPERTIES)
    body = page_hero(ctx, T["h1"], T["text"], [(L["ui"]["nav"]["propiedades.html"], "propiedades.html")]) + f"""
        <section class="filters" aria-labelledby="filtros-title">
            <div class="container">
                <div class="search__panel reveal">
                    <h2 class="search__title" id="filtros-title">{S['title_filter']}</h2>
                    <form class="search__form" id="filtro-inmuebles" action="{ctx.page('propiedades.html')}" method="get" role="search">{search_fields(ctx, 'filtro')}
                        <button class="btn btn--outline" type="reset">{S['reset']}</button>
                    </form>
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
                    <a class="btn btn--primary" href="{ctx.page('contacto.html')}#formulario">{T['empty_btn']} {ARROW}</a>
                </div>
            </div>
        </section>
{cta(ctx, T['cta_title'], T['cta_text'])}"""
    write(ctx, T["title"], T["description"], "propiedades.html", body)


def build_about(L):
    ctx = Ctx(L, "nosotros.html")
    T = L["nosotros"]
    values = "".join(feature_card(ic, title, text) for ic, (title, text) in zip(VALUE_ICONS, T["values"]))
    paras = "".join(f"\n                        <p>{p}</p>" for p in T["paras"])
    body = page_hero(ctx, T["h1"], T["text"], [(L["ui"]["nav"]["nosotros.html"], "nosotros.html")]) + f"""
        <section class="section" aria-labelledby="historia-title">
            <div class="container split">
                <div class="split__visual reveal">
                    <div class="split__frame">
                        <img class="logo--on-dark" src="logo-icon.png" alt="" width="151" height="200"><img class="logo--on-light" src="logo-icon-dark.png" alt="" width="151" height="200">
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
    body = page_hero(ctx, T["h1"], T["text"], [(L["ui"]["nav"]["servicios.html"], "servicios.html")]) + f"""
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
    body = page_hero(ctx, T["h1"], T["text"], [(ui["nav"]["blog.html"], "blog.html")]) + f"""
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
        ld = json.dumps({
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post["title"],
            "description": post["excerpt"],
            "datePublished": date,
            "inLanguage": L["lang"],
            "author": {"@type": "Organization", "name": "Twins Real Estate"},
            "publisher": {"@type": "Organization", "name": "Twins Real Estate"},
        }, ensure_ascii=False)
        meta = "\n            " + post_meta(ctx, slug, date, minutes, with_category=True)
        body = page_hero(ctx, post["title"], "", [(ui["nav"]["blog.html"], "blog.html"), (post["title"], "")], meta) + f"""
        <article class="article">
            <div class="container">
                <div class="prose">{post['body']}
                    <p class="notice">{ui['article_notice']}</p>
                </div>
                <footer class="article__footer">
                    <a class="link-arrow" href="{ctx.page('blog.html')}">{icon('arrow-left')} {ui['back_blog']}</a>
                    <a class="btn btn--primary" href="{ctx.page('contacto.html')}#formulario">{ui['consult']} {ARROW}</a>
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
              extra_head=f'\n    <script type="application/ld+json">{ld}</script>')


def build_contact(L):
    ctx = Ctx(L, "contacto.html")
    T, ui = L["contacto"], L["ui"]
    lab = T["labels"]

    def error(name):
        return f'<p class="field__error" id="error-{name}" aria-live="polite"></p>'

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
                    <form id="formulario-contacto" action="mailto:{EMAIL}" method="post" enctype="text/plain" novalidate>
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
                            <div class="field field--full">
                                <label for="contacto-referencia">{lab['referencia']}</label>
                                <input id="contacto-referencia" name="referencia" type="text" maxlength="20" placeholder="{esc(T['ref_placeholder'])}" aria-describedby="ayuda-referencia">
                                <p class="field__hint" id="ayuda-referencia">{T['ref_hint']}</p>
                            </div>
                            <div class="field field--full">
                                <label for="contacto-mensaje">{lab['mensaje']}</label>
                                <textarea id="contacto-mensaje" name="mensaje" maxlength="2000" required aria-describedby="error-mensaje"></textarea>
                                {error('mensaje')}
                            </div>
                            <div class="field field--hp" aria-hidden="true">
                                <label for="contacto-web">{T['honeypot']}</label>
                                <input id="contacto-web" name="web" type="text" tabindex="-1" autocomplete="off">
                            </div>
                            <div class="field field--full">
                                <label class="checkbox" for="contacto-privacidad">
                                    <input id="contacto-privacidad" name="privacidad" type="checkbox" required aria-describedby="error-privacidad">
                                    <span>{resolve(ctx, T['privacy_html'])}</span>
                                </label>
                                {error('privacidad')}
                            </div>
                        </div>
                        <p class="form-legal">{resolve(ctx, T['legal_html'])}</p>
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
    O = L["owner"]
    rows = []
    for label, value, note in O["rows"]:
        if value == "pending":
            cell = f"<strong>{O['pending']}</strong>"
        elif value == "email":
            cell = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
        else:
            cell = value
        if note:
            cell += f" {note}"
        rows.append(f'<tr><th scope="row">{label}</th><td>{cell}</td></tr>')
    return '<div class="table-scroll">\n<table>\n<tbody>\n' + "\n".join(rows) + "\n</tbody>\n</table>\n</div>"


def build_legal(L):
    ui = L["ui"]
    for filename, page in L["legal"].items():
        ctx = Ctx(L, filename)
        content = resolve(ctx, page["body"].replace("%%OWNER%%", owner_table(L)))
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
            <div>
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
    for lang in LANGS:
        build_index(lang)
        build_properties(lang)
        build_about(lang)
        build_services(lang)
        build_blog(lang)
        build_contact(lang)
        build_legal(lang)
    build_404(LANGS[0])
    print("Sitio generado en", SITE_DIR)


if __name__ == "__main__":
    main()
