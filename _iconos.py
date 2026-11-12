"""Genera los iconos de la web a partir de _iconos/icono.png (el icono original, cuadrado
y con fondo transparente): el de iPhone (apple-touch-icon.png, 180 px), el de los
buscadores (favicon-96.png) y los de Android y del manifiesto (icon-192.png, icon-512.png).

Se mantiene la composición del icono original y se le añade un fondo crema opaco,
porque el iPhone pinta de negro las zonas transparentes y el logotipo oscuro
desaparecería sobre ese negro.

Uso (desde la carpeta del sitio; necesita Pillow: python3 -m pip install Pillow):
    python3 _iconos.py [icono.png]

El original mide 180 px: el icono de 512 px sale algo suave. Con un original de 512 px
o más (misma composición, fondo transparente) todos quedan nítidos.
"""
import os
import sys

from PIL import Image

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKGROUND = (255, 255, 255, 255)  # blanco, el fondo claro de la web
SIZES = {"apple-touch-icon.png": 180, "favicon-96.png": 96, "icon-192.png": 192, "icon-512.png": 512}


def main(source):
    with Image.open(source) as original:
        logo = original.convert("RGBA")
    if logo.width != logo.height:
        raise SystemExit("El icono original debe ser cuadrado.")
    for name, size in SIZES.items():
        icon = Image.new("RGBA", (size, size), BACKGROUND)
        icon.alpha_composite(logo.resize((size, size), Image.LANCZOS))
        icon.convert("RGB").save(os.path.join(SITE_DIR, name), "PNG", optimize=True)
        print(f"{name}: {size} × {size}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(SITE_DIR, "_iconos", "icono.png"))
