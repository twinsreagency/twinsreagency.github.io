"""Prepara las fotos reales para la web. Necesita Pillow (python3 -m pip install Pillow).

Fotos de los inmuebles (las que se suben desde el panel a _fotos/):
    python3 _fotos.py --inmuebles

    Para cada foto y plano de _inmuebles/*.json crea versiones de 480, 800, 1200 y 1600 px de
    ancho en AVIF, WebP y JPEG en fotos/inmuebles/, con un nombre que cambia si cambia la
    foto. Anota sus medidas en _fotos/indice.json, que es lo que usa _build.py, y borra
    las versiones que ya no usa ningún inmueble. También quita a los originales los
    metadatos (ubicación GPS de la cámara, modelo…) y los reduce a 2560 px como máximo.
    En GitHub lo hace solo la publicación (.github/workflows/publicar.yml).

Foto del equipo (una cada vez):
    python3 _fotos.py original.jpg equipo

    La reduce a 1600 px de ancho como máximo, le quita los metadatos y la guarda en
    fotos/ como WebP y JPEG. Después, añada ("equipo", ancho, alto) a TEAM_PHOTOS en
    _build.py, con el tamaño que indica el script, y ejecute python3 _build.py.
"""
import json
import os
import sys

from PIL import Image, ImageOps

MAX_WIDTH = 1600
SITE_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTHS = (480, 800, 1200, 1600)
MAX_ORIGINAL = 2560
FORMATS = (
    ("avif", "AVIF", {"quality": 55}),
    ("webp", "WEBP", {"quality": 78, "method": 6}),
    ("jpg", "JPEG", {"quality": 82, "optimize": True, "progressive": True}),
)
OUT_DIR = os.path.join("fotos", "inmuebles")


def main(source, name):
    out_dir = os.path.join(SITE_DIR, "fotos")
    os.makedirs(out_dir, exist_ok=True)
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")  # orientación correcta, sin EXIF
    if image.width > MAX_WIDTH:
        image = image.resize((MAX_WIDTH, round(image.height * MAX_WIDTH / image.width)), Image.LANCZOS)
    image.save(os.path.join(out_dir, f"{name}.webp"), "WEBP", quality=82, method=6)
    image.save(os.path.join(out_dir, f"{name}.jpg"), "JPEG", quality=84, optimize=True, progressive=True)
    print(f'Foto lista. Añada a TEAM_PHOTOS: ("{name}", {image.width}, {image.height})')


def file_hash(path):
    # El mismo cálculo que _build.file_hash: así el generador sabe si una foto ha cambiado.
    sys.path.insert(0, SITE_DIR)
    sys.dont_write_bytecode = True
    import _build
    return _build.file_hash(path)


def property_photos():
    """Fotos y planos de todos los inmuebles, sin repetir."""
    folder = os.path.join(SITE_DIR, "_inmuebles")
    found = []
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if name.endswith(".json"):
            with open(os.path.join(folder, name), encoding="utf-8") as fh:
                data = json.load(fh)
            for source in (data.get("fotos") or []) + ([data["plano"]] if data.get("plano") else []):
                key = "/" + str(source).lstrip("/")
                if key not in found:
                    found.append(key)
    return found


def clean_original(path):
    """Quita los metadatos del original y lo reduce si es enorme: el repositorio es público,
    y una foto de móvil puede llevar las coordenadas GPS exactas de la vivienda."""
    with Image.open(path) as image:
        has_metadata = bool(image.getexif()) or "exif" in image.info or "xmp" in image.info
        too_big = max(image.size) > MAX_ORIGINAL
        if not (has_metadata or too_big):
            return
        fmt = image.format
        clean = ImageOps.exif_transpose(image)
        if too_big:
            clean.thumbnail((MAX_ORIGINAL, MAX_ORIGINAL), Image.LANCZOS)
        if fmt == "JPEG":
            clean.convert("RGB").save(path, "JPEG", quality=90, optimize=True)
        else:
            clean.save(path, fmt)
    print(f"Original limpiado: {os.path.relpath(path, SITE_DIR)}")


def target_widths(width):
    """Anchos que se generan para una foto de este ancho (nunca se amplía)."""
    return sorted({w for w in WIDTHS if w < width} | {min(width, WIDTHS[-1])})


def make_versions(path, digest):
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
    widths = target_widths(image.width)
    base = f"{OUT_DIR}/{digest}"
    for width in widths:
        size = (width, round(image.height * width / image.width))
        resized = image if size == image.size else image.resize(size, Image.LANCZOS)
        for ext, fmt, options in FORMATS:
            resized.save(os.path.join(SITE_DIR, f"{base}-{width}.{ext}"), fmt, **options)
    return {"hash": digest, "width": widths[-1], "height": round(image.height * widths[-1] / image.width),
            "base": base, "formats": {ext: widths for ext, _, _ in FORMATS}}


def versions_ok(entry, path):
    """Las versiones están hechas con los anchos y formatos actuales y existen todas."""
    with Image.open(path) as image:
        width = ImageOps.exif_transpose(image).width
    expected = {ext: target_widths(width) for ext, _, _ in FORMATS}
    return entry["formats"] == expected and all(
        os.path.isfile(os.path.join(SITE_DIR, f"{entry['base']}-{w}.{ext}"))
        for ext, widths in entry["formats"].items() for w in widths)


def process_properties():
    index_file = os.path.join(SITE_DIR, "_fotos", "indice.json")
    old = {}
    if os.path.exists(index_file):
        with open(index_file, encoding="utf-8") as fh:
            old = json.load(fh)
    os.makedirs(os.path.join(SITE_DIR, OUT_DIR), exist_ok=True)
    index, created = {}, 0
    for key in property_photos():
        path = os.path.join(SITE_DIR, key.lstrip("/"))
        if not os.path.isfile(path):
            print(f"Aviso: no existe {key} (la web no se generará hasta que se suba o se quite)")
            continue
        clean_original(path)
        digest = file_hash(path)
        entry = old.get(key)
        if not (entry and entry["hash"] == digest and versions_ok(entry, path)):
            entry = make_versions(path, digest)
            created += 1
        index[key] = entry
    # Borra las versiones que ya no usa ningún inmueble.
    keep = {f"{e['base']}-{w}.{ext}".rsplit("/", 1)[1] for e in index.values()
            for ext, widths in e["formats"].items() for w in widths}
    removed = 0
    for name in os.listdir(os.path.join(SITE_DIR, OUT_DIR)):
        if name not in keep:
            os.remove(os.path.join(SITE_DIR, OUT_DIR, name))
            removed += 1
    os.makedirs(os.path.dirname(index_file), exist_ok=True)
    with open(index_file, "w", encoding="utf-8") as fh:
        json.dump(dict(sorted(index.items())), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"Fotos de inmuebles: {len(index)} en uso, {created} nuevas, {removed} versiones antiguas borradas")


if __name__ == "__main__":
    if sys.argv[1:] == ["--inmuebles"]:
        process_properties()
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        sys.exit(__doc__)
