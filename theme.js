/**
 * Twins Real Estate — aplica las preferencias guardadas antes de pintar la página,
 * para evitar un parpadeo: tema (crema, oscuro o automático según el sistema), tamaño
 * del texto, movimiento y contraste. El tema predeterminado es el crema. Se carga en
 * <head> sin «defer». Los cambios los gestiona main.js (botón de tema y «Ajustes»).
 */
(function () {
    "use strict";

    var root = document.documentElement;
    var theme = "light";
    var settings = {};
    try {
        var saved = window.localStorage.getItem("twins:tema");
        if (saved === "dark" || saved === "auto") theme = saved;
        settings = JSON.parse(window.localStorage.getItem("twins:ajustes")) || {};
    } catch (error) {
        /* Almacenamiento no disponible: se usan los valores predeterminados. */
    }

    if (theme === "auto") {
        root.setAttribute("data-theme-auto", "");
        theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    root.setAttribute("data-theme", theme);

    /* Solo valores conocidos: nada de lo guardado se escribe tal cual en la página. */
    if (settings.text === "l" || settings.text === "xl") root.setAttribute("data-text", settings.text);
    if (settings.motion === "reduced") root.setAttribute("data-motion", "reduced");
    if (settings.contrast === "more") root.setAttribute("data-contrast", "more");

    /* Protección contra el «clickjacking»: si otra web carga esta página dentro de un
       marco, la página no se muestra y se intenta abrir fuera de él. GitHub Pages no
       permite enviar la cabecera frame-ancestors, que sería la protección completa. */
    if (window.self !== window.top) {
        document.documentElement.setAttribute("data-framed", "");
        try {
            window.top.location.replace(window.self.location.href);
        } catch (error) {
            /* El navegador no deja salir del marco: la página sigue oculta. */
        }
    }
})();
