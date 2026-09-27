/**
 * Twins Real Estate — comportamiento del sitio.
 *
 * Sin dependencias externas ni código en línea, para permitir una
 * Content-Security-Policy estricta (script-src 'self') en el servidor.
 * El idioma se toma del atributo lang de <html> (es, ca o en).
 */
(function () {
    "use strict";

    /**
     * Configuración del formulario de contacto.
     *
     * endpoint: URL que recibe el formulario por POST (JSON), por ejemplo un
     * servicio como Formspree o un backend propio. Si se deja vacío, el
     * formulario abre el cliente de correo del usuario con el mensaje
     * preparado para `fallbackEmail`.
     * Al configurar un endpoint externo, añada su dominio a la directiva
     * `connect-src` de la política CSP (en .htaccess y _headers).
     */
    var CONFIG = {
        endpoint: "",
        fallbackEmail: "twinsreagency@gmail.com",
        minFillTimeMs: 3000,
        favoritesKey: "twins:favoritos"
    };

    var MESSAGES = {
        es: {
            nombre: "Indique su nombre y apellidos.",
            email: "Indique una dirección de correo electrónico válida.",
            telefono: "Indique un teléfono válido o deje el campo vacío.",
            mensaje: "El mensaje debe contener al menos 10 caracteres.",
            privacidad: "Debe aceptar la política de privacidad para continuar.",
            invalid: "Revise los campos indicados antes de enviar el formulario.",
            blocked: "No ha sido posible enviar el formulario. Inténtelo de nuevo en unos segundos.",
            mailOpened: "Se ha abierto su aplicación de correo con el mensaje preparado. Si no se abre, escríbanos directamente a {email}.",
            sending: "Enviando su consulta…",
            sent: "Gracias. Hemos recibido su consulta y le responderemos a la mayor brevedad.",
            failed: "No ha sido posible enviar su consulta. Inténtelo de nuevo o escríbanos a {email}.",
            prefill: "Deseo recibir más información sobre el inmueble con referencia {ref}.",
            mailSubject: "Consulta web",
            mailDefaultSubject: "Información general",
            mailName: "Nombre",
            mailEmail: "Correo electrónico",
            mailPhone: "Teléfono",
            mailReason: "Motivo",
            mailRef: "Referencia del inmueble"
        },
        ca: {
            nombre: "Indiqueu el vostre nom i cognoms.",
            email: "Indiqueu una adreça de correu electrònic vàlida.",
            telefono: "Indiqueu un telèfon vàlid o deixeu el camp buit.",
            mensaje: "El missatge ha de contenir almenys 10 caràcters.",
            privacidad: "Heu d’acceptar la política de privacitat per continuar.",
            invalid: "Reviseu els camps indicats abans d’enviar el formulari.",
            blocked: "No ha estat possible enviar el formulari. Torneu-ho a provar d’aquí a uns segons.",
            mailOpened: "S’ha obert la vostra aplicació de correu amb el missatge preparat. Si no s’obre, escriviu-nos directament a {email}.",
            sending: "S’està enviant la consulta…",
            sent: "Gràcies. Hem rebut la vostra consulta i us respondrem com més aviat millor.",
            failed: "No ha estat possible enviar la consulta. Torneu-ho a provar o escriviu-nos a {email}.",
            prefill: "Voldria rebre més informació sobre l’immoble amb referència {ref}.",
            mailSubject: "Consulta web",
            mailDefaultSubject: "Informació general",
            mailName: "Nom",
            mailEmail: "Correu electrònic",
            mailPhone: "Telèfon",
            mailReason: "Motiu",
            mailRef: "Referència de l’immoble"
        },
        en: {
            nombre: "Please enter your full name.",
            email: "Please enter a valid email address.",
            telefono: "Please enter a valid phone number or leave the field blank.",
            mensaje: "Your message must contain at least 10 characters.",
            privacidad: "You must accept the privacy policy to continue.",
            invalid: "Please review the highlighted fields before submitting the form.",
            blocked: "The form could not be sent. Please try again in a few seconds.",
            mailOpened: "Your email application has opened with the message ready to send. If it does not open, please write to us directly at {email}.",
            sending: "Sending your enquiry…",
            sent: "Thank you. We have received your enquiry and will reply as soon as possible.",
            failed: "Your enquiry could not be sent. Please try again or write to us at {email}.",
            prefill: "I would like to receive more information about the property with reference {ref}.",
            mailSubject: "Website enquiry",
            mailDefaultSubject: "General information",
            mailName: "Name",
            mailEmail: "Email",
            mailPhone: "Phone",
            mailReason: "Reason",
            mailRef: "Property reference"
        }
    };

    var LANG = MESSAGES[document.documentElement.lang] ? document.documentElement.lang : "es";
    var T = MESSAGES[LANG];

    var PROPERTY_REF = /^TRE-\d{3}$/;
    var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    var PHONE = /^[+()\d\s.-]{9,20}$/;

    /* Utilidades --------------------------------------------------------- */

    function $(selector, root) {
        return (root || document).querySelector(selector);
    }

    function $$(selector, root) {
        return Array.prototype.slice.call((root || document).querySelectorAll(selector));
    }

    function format(text, values) {
        return text.replace(/\{(\w+)\}/g, function (match, key) {
            return Object.prototype.hasOwnProperty.call(values, key) ? values[key] : match;
        });
    }

    function storageGet(key) {
        try {
            var value = JSON.parse(window.localStorage.getItem(key));
            return Array.isArray(value) ? value : [];
        } catch (error) {
            return [];
        }
    }

    function storageSet(key, value) {
        try {
            window.localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            /* Almacenamiento no disponible (modo privado): se ignora. */
        }
    }

    /** Devuelve el valor del parámetro solo si pertenece a la lista permitida. */
    function allowedParam(params, name, allowed) {
        var value = params.get(name);
        return value !== null && value !== "" && allowed.indexOf(value) !== -1 ? value : "";
    }

    function optionValues(select) {
        return $$("option", select).map(function (option) {
            return option.value;
        });
    }

    /* Cabecera, menú y botón «volver arriba» ----------------------------- */

    function initHeader() {
        var header = $(".site-header");
        var backToTop = $(".back-to-top");
        if (!header) return;

        var ticking = false;

        function update() {
            header.classList.toggle("is-scrolled", window.scrollY > 40);
            if (backToTop) backToTop.classList.toggle("is-visible", window.scrollY > 600);
            ticking = false;
        }

        window.addEventListener("scroll", function () {
            if (!ticking) {
                window.requestAnimationFrame(update);
                ticking = true;
            }
        }, { passive: true });

        update();

        if (backToTop) {
            backToTop.addEventListener("click", function () {
                window.scrollTo({ top: 0, behavior: "smooth" });
                var main = document.getElementById("contenido");
                if (main) main.focus({ preventScroll: true });
            });
        }
    }

    function initNavigation() {
        var header = $(".site-header");
        var toggle = $(".nav-toggle");
        var nav = document.getElementById("menu-principal");
        if (!toggle || !nav || !header) return;

        var desktop = window.matchMedia("(min-width: 1281px)");
        var labelOpen = toggle.getAttribute("data-label-open");
        var labelClose = toggle.getAttribute("data-label-close");

        function setOpen(open) {
            toggle.setAttribute("aria-expanded", String(open));
            toggle.setAttribute("aria-label", open ? labelClose : labelOpen);
            nav.classList.toggle("is-open", open);
            header.classList.toggle("is-open", open);
            document.body.classList.toggle("nav-open", open);
        }

        toggle.addEventListener("click", function () {
            setOpen(toggle.getAttribute("aria-expanded") !== "true");
        });

        nav.addEventListener("click", function (event) {
            if (event.target.closest("a")) setOpen(false);
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
                setOpen(false);
                toggle.focus();
            }
        });

        desktop.addEventListener("change", function (event) {
            if (event.matches) setOpen(false);
        });
    }

    /* Aparición progresiva de secciones ---------------------------------- */

    function initReveal() {
        var items = $$(".reveal");
        if (!items.length || !("IntersectionObserver" in window)) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { rootMargin: "0px 0px -60px 0px", threshold: 0.08 });

        var viewport = window.innerHeight;
        items.forEach(function (item) {
            if (item.getBoundingClientRect().top < viewport) {
                item.classList.add("is-visible");
            } else {
                observer.observe(item);
            }
        });

        document.documentElement.classList.add("js-reveal");
    }

    /* Favoritos ---------------------------------------------------------- */

    function initFavorites() {
        var buttons = $$(".fav-btn");
        if (!buttons.length) return;

        var favorites = storageGet(CONFIG.favoritesKey).filter(function (ref) {
            return typeof ref === "string" && PROPERTY_REF.test(ref);
        });

        buttons.forEach(function (button) {
            var ref = button.getAttribute("data-ref");
            button.setAttribute("aria-pressed", String(favorites.indexOf(ref) !== -1));

            button.addEventListener("click", function () {
                var index = favorites.indexOf(ref);
                if (index === -1) {
                    favorites.push(ref);
                } else {
                    favorites.splice(index, 1);
                }
                button.setAttribute("aria-pressed", String(index === -1));
                storageSet(CONFIG.favoritesKey, favorites);
            });
        });
    }

    /* Filtro de inmuebles ------------------------------------------------ */

    function initPropertyFilter() {
        var form = document.getElementById("filtro-inmuebles");
        var list = document.getElementById("listado-inmuebles");
        if (!form || !list) return;

        var cards = $$(".property", list);
        var count = document.getElementById("resultados-total");
        var empty = document.getElementById("sin-resultados");
        var fields = ["operacion", "tipo", "zona", "precio", "dormitorios"];
        var params = new URLSearchParams(window.location.search);

        fields.forEach(function (name) {
            var select = form.elements[name];
            if (select) select.value = allowedParam(params, name, optionValues(select));
        });

        function matches(card, criteria) {
            var data = card.dataset;
            if (criteria.operacion && data.operacion !== criteria.operacion) return false;
            if (criteria.tipo && data.tipo !== criteria.tipo) return false;
            if (criteria.zona && data.zona !== criteria.zona) return false;
            if (criteria.precio && Number(data.precio) > Number(criteria.precio)) return false;
            if (criteria.dormitorios && Number(data.dormitorios) < Number(criteria.dormitorios)) return false;
            return true;
        }

        function apply() {
            var criteria = {};
            var query = new URLSearchParams();

            fields.forEach(function (name) {
                var value = form.elements[name] ? form.elements[name].value : "";
                criteria[name] = value;
                if (value) query.set(name, value);
            });

            var visible = 0;
            cards.forEach(function (card) {
                var show = matches(card, criteria);
                card.hidden = !show;
                if (show) visible += 1;
            });

            if (count) count.textContent = String(visible);
            if (empty) empty.hidden = visible !== 0;

            var search = query.toString();
            window.history.replaceState(null, "", window.location.pathname + (search ? "?" + search : ""));
        }

        form.addEventListener("submit", function (event) {
            event.preventDefault();
            apply();
        });

        form.addEventListener("change", apply);

        form.addEventListener("reset", function () {
            window.setTimeout(apply, 0);
        });

        apply();
    }

    /* Formulario de contacto --------------------------------------------- */

    function initContactForm() {
        var form = document.getElementById("formulario-contacto");
        if (!form) return;

        var status = $(".form-status", form);
        var submit = $("button[type='submit']", form);
        var subject = form.elements.asunto;
        var startedAt = Date.now();
        var params = new URLSearchParams(window.location.search);

        var presetSubject = allowedParam(params, "asunto", optionValues(subject));
        if (presetSubject) subject.value = presetSubject;

        var reference = params.get("ref");
        if (reference && PROPERTY_REF.test(reference)) {
            form.elements.referencia.value = reference;
            if (!subject.value) subject.value = "compra";
            if (!form.elements.mensaje.value) {
                form.elements.mensaje.value = format(T.prefill, { ref: reference });
            }
        }

        var rules = {
            nombre: function (value) {
                return value.length >= 2 ? "" : T.nombre;
            },
            email: function (value) {
                return EMAIL.test(value) ? "" : T.email;
            },
            telefono: function (value) {
                return !value || PHONE.test(value) ? "" : T.telefono;
            },
            mensaje: function (value) {
                return value.length >= 10 ? "" : T.mensaje;
            },
            privacidad: function (value, field) {
                return field.checked ? "" : T.privacidad;
            }
        };

        function validateField(name) {
            var field = form.elements[name];
            var error = document.getElementById("error-" + name);
            var message = rules[name](field.value.trim(), field);
            field.setAttribute("aria-invalid", String(Boolean(message)));
            if (error) error.textContent = message;
            return !message;
        }

        Object.keys(rules).forEach(function (name) {
            var field = form.elements[name];
            field.addEventListener("blur", function () {
                if (field.type !== "checkbox" && (field.value || field.getAttribute("aria-invalid") === "true")) {
                    validateField(name);
                }
            });
            field.addEventListener("change", function () {
                if (field.getAttribute("aria-invalid") === "true") validateField(name);
            });
        });

        function setStatus(type, message) {
            status.className = "form-status form-status--" + type;
            status.textContent = message;
        }

        function collect() {
            return {
                idioma: LANG,
                nombre: form.elements.nombre.value.trim(),
                email: form.elements.email.value.trim(),
                telefono: form.elements.telefono.value.trim(),
                asunto: subject.value ? subject.options[subject.selectedIndex].text : "",
                referencia: form.elements.referencia.value.trim(),
                mensaje: form.elements.mensaje.value.trim()
            };
        }

        function openMailClient(data) {
            var lines = [
                T.mailName + ": " + data.nombre,
                T.mailEmail + ": " + data.email,
                T.mailPhone + ": " + (data.telefono || "—"),
                T.mailReason + ": " + (data.asunto || "—")
            ];
            if (data.referencia) lines.push(T.mailRef + ": " + data.referencia);
            lines.push("", data.mensaje);

            window.location.href = "mailto:" + CONFIG.fallbackEmail +
                "?subject=" + encodeURIComponent(T.mailSubject + " — " + (data.asunto || T.mailDefaultSubject)) +
                "&body=" + encodeURIComponent(lines.join("\n"));
        }

        form.addEventListener("submit", function (event) {
            event.preventDefault();

            var valid = Object.keys(rules).map(validateField).every(Boolean);
            if (!valid) {
                setStatus("error", T.invalid);
                var firstInvalid = $("[aria-invalid='true']", form);
                if (firstInvalid) firstInvalid.focus();
                return;
            }

            /* Protección básica contra envíos automatizados. */
            if (form.elements.web.value || Date.now() - startedAt < CONFIG.minFillTimeMs) {
                setStatus("error", T.blocked);
                return;
            }

            var data = collect();

            if (!CONFIG.endpoint) {
                openMailClient(data);
                setStatus("success", format(T.mailOpened, { email: CONFIG.fallbackEmail }));
                return;
            }

            submit.disabled = true;
            setStatus("success", T.sending);

            window.fetch(CONFIG.endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json", "Accept": "application/json" },
                body: JSON.stringify(data),
                credentials: "omit",
                referrerPolicy: "strict-origin-when-cross-origin"
            }).then(function (response) {
                if (!response.ok) throw new Error("HTTP " + response.status);
                form.reset();
                startedAt = Date.now();
                setStatus("success", T.sent);
            }).catch(function () {
                setStatus("error", format(T.failed, { email: CONFIG.fallbackEmail }));
            }).then(function () {
                submit.disabled = false;
            });
        });
    }

    /* Año actual en el pie ----------------------------------------------- */

    function initYear() {
        $$("[data-year]").forEach(function (node) {
            node.textContent = String(new Date().getFullYear());
        });
    }

    /* Arranque ----------------------------------------------------------- */

    initHeader();
    initNavigation();
    initReveal();
    initFavorites();
    initPropertyFilter();
    initContactForm();
    initYear();
})();
