"""Genera una copia del sitio con inmuebles de prueba, para comprobar en el navegador
el listado, el filtro, los destacados y los favoritos aunque la cartera real esté vacía.

Uso: python3 _tests/fixture.py <carpeta de destino>
"""
import os
import shutil
import sys

sys.dont_write_bytecode = True
SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOWNS = {"igualada": "Igualada", "montbui": "Santa Margarida de Montbui"}

PROPERTIES = [
    dict(ref="TRE-001", op="venta", type="casa", zone="igualada", price=485000, beds=4, baths=3, area=320, icon="home"),
    dict(ref="TRE-002", op="venta", type="atico", zone="igualada", price=320000, beds=3, baths=2, area=180, icon="penthouse"),
    dict(ref="TRE-003", op="alquiler", type="piso", zone="montbui", price=1350, beds=2, baths=2, area=95, icon="building"),
    dict(ref="TRE-004", op="venta", type="casa", zone="montbui", price=1200000, beds=5, baths=4, area=550, icon="villa"),
]


def main(target):
    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(SITE_DIR, target, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
    sys.path.insert(0, target)
    import _build

    _build.SITE_DIR = target
    _build.PROPERTIES[:] = PROPERTIES
    _build.TOWNS.update(TOWNS)
    for lang in _build.LANGS:
        for p in PROPERTIES:
            lang["properties"][p["ref"]] = (f"Inmueble de prueba {p['ref']}", TOWNS[p["zone"]], None)
    with open(os.devnull, "w") as quiet:
        stdout, sys.stdout = sys.stdout, quiet
        try:
            _build.main()
        finally:
            sys.stdout = stdout


if __name__ == "__main__":
    main(sys.argv[1])
