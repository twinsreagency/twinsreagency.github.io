# Recepción de formularios con Google Apps Script

Los formularios de la web (contacto, valoración gratuita y alerta de búsqueda) envían
los datos a un pequeño programa en su cuenta de Google (`formularios.gs`).

Con cada envío, el programa:

- valida los datos en el servidor;
- frena el spam: campo trampa, tiempo mínimo, límite por correo y por día;
- guarda el contacto en una hoja de cálculo;
- le avisa por Gmail;
- responde al cliente con un correo automático.

Es gratis y no necesita ningún servidor propio.

Se instala una sola vez, en unos 10 minutos.

## 1. Crear la hoja de contactos

1. Entre en [Google Sheets](https://sheets.google.com) con la cuenta de la agencia
   (twinsreagency@gmail.com) y cree una hoja en blanco llamada **Twins — Contactos**.
2. Menú **Extensiones → Apps Script**. Se abre el editor con un archivo `Código.gs`.
3. Borre su contenido, pegue **todo** el contenido de `_backend/formularios.gs` y pulse
   el icono de guardar.
4. Si quiere recibir los avisos en otro correo, escríbalo en `aviso: ""` (al principio
   del archivo).

## 2. Dar permisos y preparar la hoja

1. En la barra superior del editor, elija la función **instalar** y pulse **Ejecutar**.
2. Google pedirá permiso: **Revisar permisos**, elija la cuenta, después
   **Configuración avanzada → Ir a … (no seguro)** y pulse **Permitir**. Este aviso
   aparece siempre con los programas propios que no ha revisado Google.
3. Al terminar, la hoja tiene dos pestañas:
   - **Contactos**: un contacto por fila. Marque la casilla **Conservar** en los clientes
     con los que empiece a trabajar.
   - **Resumen**: contactos por mes y formulario, para medir cuántos contactos trae la web.

   Cada noche se borran solos los contactos de más de un año sin la casilla marcada, que
   es el plazo que fija la política de privacidad.

## 3. Publicarlo como aplicación web

1. Pulse **Implementar → Nueva implementación**. En el engranaje de «Seleccionar tipo»,
   elija **Aplicación web**.
2. Rellénela así:
   - Descripción: `Formularios web`.
   - Ejecutar como: **Yo**.
   - Quién tiene acceso: **Cualquier usuario**.

   Es necesario para que la web pueda enviar los formularios. Nadie puede leer la hoja:
   el programa solo acepta envíos.
3. Pulse **Implementar** y copie la **URL de la aplicación web**. Empieza por
   `https://script.google.com/macros/s/` y termina en `/exec`.

## 4. Conectarlo con la web

Ponga esa URL en `main.js`, en `endpoint: ""`, y ejecute `python3 _build.py`. También
puede pasársela a quien mantenga la web.

El generador hace el resto: añade Google a la política de seguridad (CSP) y cambia el
texto de la política de privacidad.

Para comprobarlo, envíe una valoración de prueba desde la web. Debe aparecer una fila
en **Contactos**, le debe llegar el aviso y al correo que puso le debe llegar la respuesta
automática.

## Cambios posteriores

Si se actualiza `formularios.gs`:

1. Pegue la versión nueva en el editor.
2. Pulse **Implementar → Gestionar implementaciones**, el lápiz, **Versión: nueva versión**
   e **Implementar**. La URL no cambia.

## Límites

- Gmail permite unos 100 correos al día con una cuenta gratuita. Cada contacto usa dos
  (el aviso y la respuesta), y el programa acepta como máximo 40 contactos al día.
  Puede cambiarlo en `porDia`.
- Para exportar los contactos a un CRM: **Archivo → Descargar → CSV** o Excel.
