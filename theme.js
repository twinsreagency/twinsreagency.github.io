/**
 * Twins Real Estate — aplica el tema guardado antes de pintar la página, para
 * evitar un parpadeo. El tema predeterminado es el crema; el oscuro solo se usa
 * si el visitante lo ha elegido. Se carga en <head> sin «defer».
 * El cambio de tema lo gestiona main.js.
 */
(function () {
    "use strict";

    var theme = "light";
    try {
        if (window.localStorage.getItem("twins:tema") === "dark") theme = "dark";
    } catch (error) {
        /* Almacenamiento no disponible: se usa el tema crema. */
    }
    document.documentElement.setAttribute("data-theme", theme);

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
