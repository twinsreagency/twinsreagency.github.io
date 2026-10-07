"""Prepara una foto real para la web: la reduce a un máximo de 1600 px de ancho, elimina
los metadatos (ubicación GPS, cámara…) y la guarda en fotos/ como WebP y como JPEG
(alternativa para navegadores antiguos).

Uso (desde la carpeta del sitio; necesita Pillow: python3 -m pip install Pillow):
    python3 _fotos.py original.jpg equipo

Después, añada ("equipo", ancho, alto) a TEAM_PHOTOS en _build.py, con el tamaño que
indica este script, y ejecute python3 _build.py.
"""
import os
import sys

from PIL import Image, ImageOps

MAX_WIDTH = 1600
SITE_DIR = os.path.dirname(os.path.abspath(__file__))


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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
