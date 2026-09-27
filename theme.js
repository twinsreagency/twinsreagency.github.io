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
})();
