# Publicar inmuebles desde el panel (Pages CMS)

El panel permite publicar inmuebles, fotos, datos de la agencia y opiniones sin tocar
código, desde el ordenador o el móvil. Es gratuito.

## Activarlo (una sola vez, unos 5 minutos)

1. Entre en [app.pagescms.org](https://app.pagescms.org) y pulse **Sign in with GitHub**
   con la cuenta de GitHub de la agencia.
2. Pulse **Install** e instale la app de Pages CMS **solo** en el repositorio
   `twinsreagency/twinsreagency.github.io`.
3. Abra el repositorio en el panel. Verá tres apartados: **Inmuebles**, **Datos de la
   agencia** y **Opiniones y casos de éxito**. La configuración ya está en el
   repositorio (`.pages.yml`).

No hace falta cambiar nada en GitHub. Cada vez que se guarda un cambio en el panel, el
flujo «Publicar cambios del panel» hace lo siguiente:

1. Prepara las fotos (AVIF, WebP y JPEG en tres tamaños, sin ubicación GPS).
2. Genera las fichas en los tres idiomas.
3. Prueba toda la web.
4. La publica.

En unos 5 minutos el cambio está en la web. Se puede seguir en la pestaña **Actions** de
GitHub.

## Añadir un inmueble

En **Inmuebles → Add an entry**, rellene:

- **Referencia**: TRE- y tres cifras, distinta en cada inmueble (TRE-001, TRE-002…).
  Es la que aparece en la web y en las consultas.
- **Operación, tipo, localidad, precio, dormitorios, baños y superficie.**
- **Certificado energético (consumo)**: es obligatorio en los anuncios (Real
  Decreto 390/2021). Si aún no lo tiene, elija «En trámite».
- **Título** (máximo 60 caracteres) y **descripción** en castellano. Si deja el catalán
  o el inglés en blanco, se muestra el texto en castellano.
- **Fotos**: la primera es la portada. Súbalas en horizontal y con al menos 1600 px de
  ancho.
- **Latitud y longitud** (opcional): la web solo muestra la zona aproximada, a unos 1 km.
  La dirección exacta nunca aparece.

Pulse **Save**. Para retirar un inmueble sin borrarlo (vendido, reservado), desmarque
**Publicado en la web**.

## Antes de subir fotos

El repositorio es público: lo que se sube se puede descargar, también su historial.

- **Quite la ubicación de las fotos antes de subirlas.**
  - En el iPhone: al compartir, toque **Opciones** y desactive **Ubicación**.
  - En Android: desactive la ubicación en los ajustes de la cámara.

  La publicación borra igualmente los metadatos, pero el original subido queda en el
  historial.
- No suba fotos con personas, matrículas o documentos visibles.
- Tamaño recomendado: menos de 3 MB por foto. Así el repositorio no crece demasiado; la
  publicación reduce las más grandes.

## Datos de la agencia y opiniones

- **Datos de la agencia**: titular, NIF, domicilio y n.º AICAT (obligatorios en el aviso
  legal), teléfono y WhatsApp, año de inicio y enlace de Google Business. Mientras un dato
  esté vacío, no se muestra.
- **Opiniones**: solo reales, copiadas tal cual de su fuente (p. ej. Google), con el
  nombre como aparece allí.
- **Casos de éxito**: solo reales y con permiso del cliente.

## Si algo falla

Si un dato no es válido (p. ej. una referencia repetida o sin certificado energético), la
web no se actualiza y la publicación aparece en rojo en **Actions**. El primer error del
registro dice qué corregir, en castellano.

Corríjalo en el panel y vuelva a guardar. Mientras tanto, la web sigue como estaba.

## Formato (para quien mantenga la web)

Cada inmueble es un archivo `_inmuebles/<ref>.json` con los campos de `.pages.yml`. Los
valida `load_property()` en `_build.py`.

- Las fotos se guardan en `_fotos/` (no se publican).
- `_fotos.py --inmuebles` crea sus versiones en `fotos/inmuebles/` y el índice
  `_fotos/indice.json`.
- Sin Pillow instalado, la publicación de GitHub lo hace sola.
