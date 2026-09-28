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
        self.lang = self.canonical = self.description = self.refresh = None
        self.title, self.json_ld = "", []
        self._in_title = self._in_ld = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
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
                         if f.endswith((".html", ".xml", ".txt"))]
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
