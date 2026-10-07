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
SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
                         if f.endswith((".html", ".xml", ".txt", ".min.css", ".min.js"))] + ["_headers", ".well-known/security.txt"]
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
                "base-uri 'self'", "font-src 'self'"]

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
        allowed = (".html", ".css", ".js", ".png", ".ico", ".woff2", ".webp", ".jpg", ".xml", ".txt")
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
