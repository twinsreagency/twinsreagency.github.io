"""Comprobaciones del sitio generado.

Uso (desde la carpeta del sitio):
    python3 -m unittest discover -s _tests -v

Solo usa la biblioteca estándar de Python.
"""
import filecmp
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True
# TWINS_SITE: probar otra copia generada del sitio (p. ej. la de _tests/fixture.py, con
# inmuebles de prueba), para comprobar que las fichas también cumplen todas las reglas.
SITE_DIR = os.environ.get("TWINS_SITE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SITE_DIR)

import _build  # noqa: E402


class Page(HTMLParser):
    """Extrae de un HTML lo necesario para las comprobaciones."""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.imgs, self.h1 = [], [], [], 0
        self.lang = self.canonical = self.description = self.refresh = self.csp = None
        self.inline_scripts, self.unsafe_attrs, self.blank_links, self.metas = 0, [], [], []
        self.title, self.json_ld = "", []
        self._in_title = self._in_ld = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.unsafe_attrs += [f"{tag}[{n}]" for n, _ in attrs if n == "style" or n.startswith("on")]
        if tag == "a" and a.get("target") == "_blank":
            self.blank_links.append(a)
        if tag == "meta":
            self.metas.append(a)
        if tag == "script" and not a.get("src") and a.get("type") != "application/ld+json":
            self.inline_scripts += 1
        if "id" in a:
            self.ids.append(a["id"])
        for attr in ("href", "src"):
            if a.get(attr):
                self.links.append(a[attr])
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "meta" and a.get("name") == "description":
            self.description = a.get("content")
        elif tag == "meta" and a.get("http-equiv") == "refresh":
            self.refresh = a.get("content")
        elif tag == "meta" and a.get("http-equiv") == "Content-Security-Policy":
            self.csp = a.get("content")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True
            self.json_ld.append("")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script":
            self._in_ld = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ld:
            self.json_ld[-1] += data


def html_files():
    return sorted(os.path.basename(f) for f in glob.glob(os.path.join(SITE_DIR, "*.html")))


def load(name):
    with open(os.path.join(SITE_DIR, name), encoding="utf-8") as fh:
        return Page(fh.read())


PAGES = {name: load(name) for name in html_files()}
REDIRECTS = {n: p for n, p in PAGES.items() if p.refresh}
CONTENT = {n: p for n, p in PAGES.items() if not p.refresh}


def local_target(link):
    """Archivo y fragmento de un enlace interno, o None si es externo."""
    parsed = urlparse(link)
    if parsed.scheme or link.startswith("//"):
        return None
    path = unquote(parsed.path).lstrip("/")
    return path, parsed.fragment


class BuildTest(unittest.TestCase):
    def test_translations_have_same_keys(self):
        _build.check_translations()

    def test_committed_output_is_up_to_date(self):
        """Ejecutar _build.py no debe cambiar nada: los HTML publicados están al día."""
        with tempfile.TemporaryDirectory() as tmp:
            copy = os.path.join(tmp, "site")
            shutil.copytree(SITE_DIR, copy, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
            subprocess.run([sys.executable, "_build.py"], cwd=copy, check=True, capture_output=True,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            generated = [os.path.basename(f) for f in glob.glob(os.path.join(copy, "*"))
                         if f.endswith((".html", ".xml", ".txt", ".min.css", ".min.js", ".webmanifest"))] + ["_headers", ".well-known/security.txt"]
            match, mismatch, errors = filecmp.cmpfiles(SITE_DIR, copy, generated, shallow=False)
            self.assertEqual(mismatch + errors, [], "Vuelva a ejecutar «python3 _build.py» y publique el resultado")


class LinkTest(unittest.TestCase):
    def test_internal_links_and_resources_exist(self):
        broken = []
        for name, page in PAGES.items():
            for link in page.links:
                target = local_target(link)
                if target is None:
                    continue
                path, fragment = target
                file = path or name
                if not os.path.isfile(os.path.join(SITE_DIR, file)):
                    broken.append(f"{name}: {link}")
                elif fragment and file.endswith(".html") and fragment not in PAGES[file].ids:
                    broken.append(f"{name}: {link} (ancla inexistente)")
        self.assertEqual(broken, [])

    def test_404_uses_root_paths(self):
        """El servidor muestra 404.html en cualquier ruta, así que no puede usar rutas relativas."""
        relative = [link for link in PAGES["404.html"].links
                    if local_target(link) and not link.startswith(("/", "#"))]
        self.assertEqual(relative, [])

    def test_legacy_urls_redirect_to_existing_pages(self):
        self.assertTrue(REDIRECTS, "Faltan las redirecciones de las direcciones antiguas")
        for name, page in REDIRECTS.items():
            target = page.refresh.split("url=", 1)[1]
            self.assertTrue(os.path.isfile(os.path.join(SITE_DIR, target)), name)
            self.assertTrue(page.canonical.endswith("/" + target), name)


class ContentTest(unittest.TestCase):
    def test_every_page_has_basic_metadata(self):
        for name, page in CONTENT.items():
            with self.subTest(page=name):
                self.assertIn(page.lang, {"es", "ca", "en"})
                self.assertTrue(page.title.strip())
                self.assertTrue(page.description and page.description.strip())
                self.assertEqual(page.h1, 1, "Debe haber exactamente un <h1>")
                if name != "404.html":
                    self.assertTrue(page.canonical and page.canonical.startswith(_build.SITE_URL))

    def test_no_placeholders_are_published(self):
        for path in glob.glob(os.path.join(SITE_DIR, "*.html")):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            self.assertIsNone(re.search(r"\[(pendiente|pendent|to be completed|completar)", text, re.I), path)

    def test_owner_rows_appear_only_when_filled(self):
        L = _build._textos_es.C
        table = _build.owner_table(L)
        self.assertNotIn("NIF", table)
        saved = dict(_build.OWNER)
        try:
            _build.OWNER.update(nif="12345678Z", titular="Nombre <Apellido>")
            table = _build.owner_table(L)
            self.assertIn("<td>12345678Z</td>", table)
            self.assertIn("Nombre &lt;Apellido&gt;", table)
            self.assertNotIn("Domicilio", table)
        finally:
            _build.OWNER.clear()
            _build.OWNER.update(saved)

    def test_forms_post_to_the_form_service_when_configured(self):
        """Sin servicio, los formularios abren el correo; con él, envían por HTTPS (sin el
        aviso de contenido mixto de un action="mailto:" y útiles también sin JavaScript)."""
        self.assertEqual(_build.form_action(), f'action="mailto:{_build.EMAIL}" method="post" enctype="text/plain"')
        saved = _build.form_endpoint
        try:
            _build.form_endpoint = lambda: "https://formspree.io/f/abcdefgh"
            self.assertEqual(_build.form_action(), 'action="https://formspree.io/f/abcdefgh" method="post"')
            self.assertIn("form-action 'self' mailto: https://formspree.io", _build.csp())
            self.assertEqual(_build.form_service(), "endpoint")
            _build.form_endpoint = lambda: "https://script.google.com/macros/s/AKfycbx123/exec"
            self.assertEqual(_build.form_service(), "google")
            self.assertIn("connect-src 'self' https://script.google.com https://script.googleusercontent.com", _build.csp())
            self.assertIn("Google Apps Script", _build.forms_privacy(_build._textos_es.C))
        finally:
            _build.form_endpoint = saved

    def test_single_main_call_to_action(self):
        """La acción principal es la misma en toda la web: la valoración gratuita."""
        for name in CONTENT:
            with open(os.path.join(SITE_DIR, name), encoding="utf-8") as fh:
                text = fh.read()
            header = re.findall(r'class="btn btn--primary nav__cta" href="([^"]+)"', text)
            self.assertEqual(len(header), 1, name)
            self.assertTrue(header[0].endswith("index.html#valoracion") or header[0] == "#valoracion"
                            or header[0].endswith(("-inici.html#valoracion", "-home.html#valoracion")), f"{name}: {header[0]}")
            closing = re.search(r'<section class="cta".*?</section>', text, re.S)
            if closing:
                self.assertRegex(closing.group(0), r'class="btn btn--primary" href="[^"]*#valoracion"', name)

    def test_phone_and_whatsapp_appear_only_when_configured(self):
        L = _build._textos_es.C
        ctx = _build.Ctx(L, "contacto.html")
        self.assertEqual(_build.phone_items(ctx) + _build.contact_phone_cards(ctx), "")
        for name in CONTENT:
            with open(os.path.join(SITE_DIR, name), encoding="utf-8") as fh:
                self.assertNotRegex(fh.read(), r'href="(tel:|https://wa\.me)', name)
        saved = (_build.PHONE, _build.WHATSAPP)
        try:
            _build.PHONE = _build.WHATSAPP = "+34 600 11 22 33"
            footer = _build.phone_items(ctx)
            self.assertIn('href="tel:+34600112233"', footer)
            self.assertIn("https://wa.me/34600112233?text=Hola%2C", footer)
            self.assertIn('rel="noopener noreferrer"', footer)
            self.assertIn("WhatsApp Ireland", _build.forms_privacy(L))
            _build.PHONE = "600 11 22 33"
            with self.assertRaises(SystemExit):
                _build.phone_items(ctx)
        finally:
            _build.PHONE, _build.WHATSAPP = saved

    def test_descriptions_still_fit_with_listings_and_long_town_names(self):
        """Las descripciones que dependen de los datos (listado con inmuebles, páginas por
        localidad y fichas) también caben, aunque hoy no se generen."""
        long_town = "Santa Margarida de Montbui i la Pobla"  # 37 caracteres
        for L in _build.LANGS:
            self.assertLessEqual(len(L["propiedades"]["description"]), 160, L["code"])
            town = L["town_page"]["description"].replace("{town}", long_town)
            self.assertTrue(70 <= len(town) <= 160, f"{L['code']}: {len(town)}")
            D, P = L["detail"], L["prop"]
            listing = D["description"].format(operation=P["sale"], type=max(L["search"]["options"]["tipo"], key=len),
                                              town=long_town, beds=count_sample(P["bed"]), baths=count_sample(P["bath"]),
                                              area=12345, price=_build.price(L, 12_500_000), ref="TRE-001")
            self.assertTrue(70 <= len(listing) <= 160, f"{L['code']}: {len(listing)} {listing}")

    def test_titles_fit_in_search_results(self):
        long = {n: p.title for n, p in CONTENT.items() if len(p.title) > 60}
        self.assertEqual(long, {})

    def test_descriptions_fit_in_search_results(self):
        """Entre 70 y 160 caracteres: más cortas desaprovechan el resultado de búsqueda y
        más largas aparecen cortadas."""
        wrong = {n: len(p.description) for n, p in CONTENT.items() if not 70 <= len(p.description) <= 160}
        self.assertEqual(wrong, {})

    def test_share_image_is_declared_and_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(SITE_DIR, _build.OG_IMAGE)))
        for name, page in CONTENT.items():
            if name != "404.html":
                image = [m for m in page.metas if m.get("property") == "og:image"]
                self.assertEqual([m.get("content") for m in image], [f"{_build.SITE_URL}/{_build.OG_IMAGE}"], name)

    def test_titles_and_descriptions_are_unique(self):
        titles = [p.title for p in CONTENT.values()]
        descriptions = [p.description for p in CONTENT.values()]
        self.assertEqual(len(titles), len(set(titles)))
        self.assertEqual(len(descriptions), len(set(descriptions)))

    def test_ids_are_unique(self):
        for name, page in CONTENT.items():
            duplicated = {i for i in page.ids if page.ids.count(i) > 1}
            self.assertEqual(duplicated, set(), name)

    def test_images_have_alt_and_size(self):
        for name, page in CONTENT.items():
            for img in page.imgs:
                self.assertIn("alt", img, f"{name}: {img.get('src')}")
                self.assertTrue(img.get("width") and img.get("height"), f"{name}: {img.get('src')}")

    def test_structured_data_is_valid_json(self):
        for name, page in CONTENT.items():
            for block in page.json_ld:
                data = json.loads(block)
                self.assertEqual(data["@context"], "https://schema.org", name)
                self.assertNotIn("</", block, name)

    def test_icons_and_manifest(self):
        """Favicon en todos los tamaños habituales y manifiesto con los iconos de Android."""
        def png_size(name):
            with open(os.path.join(SITE_DIR, name), "rb") as fh:
                header = fh.read(24)
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n", name)
            return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")

        for name, size in (("favicon-32.png", 32), ("favicon-96.png", 96), ("apple-touch-icon.png", 180),
                           ("icon-192.png", 192), ("icon-512.png", 512)):
            self.assertEqual(png_size(name), (size, size), name)
        self.assertTrue(os.path.isfile(os.path.join(SITE_DIR, "favicon.ico")))
        with open(os.path.join(SITE_DIR, "site.webmanifest"), encoding="utf-8") as fh:
            manifest = json.load(fh)
        self.assertEqual({icon["sizes"] for icon in manifest["icons"]}, {"192x192", "512x512"})
        for icon in manifest["icons"]:
            self.assertEqual(png_size(icon["src"]), tuple(map(int, icon["sizes"].split("x"))))
        for name, page in CONTENT.items():
            for link in ("favicon.ico", "favicon-96.png", "apple-touch-icon.png", "site.webmanifest"):
                self.assertTrue(any(l.endswith(link) for l in page.links), f"{name}: {link}")

    def test_home_pages_describe_the_agency_and_the_website(self):
        """Cada portada declara la agencia (RealEstateAgent) y el sitio (WebSite), enlazados."""
        for lang in _build.LANGS:
            page = PAGES[_build.filename(lang, "index.html")]
            graph = [node for block in page.json_ld for node in json.loads(block).get("@graph", [])]
            types = {node["@type"]: node for node in graph}
            self.assertEqual(set(types), {"RealEstateAgent", "WebSite"}, lang["lang"])
            self.assertEqual(types["WebSite"]["publisher"]["@id"], types["RealEstateAgent"]["@id"])
            self.assertEqual(types["WebSite"]["url"], page.canonical)


class DataTest(unittest.TestCase):
    """Inmuebles y datos que se editan en el panel: lo que no es válido detiene la
    publicación con un mensaje claro, en lugar de publicar una ficha rota."""

    BASE = dict(ref="TRE-010", operacion="venta", tipo="piso", localidad="Òdena", precio=150000,
                dormitorios=2, banos=1, superficie=70, energia_consumo="E", titulo_es="Piso céntrico")

    def load(self, **changes):
        return _build.load_property({**self.BASE, **changes}, "_inmuebles/prueba.json", {})

    def assertRejected(self, message, **changes):
        with self.assertRaises(SystemExit) as raised:
            self.load(**changes)
        self.assertIn(message, str(raised.exception))

    def test_valid_property(self):
        p = self.load(titulo_ca="Pis cèntric", precio="150.000", extras=["terraza", "ascensor"], lat=41.6, lon=1.55)
        self.assertEqual((p["zone"], p["town"], p["price"]), ("odena", "Òdena", 150000))
        self.assertEqual(p["title"], {"es": "Piso céntrico", "ca": "Pis cèntric", "en": "Piso céntrico"})
        self.assertEqual(p["extras"], ["ascensor", "terraza"], "en el orden de la lista")
        self.assertEqual(_build.slugify("Santa Margarida de Montbui"), "santa-margarida-de-montbui")

    def test_invalid_properties_are_rejected(self):
        self.assertRejected("TRE- y tres cifras", ref="123")
        self.assertRejected("operación", operacion="permuta")
        self.assertRejected("certificado energético es obligatorio", energia_consumo="")
        self.assertRejected("características desconocidas", extras=["helipuerto"])
        self.assertRejected("https://", video="http://example.com/video")
        self.assertRejected("fuera de lo razonable", dormitorios=80)
        self.assertRejected("falta «titulo_es»", titulo_es="")
        self.assertRejected("fuera de rango", lat=52.5)
        self.assertRejected("60 caracteres", titulo_en="A" * 61)
        p = self.load(titulo_ca="Pis cèntric")
        self.assertEqual(p["title_translated"], {"es": True, "ca": True, "en": False})
        self.assertRejected("no existe la foto", fotos=["/_fotos/no-existe.jpg"])

    def test_photos_need_their_optimized_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            saved = _build.SITE_DIR
            try:
                _build.SITE_DIR = tmp
                os.makedirs(os.path.join(tmp, "_fotos"))
                with open(os.path.join(tmp, "_fotos", "a.jpg"), "wb") as fh:
                    fh.write(b"foto")
                with self.assertRaises(SystemExit) as raised:
                    self.load(fotos=["/_fotos/a.jpg"])
                self.assertIn("python3 _fotos.py --inmuebles", str(raised.exception))
                index = {"/_fotos/a.jpg": {"hash": _build.file_hash(os.path.join(tmp, "_fotos", "a.jpg")), "width": 960,
                                           "height": 640, "base": "fotos/inmuebles/x", "formats": {"jpg": [480, 960]}}}
                p = _build.load_property({**self.BASE, "fotos": ["/_fotos/a.jpg"]}, "prueba", index)
                html_img = _build.picture(_build.Ctx(_build._textos_es.C, "index.html"), p["photos"][0], "Salón", "100vw")
                self.assertIn('srcset="fotos/inmuebles/x-480.jpg 480w, fotos/inmuebles/x-960.jpg 960w"', html_img)
                self.assertIn('width="960" height="640"', html_img)
            finally:
                _build.SITE_DIR = saved

    def test_trust_blocks_show_only_real_data(self):
        L = _build._textos_es.C
        ctx = _build.Ctx(L, "index.html")
        self.assertEqual(_build.trust_section(ctx), "")
        saved = (list(_build.REVIEWS), list(_build.CASES), dict(_build.AGENCY), dict(_build.OWNER))
        try:
            _build.REVIEWS[:] = _build.load_reviews([{"autor": "Joan P.", "texto": "Molt bé <script>x</script>", "fuente": "Google",
                                                      "estrellas": 5, "idioma": "ca", "enlace": "https://g.co/x", "fecha": "2026-10-01"}])
            _build.CASES[:] = _build.load_cases([{"titulo_es": "Venta en 30 días", "texto_es": "Piso vendido.", "localidad": "Igualada"}])
            _build.AGENCY.update(desde=2015, google_business="https://g.page/twins")
            _build.OWNER["registro_agentes"] = "AICAT 1234"
            html_trust = _build.trust_section(ctx)
            self.assertIn('aria-label="5 de 5 estrellas"', html_trust)
            self.assertIn('lang="ca"', html_trust)
            self.assertIn("Molt bé &lt;script&gt;", html_trust)
            self.assertIn('href="https://g.page/twins" target="_blank" rel="noopener noreferrer"', html_trust)
            self.assertIn("Venta en 30 días", html_trust)
            self.assertIn("2015", _build.figures(ctx))
            self.assertIn("n.º AICAT 1234", _build.aicat_note(ctx))
            self.assertIn("Opiniones en Google", _build.google_item(ctx))
        finally:
            _build.REVIEWS[:], _build.CASES[:] = saved[0], saved[1]
            _build.AGENCY.clear(); _build.AGENCY.update(saved[2])
            _build.OWNER.clear(); _build.OWNER.update(saved[3])

    def test_agency_and_trust_data_files(self):
        for name in ("agencia.json", "confianza.json"):
            with open(os.path.join(SITE_DIR, "_datos", name), encoding="utf-8") as fh:
                json.load(fh)
        with self.assertRaises(SystemExit):
            _build.load_reviews([{"autor": "Ana", "texto": "Muy bien"}])  # sin fuente
        review = _build.load_reviews([{"autor": "Ana", "texto": "Muy bien", "fuente": "Google", "estrellas": 5}])[0]
        self.assertEqual((review["stars"], review["lang"]), (5, "es"))


try:
    import yaml
except ImportError:
    yaml = None


@unittest.skipUnless(yaml, "necesita PyYAML")
class PanelTest(unittest.TestCase):
    """El panel (.pages.yml) ofrece exactamente los valores que acepta el generador."""

    def test_panel_matches_the_build(self):
        with open(os.path.join(SITE_DIR, ".pages.yml"), encoding="utf-8") as fh:
            config = yaml.safe_load(fh)
        entries = {c["name"]: c for c in config["content"]}
        fields = {f["name"]: f for f in entries["inmuebles"]["fields"]}

        def values(name):
            return [v["name"] if isinstance(v, dict) else v for v in fields[name]["options"]["values"]]

        self.assertEqual(values("operacion"), _build.SEARCH_VALUES["operacion"])
        self.assertEqual(values("tipo"), _build.SEARCH_VALUES["tipo"])
        self.assertEqual(values("extras"), _build.EXTRAS)
        self.assertEqual(values("energia_consumo"), _build.ENERGY_STATES)
        self.assertEqual(values("energia_emisiones"), _build.ENERGY_LETTERS)
        self.assertEqual(entries["inmuebles"]["path"], "_inmuebles")
        self.assertEqual(config["media"]["input"], "_fotos")
        # Todo lo que guarda el panel lo lee el generador (y al revés).
        prop = _build.load_property({**DataTest.BASE, **{k: None for k in fields if k not in DataTest.BASE}},
                                    "panel", {})
        self.assertEqual(prop["ref"], "TRE-010")
        with open(os.path.join(SITE_DIR, "_datos", "agencia.json"), encoding="utf-8") as fh:
            agency = json.load(fh)
        self.assertEqual({f["name"] for f in entries["agencia"]["fields"]}, set(agency))
        self.assertEqual(entries["agencia"]["path"], "_datos/agencia.json")


try:
    import PIL  # noqa: F401  (solo para la prueba de _fotos.py; en GitHub se instala)
    from PIL import Image as _Image
    HAS_PILLOW = hasattr(_Image, "new") and _Image.new("RGB", (1, 1)) is not None
except Exception:  # Pillow no instalado o incompleto
    HAS_PILLOW = False


@unittest.skipUnless(HAS_PILLOW, "necesita Pillow")
class PhotosTest(unittest.TestCase):
    """_fotos.py --inmuebles: versiones AVIF, WebP y JPEG, sin GPS, y la ficha las usa."""

    def test_property_photos_are_optimized_and_cleaned(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            copy = os.path.join(tmp, "site")
            shutil.copytree(SITE_DIR, copy, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
            os.makedirs(os.path.join(copy, "_fotos"), exist_ok=True)
            original = os.path.join(copy, "_fotos", "salon.jpg")
            exif = Image.Exif()
            exif[0x8825] = {2: (41.0, 34.0, 50.0), 4: (1.0, 37.0, 3.0)}  # coordenadas GPS
            Image.new("RGB", (3000, 2000), (180, 150, 120)).save(original, "JPEG", exif=exif)
            # Solo el inmueble de prueba, sin los reales ni sus fotos.
            shutil.rmtree(os.path.join(copy, "_inmuebles"))
            shutil.rmtree(os.path.join(copy, "fotos", "inmuebles"), ignore_errors=True)
            os.makedirs(os.path.join(copy, "_inmuebles"))
            with open(os.path.join(copy, "_fotos", "indice.json"), "w", encoding="utf-8") as fh:
                fh.write("{}")
            prop = dict(DataTest.BASE, fotos=["/_fotos/salon.jpg"])
            with open(os.path.join(copy, "_inmuebles", "TRE-010.json"), "w", encoding="utf-8") as fh:
                json.dump(prop, fh)
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            subprocess.run([sys.executable, "_fotos.py", "--inmuebles"], cwd=copy, check=True, capture_output=True, env=env)
            subprocess.run([sys.executable, "_build.py"], cwd=copy, check=True, capture_output=True, env=env)
            with Image.open(original) as cleaned:
                self.assertEqual(dict(cleaned.getexif()), {}, "sin metadatos GPS")
                self.assertEqual(max(cleaned.size), 2560)
            with open(os.path.join(copy, "_fotos", "indice.json"), encoding="utf-8") as fh:
                entry = json.load(fh)["/_fotos/salon.jpg"]
            self.assertEqual(entry["formats"], {f: [480, 800, 1200, 1600] for f in ("avif", "webp", "jpg")})
            self.assertEqual((entry["width"], entry["height"]), (1600, 1067))
            with open(os.path.join(copy, "es-inmueble-tre-010.html"), encoding="utf-8") as fh:
                page = fh.read()
            self.assertIn('<source type="image/avif"', page)
            self.assertIn('fetchpriority="high"', page)
            self.assertIn(f"{entry['base']}-800.webp 800w", page)
            # Una segunda pasada no rehace nada y quitar la foto borra sus versiones.
            out = subprocess.run([sys.executable, "_fotos.py", "--inmuebles"], cwd=copy, check=True, capture_output=True, text=True, env=env)
            self.assertIn("0 nuevas", out.stdout)
            os.remove(os.path.join(copy, "_inmuebles", "TRE-010.json"))
            subprocess.run([sys.executable, "_fotos.py", "--inmuebles"], cwd=copy, check=True, capture_output=True, env=env)
            self.assertEqual(os.listdir(os.path.join(copy, "fotos", "inmuebles")), [])


def count_sample(forms):
    return _build.count(10, forms)


def published_files():
    """Archivos que publica GitHub Pages (Jekyll): todo salvo lo que empieza por «_» o «.»,
    más lo indicado en «include» de _config.yml."""
    with open(os.path.join(SITE_DIR, "_config.yml"), encoding="utf-8") as fh:
        config = fh.read()

    def listed(key):
        block = re.search(rf"^{key}:\n((?:\s+-.*\n?)+)", config, re.M)
        return re.findall(r'-\s*"?([^"\s]+)"?', block.group(1)) if block else []

    included, excluded = listed("include"), listed("exclude")
    out = []
    for root, dirs, files in os.walk(SITE_DIR):
        rel = os.path.relpath(root, SITE_DIR)
        parts = [] if rel == "." else rel.split(os.sep)
        if any(p.startswith(("_", ".")) and p not in included for p in parts):
            continue
        for name in files:
            rel_name = os.path.join(*parts, name) if parts else name
            if (not name.startswith(("_", ".")) or name in included) and rel_name not in excluded:
                out.append(rel_name)
    return sorted(out)


class SecurityTest(unittest.TestCase):
    REQUIRED = ["default-src 'self'", "script-src 'self'", "style-src 'self'", "object-src 'none'",
                "base-uri 'self'", "font-src 'self'", "frame-src 'none'", "worker-src 'none'",
                "require-trusted-types-for 'script'", "trusted-types 'none'"]

    def test_every_page_has_a_strict_csp(self):
        for name, page in PAGES.items():
            with self.subTest(page=name):
                self.assertTrue(page.csp, "Falta la CSP en <meta>")
                self.assertNotIn("unsafe-inline", page.csp)
                self.assertNotIn("unsafe-eval", page.csp)
                self.assertNotIn("frame-ancestors", page.csp, "frame-ancestors no funciona en <meta>")
                self.assertEqual(page.metas[0].get("charset"), "utf-8")
                self.assertEqual(page.metas[1].get("http-equiv"), "Content-Security-Policy",
                                 "La CSP debe ir al principio de <head>, antes de cualquier recurso")
                if name not in REDIRECTS:
                    for rule in self.REQUIRED:
                        self.assertIn(rule, page.csp)

    def test_headers_file_matches_the_meta_csp(self):
        with open(os.path.join(SITE_DIR, "_headers"), encoding="utf-8") as fh:
            headers = fh.read()
        self.assertIn(f"Content-Security-Policy: {_build.csp(meta=False)}", headers)
        self.assertIn("frame-ancestors 'none'", headers)

    def test_no_inline_code(self):
        """La CSP no permite JavaScript ni estilos en línea: no debe haberlos."""
        for name, page in PAGES.items():
            self.assertEqual(page.inline_scripts, 0, name)
            self.assertEqual(page.unsafe_attrs, [], name)

    def test_new_tab_links_are_isolated(self):
        for name, page in PAGES.items():
            for a in page.blank_links:
                self.assertEqual(set((a.get("rel") or "").split()), {"noopener", "noreferrer"}, f"{name}: {a.get('href')}")

    def test_only_public_files_are_published(self):
        allowed = (".html", ".css", ".js", ".png", ".ico", ".woff2", ".webp", ".jpg", ".xml", ".txt", ".webmanifest")
        for file in published_files():
            self.assertTrue(file.endswith(allowed), f"Se publicaría {file}")
            self.assertFalse(file.startswith(("_", ".git")) or "/_" in file, f"Se publicaría {file}")
        self.assertIn(os.path.join(".well-known", "security.txt"), published_files())
        for internal in ("_build.py", "_textos_es.py", "_headers", "_config.yml", "_tests/test_site.py", "styles.css", "main.js"):
            self.assertNotIn(internal, published_files())

    def test_published_code_has_no_secrets_or_internal_notes(self):
        pattern = re.compile(r"(?i:api[_-]?key|secret[_-]?key|client[_-]?secret|password|access[_-]?token|BEGIN [A-Z ]*PRIVATE KEY)|TODO|FIXME|XXX|<!--")
        for file in published_files():
            if file.endswith((".html", ".js", ".css", ".txt", ".xml")) and not file.startswith("fonts"):
                with open(os.path.join(SITE_DIR, file), encoding="utf-8") as fh:
                    found = pattern.findall(fh.read())
                self.assertEqual(found, [], file)

    def test_security_txt_is_valid_and_not_expiring(self):
        import datetime
        with open(os.path.join(SITE_DIR, ".well-known", "security.txt"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn(f"Contact: mailto:{_build.EMAIL}", text)
        expires = datetime.datetime.fromisoformat(re.search(r"^Expires: (.+)$", text, re.M).group(1).replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        self.assertGreater(expires - now, datetime.timedelta(days=30),
                           "security.txt caduca pronto: adelante SECURITY_TXT_EXPIRES en _build.py")
        self.assertLess(expires - now, datetime.timedelta(days=366))


class FormsTest(unittest.TestCase):
    """Cada formulario tiene casilla de privacidad, texto informativo, campo trampa y límites."""

    def forms(self):
        for name in ("index.html", "es-inmuebles.html", "es-contacto.html", "ca-inici.html", "en-home.html"):
            with open(os.path.join(SITE_DIR, name), encoding="utf-8") as fh:
                for form in re.findall(r'<form class="lead-form".*?</form>', fh.read(), re.S):
                    yield name, form

    def test_lead_forms_are_complete(self):
        found = set()
        for name, form in self.forms():
            form_id = re.search(r'id="([^"]+)"', form).group(1)
            found.add(form_id)
            with self.subTest(form=f"{name}#{form_id}"):
                self.assertRegex(form, r'name="privacidad" type="checkbox" required')
                self.assertIn('class="form-legal"', form)
                self.assertRegex(form, r'name="web" type="text" tabindex="-1"')
                self.assertIn("novalidate", form)
                for field in re.findall(r"<(?:input|textarea)[^>]*>", form):
                    if 'type="checkbox"' in field or 'type="number"' in field:
                        continue
                    self.assertIn("maxlength=", field, field)
        self.assertEqual(found, {"formulario-valoracion", "formulario-alerta", "formulario-contacto"})


class SeoFilesTest(unittest.TestCase):
    def test_sitemap_lists_every_indexable_page(self):
        with open(os.path.join(SITE_DIR, "sitemap.xml"), encoding="utf-8") as fh:
            sitemap = fh.read()
        locs = set(re.findall(r"<loc>(.*?)</loc>", sitemap))
        canonicals = {p.canonical for n, p in CONTENT.items() if n != "404.html"}
        self.assertEqual(locs, canonicals)

    def test_robots_declares_sitemap(self):
        with open(os.path.join(SITE_DIR, "robots.txt"), encoding="utf-8") as fh:
            self.assertIn(f"Sitemap: {_build.SITE_URL}/sitemap.xml", fh.read())


if __name__ == "__main__":
    unittest.main()
