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
        favoritesKey: "twins:favoritos",
        themeKey: "twins:tema"
    };

    var MESSAGES = {
        es: {
            localidad: "Indique la localidad en la que busca.",
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
            mailDefaultSubject: "Información general"
        },
        ca: {
            localidad: "Indiqueu la localitat on busqueu.",
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
            mailDefaultSubject: "Informació general"
        },
        en: {
            localidad: "Please enter the town you are looking in.",
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
            mailDefaultSubject: "General information"
        }
    };

    var LANG = MESSAGES[document.documentElement.lang] ? document.documentElement.lang : "es";
    var T = MESSAGES[LANG];

    var REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var FINE_POINTER = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

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

        var desktop = window.matchMedia("(min-width: 1101px)");
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

        function onBreakpoint(event) {
            if (event.matches) setOpen(false);
        }

        /* Safari < 14 solo admite addListener; sin esta comprobación, el error
           detendría el resto del script (filtros, formulario, favoritos). */
        if (desktop.addEventListener) {
            desktop.addEventListener("change", onBreakpoint);
        } else if (desktop.addListener) {
            desktop.addListener(onBreakpoint);
        }
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

    /* Tema oscuro / crema ----------------------------------------------- */

    function initTheme() {
        var root = document.documentElement;
        var toggle = $(".theme-toggle");
        var meta = $("meta[name='theme-color']");

        function apply(theme) {
            root.setAttribute("data-theme", theme);
            if (meta) meta.setAttribute("content", theme === "light" ? "#f2ede4" : "#000000");
            if (toggle) {
                var label = toggle.getAttribute(theme === "light" ? "data-label-dark" : "data-label-light");
                toggle.setAttribute("aria-label", label);
                toggle.setAttribute("title", label);
            }
        }

        apply(root.getAttribute("data-theme") === "dark" ? "dark" : "light");
        if (!toggle) return;

        toggle.addEventListener("click", function (event) {
            var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
            try {
                window.localStorage.setItem(CONFIG.themeKey, next);
            } catch (error) {
                /* Almacenamiento no disponible: el cambio dura solo esta visita. */
            }

            if (!document.startViewTransition || REDUCED_MOTION) {
                apply(next);
                return;
            }

            var rect = toggle.getBoundingClientRect();
            var x = event.clientX || rect.left + rect.width / 2;
            var y = event.clientY || rect.top + rect.height / 2;
            root.style.setProperty("--vt-x", x + "px");
            root.style.setProperty("--vt-y", y + "px");
            var transition = document.startViewTransition(function () {
                apply(next);
            });
            /* Si el navegador cancela la animación, el tema se aplica igualmente. */
            transition.ready.catch(function () {
                apply(next);
            });
            transition.finished.catch(function () {});
        });
    }

    /* Escenas ligadas al desplazamiento ------------------------------------ */

    /**
     * Actualiza la variable CSS --p (de 0 a 1) en cada elemento [data-scroll]:
     * - data-scroll="sticky": progreso mientras la sección fija recorre su altura.
     * - data-scroll="view": progreso desde que entra hasta que sale de la pantalla.
     * Solo se recalculan las escenas visibles, en un único requestAnimationFrame.
     */
    function initScrollScenes() {
        var scenes = $$("[data-scroll]");
        if (!scenes.length) return;

        var visible = [];
        var ticking = false;

        function clamp(value) {
            return Math.min(1, Math.max(0, value));
        }

        function update() {
            var viewport = window.innerHeight;
            visible.forEach(function (scene) {
                var rect = scene.getBoundingClientRect();
                var progress = scene.getAttribute("data-scroll") === "sticky"
                    ? clamp(-rect.top / Math.max(1, rect.height - viewport))
                    : clamp((viewport - rect.top) / (viewport + rect.height));
                scene.style.setProperty("--p", progress.toFixed(4));
                scene.classList.toggle("is-advanced", progress > 0.45);
            });
            ticking = false;
        }

        function requestUpdate() {
            if (!ticking) {
                window.requestAnimationFrame(update);
                ticking = true;
            }
        }

        if ("IntersectionObserver" in window) {
            var observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    var index = visible.indexOf(entry.target);
                    if (entry.isIntersecting && index === -1) visible.push(entry.target);
                    if (!entry.isIntersecting && index !== -1) visible.splice(index, 1);
                });
                requestUpdate();
            }, { rootMargin: "10% 0px" });
            scenes.forEach(function (scene) {
                observer.observe(scene);
            });
        } else {
            visible = scenes;
        }

        window.addEventListener("scroll", requestUpdate, { passive: true });
        window.addEventListener("resize", requestUpdate);
        requestUpdate();

        if (!REDUCED_MOTION) document.documentElement.classList.add("js-scroll");
    }

    /** Divide los textos [data-words] en palabras para iluminarlas al desplazar. */
    function initWordReveal() {
        $$("[data-words]").forEach(function (node) {
            var words = node.textContent.trim().split(/\s+/);
            node.textContent = "";
            words.forEach(function (word, index) {
                var span = document.createElement("span");
                span.className = "w";
                span.textContent = word;
                span.style.setProperty("--i", String(index));
                node.appendChild(span);
                if (index < words.length - 1) node.appendChild(document.createTextNode(" "));
            });
            node.style.setProperty("--n", String(words.length));
        });
    }

    /** Inclinación 3D y reflejo de luz de las tarjetas según la posición del cursor. */
    function initTilt() {
        if (!FINE_POINTER || REDUCED_MOTION) return;

        $$(".tilt").forEach(function (card) {
            var frame = 0;

            card.addEventListener("pointerenter", function () {
                card.classList.add("is-tilting");
            });

            card.addEventListener("pointermove", function (event) {
                if (frame) return;
                frame = window.requestAnimationFrame(function () {
                    var rect = card.getBoundingClientRect();
                    var x = (event.clientX - rect.left) / rect.width;
                    var y = (event.clientY - rect.top) / rect.height;
                    card.style.setProperty("--tx", ((x - 0.5) * 7).toFixed(2) + "deg");
                    card.style.setProperty("--ty", ((0.5 - y) * 7).toFixed(2) + "deg");
                    card.style.setProperty("--gx", (x * 100).toFixed(1) + "%");
                    card.style.setProperty("--gy", (y * 100).toFixed(1) + "%");
                    frame = 0;
                });
            });

            card.addEventListener("pointerleave", function () {
                card.classList.remove("is-tilting");
                card.style.setProperty("--tx", "0deg");
                card.style.setProperty("--ty", "0deg");
            });
        });
    }

    /** El modelo 3D de la portada reacciona suavemente al movimiento del ratón. */
    function initHeroPointer() {
        var hero = $(".hero3d");
        if (!hero || !FINE_POINTER || REDUCED_MOTION) return;

        var target = { x: 0, y: 0 };
        var current = { x: 0, y: 0 };
        var running = false;

        function step() {
            current.x += (target.x - current.x) * 0.08;
            current.y += (target.y - current.y) * 0.08;
            hero.style.setProperty("--mx", current.x.toFixed(3));
            hero.style.setProperty("--my", current.y.toFixed(3));
            if (Math.abs(target.x - current.x) > 0.001 || Math.abs(target.y - current.y) > 0.001) {
                window.requestAnimationFrame(step);
            } else {
                running = false;
            }
        }

        window.addEventListener("pointermove", function (event) {
            target.x = (event.clientX / window.innerWidth - 0.5) * 2;
            target.y = (event.clientY / window.innerHeight - 0.5) * 2;
            if (!running) {
                running = true;
                window.requestAnimationFrame(step);
            }
        }, { passive: true });
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
        var alertForm = document.getElementById("formulario-alerta");
        var townEdited = false;

        if (alertForm) {
            alertForm.elements.localidad.addEventListener("input", function () {
                townEdited = true;
            });
        }

        /** Traslada los criterios del filtro a la alerta de búsqueda, para no repetirlos. */
        function syncAlert() {
            if (!alertForm) return;
            fields.forEach(function (name) {
                var select = form.elements[name];
                if (!select) return;
                if (name === "zona") {
                    if (!townEdited) alertForm.elements.localidad.value = select.value ? select.options[select.selectedIndex].text : "";
                } else if (alertForm.elements[name]) {
                    alertForm.elements[name].value = select.value;
                }
            });
        }

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
            syncAlert();

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

    /* Formularios de contacto y de alerta de búsqueda --------------------- */

    /** Rellena el formulario de contacto con el motivo y la referencia de la URL. */
    function initContactPreset() {
        var form = document.getElementById("formulario-contacto");
        if (!form) return;

        var subject = form.elements.asunto;
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
    }

    /** Reglas de validación por nombre de campo; solo se aplican a los campos presentes. */
    var RULES = {
        localidad: function (value) {
            return value.length >= 2 ? "" : T.localidad;
        },
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

    /** Texto de la etiqueta de un campo, sin el asterisco de obligatorio. */
    function labelText(form, field) {
        var label = field.id ? $("label[for='" + field.id + "']", form) : null;
        return label ? label.textContent.replace(/\s*\*\s*$/, "").trim() : field.name;
    }

    /**
     * Validación y envío de un formulario .lead-form. Los datos se envían por
     * POST (JSON) a CONFIG.endpoint o, si no hay, se prepara un correo con
     * todos los campos rellenados. data-mail-subject y data-subject-field
     * definen el asunto del correo.
     */
    function initLeadForm(form) {
        var status = $(".form-status", form);
        var submit = $("button[type='submit']", form);
        var startedAt = Date.now();
        var rules = Object.keys(RULES).filter(function (name) {
            return Boolean(form.elements[name]);
        });

        function validateField(name) {
            var field = form.elements[name];
            var error = document.getElementById(field.getAttribute("aria-describedby"));
            var message = RULES[name](field.value.trim(), field);
            field.setAttribute("aria-invalid", String(Boolean(message)));
            if (error) error.textContent = message;
            return !message;
        }

        rules.forEach(function (name) {
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

        /** Campos enviados, en el orden del formulario (sin la casilla ni el campo trampa). */
        function fields() {
            return Array.prototype.filter.call(form.elements, function (field) {
                return field.name && field.name !== "web" && field.type !== "checkbox" &&
                    field.type !== "submit" && field.type !== "button";
            });
        }

        function valueOf(field) {
            if (field.tagName === "SELECT") return field.value ? field.options[field.selectedIndex].text : "";
            return field.value.trim();
        }

        function collect() {
            var data = { idioma: LANG, formulario: form.id };
            fields().forEach(function (field) {
                data[field.name] = valueOf(field);
            });
            return data;
        }

        function openMailClient(data) {
            var lines = [];
            var notes = [];
            fields().forEach(function (field) {
                var value = data[field.name];
                if (!value) return;
                if (field.tagName === "TEXTAREA") {
                    notes.push(value);
                } else {
                    lines.push(labelText(form, field) + ": " + value);
                }
            });
            if (notes.length) lines.push("", notes.join("\n\n"));

            var subjectField = form.getAttribute("data-subject-field") || "asunto";
            var subject = (form.getAttribute("data-mail-subject") || T.mailSubject) +
                " — " + (data[subjectField] || T.mailDefaultSubject);

            window.location.href = "mailto:" + CONFIG.fallbackEmail +
                "?subject=" + encodeURIComponent(subject) +
                "&body=" + encodeURIComponent(lines.join("\n"));
        }

        form.addEventListener("submit", function (event) {
            event.preventDefault();

            var valid = rules.map(validateField).every(Boolean);
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

    function initLeadForms() {
        initContactPreset();
        $$("form.lead-form").forEach(initLeadForm);
    }

    /* Año actual en el pie ----------------------------------------------- */

    function initYear() {
        $$("[data-year]").forEach(function (node) {
            node.textContent = String(new Date().getFullYear());
        });
    }

    /* Arranque ----------------------------------------------------------- */

    initTheme();
    initHeader();
    initNavigation();
    initWordReveal();
    initScrollScenes();
    initReveal();
    initTilt();
    initHeroPointer();
    initFavorites();
    initPropertyFilter();
    initLeadForms();
    initYear();
})();
