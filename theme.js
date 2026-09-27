/**
 * Twins Real Estate — aplica el tema guardado (oscuro o crema) antes de pintar
 * la página, para evitar un parpadeo. Se carga en <head> sin «defer».
 * El cambio de tema lo gestiona main.js.
 */
(function () {
    "use strict";

    var theme = "dark";
    try {
        if (window.localStorage.getItem("twins:tema") === "light") theme = "light";
    } catch (error) {
        /* Almacenamiento no disponible: se usa el tema oscuro. */
    }
    document.documentElement.setAttribute("data-theme", theme);
})();
