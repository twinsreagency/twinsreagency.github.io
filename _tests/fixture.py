"""Genera una copia del sitio con inmuebles de prueba, para comprobar en el navegador
el listado, el filtro, los destacados y los favoritos aunque la cartera real esté vacía.

Uso: python3 _tests/fixture.py <carpeta de destino> [dirección del servicio de formularios]

Con la dirección, la copia se genera como si los formularios enviaran a ese servicio
(p. ej. Google Apps Script), para probar el envío sin el programa de correo.
"""
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True
SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOWNS = {"igualada": "Igualada", "santa-margarida-de-montbui": "Santa Margarida de Montbui"}

# Como los guarda el panel (Pages CMS) en _inmuebles/<ref>.json.
PROPERTIES = [
    dict(ref="TRE-001", operacion="venta", tipo="casa", localidad="Igualada", zona="Les Comes", precio=485000,
         dormitorios=4, banos=3, superficie=320, fecha="2026-10-01", extras=["jardin", "piscina", "garaje"],
         energia_consumo="C", energia_consumo_valor=98.4, energia_emisiones="D", energia_emisiones_valor=21,
         lat=41.5791, lon=1.6172, planta="", ano=2004, video="https://www.youtube.com/watch?v=prueba",
         titulo_es="Casa con jardín en Les Comes", titulo_ca="Casa amb jardí a Les Comes",
         descripcion_es="Casa luminosa con jardín y piscina.\n\nA cinco minutos del centro.",
         etiqueta_es="Novedad", fotos=["/_fotos/TRE-001/fachada.jpg", "/_fotos/TRE-001/salon.jpg"],
         plano="/_fotos/TRE-001/plano.jpg"),
    dict(ref="TRE-002", operacion="venta", tipo="atico", localidad="Igualada", precio=320000, dormitorios=3,
         banos=2, superficie=180, fecha="2026-09-15", energia_consumo="en_tramite", titulo_es="Ático con terraza"),
    dict(ref="TRE-003", operacion="alquiler", tipo="piso", localidad="Santa Margarida de Montbui", precio=1350,
         dormitorios=2, banos=2, superficie=95, fecha="2026-11-01", energia_consumo="E", titulo_es="Piso con balcón",
         extras=["balcon", "ascensor"]),
    dict(ref="TRE-004", operacion="venta", tipo="casa", localidad="Santa Margarida de Montbui", precio=1200000,
         dormitorios=5, banos=4, superficie=550, fecha="2026-08-20", energia_consumo="exento",
         titulo_es="Masía con terreno"),
]


def fake_photos(target, build):
    """Fotos de prueba sin Pillow: la imagen para redes hace de original y de versión JPEG."""
    source = os.path.join(target, "og-image.jpg")
    index = {}
    for p in PROPERTIES:
        for path in p.get("fotos", []) + ([p["plano"]] if p.get("plano") else []):
            original = os.path.join(target, path.lstrip("/"))
            os.makedirs(os.path.dirname(original), exist_ok=True)
            with open(source, "rb") as src, open(original, "wb") as dst:
                dst.write(src.read() + path.encode())  # contenido distinto por foto
            digest = build.file_hash(original)
            base = f"fotos/inmuebles/{digest}"
            os.makedirs(os.path.join(target, "fotos", "inmuebles"), exist_ok=True)
            shutil.copyfile(source, os.path.join(target, f"{base}-1200.jpg"))
            index[path] = {"hash": digest, "width": 1200, "height": 630, "base": base, "formats": {"jpg": [1200]}}
    with open(os.path.join(target, "_fotos", "indice.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh)


def main(target, endpoint=""):
    if os.path.exists(target):
        shutil.rmtree(target)
    shutil.copytree(SITE_DIR, target, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
    if endpoint:
        script = os.path.join(target, "main.js")
        with open(script, encoding="utf-8") as fh:
            code = fh.read()
        with open(script, "w", encoding="utf-8") as fh:
            fh.write(code.replace('endpoint: "",', f'endpoint: "{endpoint}",', 1))
    sys.path.insert(0, target)
    import _build

    _build.SITE_DIR = target
    _build.TOWNS.update(TOWNS)
    # Solo los inmuebles de prueba: los reales (y sus fotos) no intervienen.
    shutil.rmtree(os.path.join(target, "_inmuebles"), ignore_errors=True)
    shutil.rmtree(os.path.join(target, "fotos", "inmuebles"), ignore_errors=True)
    os.makedirs(os.path.join(target, "_inmuebles"))
    for p in PROPERTIES:
        with open(os.path.join(target, "_inmuebles", f"{p['ref']}.json"), "w", encoding="utf-8") as fh:
            json.dump(p, fh, ensure_ascii=False)
    fake_photos(target, _build)
    with open(os.devnull, "w") as quiet:
        stdout, sys.stdout = sys.stdout, quiet
        try:
            _build.main()
        finally:
            sys.stdout = stdout


if __name__ == "__main__":
    main(*sys.argv[1:3])
