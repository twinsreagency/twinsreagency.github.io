"""Textos del sitio en castellano (idioma principal)."""

C = {
    "code": "es",
    "lang": "es",
    "locale": "es_ES",
    "label": "Español",
    "abbr": "ES",
    "slugs": {"index": "inicio", "propiedades": "inmuebles", "servicios": "servicios", "nosotros": "nosotros", "blog": "blog", "contacto": "contacto", "aviso-legal": "aviso-legal", "privacidad": "privacidad", "cookies": "cookies"},

    "ui": {
        "skip": "Saltar al contenido principal",
        "home_aria": "Twins Real Estate, ir a la página de inicio",
        "nav_aria": "Navegación principal",
        "nav": {
            "index.html": "Inicio",
            "propiedades.html": "Inmuebles",
            "servicios.html": "Servicios",
            "nosotros.html": "Nosotros",
            "blog.html": "Blog",
            "contacto.html": "Contacto",
        },
        "cta_nav": "Solicitar cita",
        "menu_open": "Abrir menú",
        "menu_close": "Cerrar menú",
        "lang_aria": "Idioma",
        "footer_about": "Agencia inmobiliaria especializada en compraventa, alquiler e inversión. Asesoramiento cercano, riguroso y transparente en cada operación.",
        "footer_nav_title": "Navegación",
        "footer_nav_aria": "Enlaces del sitio",
        "footer_services_title": "Servicios",
        "footer_contact_title": "Contacto",
        "hours_html": "Lunes a viernes: 9:00&nbsp;–&nbsp;18:00<br>Sábados: 10:00&nbsp;–&nbsp;14:00",
        "rights": "Todos los derechos reservados.",
        "legal_aria": "Información legal",
        "legal": {
            "aviso-legal.html": "Aviso legal",
            "privacidad.html": "Política de privacidad",
            "cookies.html": "Política de cookies",
        },
        "instagram_aria": "Instagram de Twins Real Estate (se abre en una pestaña nueva)",
        "mail_aria": "Enviar un correo electrónico a Twins Real Estate",
        "new_tab": "(se abre en una pestaña nueva)",
        "back_top": "Volver al inicio de la página",
        "breadcrumb_aria": "Ruta de navegación",
        "home": "Inicio",
        "cta_primary": "Solicitar una cita",
        "cta_mail": "Escríbanos por correo",
        "more_info": "Más información",
        "about": "sobre",
        "read_article": "Leer artículo",
        "min_read": "{} min de lectura",
        "featured": "Destacado",
        "other_posts": "Otros artículos",
        "back_blog": "Volver al blog",
        "consult": "Consultar con un asesor",
        "article_notice": "Este artículo tiene carácter meramente informativo y no constituye asesoramiento jurídico, fiscal ni financiero. La normativa puede variar según la comunidad autónoma; consulte su caso con un profesional.",
        "updated": "Última actualización: {}",
        "updated_date": "27 de septiembre de 2026",
        "theme_to_light": "Cambiar a tema claro",
        "theme_to_dark": "Cambiar a tema oscuro",
        "scroll_hint": "Deslice para descubrir",
        "commitments_title": "Nuestros compromisos",
    },

    "search": {
        "title_home": "Encuentre su inmueble",
        "title_filter": "Filtrar inmuebles",
        "submit": "Buscar",
        "reset": "Restablecer",
        "fields": {
            "operacion": ("Operación", "Todas"),
            "tipo": ("Tipo de inmueble", "Todos"),
            "zona": ("Zona", "Todas"),
            "precio": ("Precio máximo", "Sin límite"),
            "dormitorios": ("Dormitorios", "Indiferente"),
        },
        "options": {
            "operacion": ["Venta", "Alquiler"],
            "tipo": ["Piso o apartamento", "Ático", "Casa o chalet", "Terreno", "Oficina", "Local comercial"],
            "zona": ["Centro", "Zona Norte", "Zona Sur", "Zona Este", "Zona Oeste", "Periferia y entorno rural"],
            "precio": ["Hasta 200.000 €", "Hasta 400.000 €", "Hasta 700.000 €", "Hasta 1.000.000 €"],
            "dormitorios": ["1 o más", "2 o más", "3 o más", "4 o más", "5 o más"],
        },
    },

    "prop": {
        "sale": "En venta",
        "rent": "En alquiler",
        "per_month": "/ mes",
        "bed": ("dormitorio", "dormitorios"),
        "bath": ("baño", "baños"),
        "request": "Solicitar información",
        "fav": "Guardar {} en favoritos",
        "features_aria": "Características",
        "ref": "Ref.",
    },

    "properties": {
        "TRE-001": ("Casa moderna con vistas al lago", "Zona Norte · Urbanización Los Lagos", "Destacado"),
        "TRE-002": ("Ático en el casco antiguo", "Centro · Casco antiguo", "Novedad"),
        "TRE-003": ("Piso luminoso con terraza", "Zona Sur · Jardines del Valle", None),
        "TRE-004": ("Villa contemporánea con piscina", "Zona Este · Club de Campo", "Exclusiva"),
        "TRE-005": ("Loft en el distrito creativo", "Zona Oeste · Distrito Creativo", None),
        "TRE-006": ("Casa de campo con jardín", "Entorno rural · Valle Verde", "Precio rebajado"),
        "TRE-007": ("Piso con vistas panorámicas", "Centro · Torre Mirador", "Novedad"),
        "TRE-008": ("Casa familiar con amplio jardín", "Zona Norte · Los Bosques", None),
        "TRE-009": ("Residencia de diseño minimalista", "Zona Este · Colinas del Sol", "Exclusiva"),
    },

    "commitments": [
        ("Información verificada", "Revisamos la nota simple, las cargas y el certificado energético antes de publicar cada inmueble."),
        ("Honorarios transparentes", "Las condiciones económicas se acuerdan por escrito antes de iniciar cualquier gestión."),
        ("Confidencialidad", "Tratamos sus datos personales conforme al RGPD y a la LOPDGDD."),
        ("Acompañamiento hasta la firma", "Coordinamos notaría, financiación y trámites posteriores a la compraventa."),
    ],

    "services": {
        "compraventa": ("Compraventa de inmuebles",
                        "Le acompañamos en la venta o la adquisición de su inmueble, desde la valoración inicial hasta la firma de la escritura.",
                        ["Estudio de mercado y fijación del precio", "Reportaje fotográfico y difusión del inmueble",
                         "Gestión de visitas y negociación", "Contrato de arras y coordinación con la notaría"]),
        "alquiler": ("Alquiler de viviendas",
                     "Seleccionamos al inquilino adecuado mediante un proceso riguroso y formalizamos un contrato conforme a la Ley de Arrendamientos Urbanos.",
                     ["Análisis de solvencia de los candidatos", "Redacción y revisión del contrato",
                      "Depósito de la fianza ante el organismo autonómico", "Inventario y entrega de llaves"]),
        "gestion-alquileres": ("Gestión integral de alquileres",
                               "Administramos su inmueble para que obtenga rentabilidad sin tener que ocuparse del día a día.",
                               ["Cobro de rentas y seguimiento de impagos", "Coordinación de reparaciones y mantenimiento",
                                "Atención a los inquilinos", "Informes periódicos al propietario"]),
        "inversion": ("Asesoramiento para inversión",
                      "Identificamos oportunidades y analizamos su rentabilidad con criterios objetivos y adaptados a su perfil.",
                      ["Análisis de rentabilidad bruta y neta", "Estudio de la zona y de la demanda",
                       "Selección de activos según sus objetivos", "Orientación sobre financiación"]),
        "valoracion": ("Valoración de inmuebles",
                       "Determinamos el valor de mercado de su inmueble a partir de operaciones reales y de la oferta de la zona.",
                       ["Estudio de inmuebles comparables", "Visita técnica al inmueble",
                        "Informe de valoración por escrito", "Recomendaciones para optimizar el precio"]),
        "asesoramiento-juridico": ("Asesoramiento documental y jurídico",
                                   "En colaboración con profesionales del ámbito jurídico, revisamos la documentación para garantizar la seguridad de cada operación.",
                                   ["Nota simple y verificación de cargas", "Certificado energético y cédula de habitabilidad",
                                    "Revisión de contratos", "Estimación de impuestos y gastos de la operación"]),
    },
    "footer_services": ["Compraventa", "Alquiler de viviendas", "Gestión de alquileres", "Inversión inmobiliaria", "Valoración de inmuebles"],

    "index": {
        "title": "Twins Real Estate | Agencia inmobiliaria",
        "description": "Agencia inmobiliaria especializada en compraventa, alquiler e inversión. Asesoramiento personalizado, información verificada y acompañamiento hasta la firma ante notario.",
        "eyebrow": "Agencia inmobiliaria",
        "h1": "Porque cada nueva etapa merece un lugar al que llamar <em>hogar</em>.",
        "slogan": "Porque cada nueva etapa merece un lugar al que llamar hogar.",
        "text": "Acompañamos a particulares, familias e inversores en la compra, la venta y el alquiler de inmuebles, con un asesoramiento cercano, riguroso y transparente en cada fase de la operación.",
        "btn_props": "Ver inmuebles",
        "btn_advice": "Solicitar asesoramiento",
        "pillars": ["Operaciones con seguridad jurídica", "Honorarios claros desde el inicio", "Atención personalizada"],
        "featured_eyebrow": "Cartera de inmuebles",
        "featured_title": "Inmuebles destacados",
        "featured_lead": "Una selección de viviendas disponibles, revisadas por nuestro equipo en cuanto a documentación, estado y precio de mercado.",
        "featured_all": "Ver todos los inmuebles",
        "about_eyebrow": "Quiénes somos",
        "about_title": "Más que una inmobiliaria, un aliado de confianza",
        "about_paras": [
            "Twins Real Estate nace con un propósito claro: que comprar, vender o alquilar una vivienda sea un proceso seguro, comprensible y sin sorpresas. Por ello, gestionamos cada operación de forma personalizada y con la máxima transparencia.",
            "Analizamos cada inmueble antes de comercializarlo, verificamos su situación registral y asesoramos a nuestros clientes con datos objetivos del mercado, para que cada decisión se tome con información completa.",
        ],
        "about_checks": [
            "Asesoramiento personalizado de principio a fin",
            "Verificación documental y registral de cada inmueble",
            "Honorarios y condiciones pactados por escrito",
            "Coordinación con notaría, entidades financieras y gestoría",
            "Seguimiento posterior a la firma",
        ],
        "about_btn": "Conozca nuestra agencia",
        "quote": "Sin compromiso, con toda la confianza.",
        "services_eyebrow": "Servicios",
        "services_title": "Soluciones inmobiliarias integrales",
        "services_lead": "Un servicio completo para propietarios, compradores, inquilinos e inversores, con el mismo nivel de exigencia en cada gestión.",
        "services_all": "Ver todos los servicios",
        "cta_title": "¿Desea vender, comprar o alquilar un inmueble?",
        "cta_text": "Solicite una primera reunión sin compromiso. Analizaremos su caso y le propondremos la estrategia más adecuada a sus objetivos.",
    },

    "propiedades": {
        "title": "Inmuebles en venta y alquiler",
        "description": "Pisos, áticos, casas y chalets en venta y alquiler. Consulte la cartera de Twins Real Estate y filtre por zona, tipo de inmueble, precio y número de dormitorios.",
        "h1": "Inmuebles en venta y alquiler",
        "text": "Consulte nuestra cartera de viviendas y utilice los filtros para encontrar el inmueble que mejor se adapta a sus necesidades.",
        "list_title": "Listado de inmuebles",
        "found": "inmuebles encontrados",
        "prices_note": "Precios de venta sin impuestos ni gastos de la operación.",
        "empty_title": "No hay inmuebles con estos criterios",
        "empty_text": "Modifique los filtros o indíquenos qué busca: le informaremos de las opciones disponibles, incluidas las que todavía no se han publicado.",
        "empty_btn": "Comuníquenos su búsqueda",
        "cta_title": "¿No encuentra lo que busca?",
        "cta_text": "Cuéntenos qué tipo de inmueble necesita y le avisaremos en cuanto dispongamos de una opción adecuada a su perfil.",
    },

    "nosotros": {
        "title": "Nosotros",
        "description": "Conozca Twins Real Estate: una agencia inmobiliaria centrada en las personas, con un asesoramiento cercano, riguroso y transparente.",
        "h1": "Más que una inmobiliaria, somos su aliado",
        "text": "Conozca quiénes somos, cómo trabajamos y los principios que guían cada una de nuestras operaciones.",
        "eyebrow": "Nuestra agencia",
        "h2": "Un proyecto nacido de la confianza",
        "paras": [
            "Twins Real Estate nace de una convicción sencilla: comprar, vender o alquilar una vivienda es una de las decisiones más importantes en la vida de una persona, y merece un acompañamiento profesional, honesto y cercano.",
            "Por ello hemos construido una agencia centrada en las personas, en la que cada cliente cuenta con un asesor de referencia, información clara en todo momento y un proceso ordenado desde la primera reunión hasta la entrega de llaves.",
            "Trabajamos con una cartera cuidadosamente seleccionada y con una red de profesionales colaboradores —notarías, abogados, gestorías y entidades financieras— que nos permite ofrecer un servicio integral.",
        ],
        "btn": "Hablar con un asesor",
        "purpose_eyebrow": "Propósito",
        "purpose_title": "Misión y visión",
        "mission": ("Nuestra misión", "Acompañar a nuestros clientes en cada decisión inmobiliaria con rigor, transparencia y cercanía, protegiendo sus intereses como si fueran propios."),
        "vision": ("Nuestra visión", "Ser la agencia de referencia para quienes buscan un trato personal y un servicio de calidad, construyendo relaciones duraderas basadas en la confianza."),
        "values_eyebrow": "Lo que nos define",
        "values_title": "Nuestros valores",
        "values_lead": "Los principios que guían cada decisión y cada relación con nuestros clientes.",
        "values": [
            ("Transparencia", "Información clara y veraz en cada fase, con condiciones pactadas por escrito y sin letra pequeña."),
            ("Rigor", "Verificamos la documentación de cada inmueble y fundamentamos nuestras recomendaciones en datos reales del mercado."),
            ("Compromiso", "Defendemos los intereses de nuestros clientes antes, durante y después de cada operación."),
            ("Cercanía", "Un asesor de referencia que conoce su caso y está disponible cuando lo necesita."),
        ],
        "cta_title": "Hablemos de su próximo proyecto",
        "cta_text": "Estaremos encantados de conocer sus necesidades y explicarle, sin compromiso, cómo podemos ayudarle.",
        "cta_secondary": "Ver inmuebles",
    },

    "servicios": {
        "title": "Servicios inmobiliarios",
        "description": "Compraventa, alquiler, gestión integral de alquileres, inversión, valoración de inmuebles y asesoramiento documental. Conozca los servicios de Twins Real Estate.",
        "h1": "Servicios inmobiliarios",
        "text": "Soluciones completas para propietarios, compradores, inquilinos e inversores, con el mismo nivel de exigencia en cada gestión.",
        "list_title": "Nuestros servicios",
        "process_eyebrow": "Metodología",
        "process_title": "Cómo trabajamos",
        "process_lead": "Un proceso claro y ordenado, diseñado para que cada etapa resulte sencilla y usted disponga siempre de la información necesaria.",
        "steps": [
            ("Primera reunión", "Analizamos sus necesidades, objetivos y plazos, y le explicamos con claridad nuestras condiciones."),
            ("Estudio y estrategia", "Valoramos el inmueble o seleccionamos las opciones que mejor se ajustan a su perfil."),
            ("Gestión y negociación", "Coordinamos las visitas, negociamos las condiciones y revisamos toda la documentación."),
            ("Firma y seguimiento", "Le acompañamos en la firma ante notario y en los trámites posteriores."),
        ],
        "faq_eyebrow": "Preguntas frecuentes",
        "faq_title": "Resolvemos sus dudas",
        "faqs": [
            ("¿Cuáles son sus honorarios?",
             "Nuestros honorarios dependen del tipo de servicio y de las características de la operación. En todos los casos se detallan y se acuerdan por escrito antes de iniciar cualquier gestión, sin costes ocultos."),
            ("¿Qué documentación necesito para vender mi vivienda?",
             "Con carácter general: DNI o NIE de los titulares, escritura de propiedad, último recibo del IBI, certificado de eficiencia energética, certificado de la comunidad de propietarios de estar al corriente de pago y, según la comunidad autónoma, cédula de habitabilidad. Si existe una hipoteca pendiente, también el certificado de deuda. Le ayudamos a reunir toda la documentación."),
            ("¿Quién paga los honorarios de la agencia en el alquiler de una vivienda?",
             "De acuerdo con la Ley 12/2023, por el derecho a la vivienda, los gastos de gestión inmobiliaria y de formalización del contrato de arrendamiento de vivienda corresponden al arrendador."),
            ("¿Realizan tasaciones para solicitar una hipoteca?",
             "Las tasaciones con validez hipotecaria solo pueden emitirlas sociedades de tasación homologadas por el Banco de España. Nosotros realizamos valoraciones de mercado orientadas a fijar un precio de venta o de alquiler realista y, si lo necesita, le ponemos en contacto con una sociedad de tasación."),
            ("¿Cuánto tiempo se tarda en vender un inmueble?",
             "Depende de la ubicación, del estado del inmueble y, sobre todo, de su precio. Un precio ajustado al mercado desde el primer día es el factor que más acorta los plazos. En la primera reunión le ofreceremos una estimación realista para su caso."),
        ],
        "cta_title": "¿Necesita asesoramiento sobre un servicio concreto?",
        "cta_text": "Cuéntenos su caso y le propondremos una solución adaptada a sus necesidades.",
    },

    "blog": {
        "title": "Blog inmobiliario",
        "description": "Guías, análisis y consejos sobre compraventa, alquiler, financiación e inversión inmobiliaria, elaborados por el equipo de Twins Real Estate.",
        "h1": "Blog y actualidad inmobiliaria",
        "text": "Guías prácticas, análisis de mercado y consejos para tomar decisiones inmobiliarias con criterio.",
        "list_title": "Artículos",
        "cta_title": "¿Tiene alguna duda sobre su caso concreto?",
        "cta_text": "Nuestro equipo le asesorará de forma personalizada y sin compromiso.",
    },

    "posts": {
        "comprar-o-alquilar-en-2026": dict(
            slug="comprar-o-alquilar-en-2026", category="Mercado", date_label="15 de enero de 2026",
            title="¿Comprar o alquilar vivienda en 2026? Claves para decidir",
            excerpt="Horizonte de permanencia, ahorro disponible, tipos de interés y flexibilidad: los factores que conviene analizar antes de tomar una decisión.",
            body="""
<p class="lead">No existe una respuesta universal. La decisión de comprar o alquilar depende de su situación personal, de su capacidad de ahorro y del tiempo que prevea permanecer en la vivienda. Estos son los factores que recomendamos analizar.</p>
<h2>1. El horizonte de permanencia</h2>
<p>La compra de una vivienda conlleva gastos iniciales significativos —impuestos, notaría, registro y, en su caso, gestoría y tasación— que solo se amortizan con el paso del tiempo. Como regla general, cuanto más largo sea el periodo que prevé residir en la vivienda, más sentido tiene la compra.</p>
<h2>2. El ahorro disponible</h2>
<p>Las entidades financieras suelen financiar hasta el 80 % del valor de tasación o del precio de compra, si este es inferior. Por tanto, además de la entrada, es necesario disponer de ahorro para cubrir los gastos e impuestos de la compraventa, que en la práctica representan una parte relevante del precio.</p>
<h2>3. El coste de la financiación</h2>
<p>Compare no solo el tipo de interés, sino la <strong>TAE</strong>, que incluye comisiones y gastos. Valore también si le conviene un préstamo a tipo fijo, que aporta estabilidad en la cuota, o a tipo variable o mixto, cuya cuota evoluciona con el Euríbor.</p>
<h2>4. La flexibilidad</h2>
<p>El alquiler ofrece mayor movilidad ante cambios laborales o familiares y evita inmovilizar ahorro. La compra, en cambio, permite construir patrimonio y fijar el coste de la vivienda a largo plazo.</p>
<h2>5. La comparación real de costes</h2>
<p>Para comparar ambas opciones con rigor, sume a la cuota hipotecaria el IBI, la comunidad de propietarios, el seguro y el mantenimiento, y compárelo con la renta de un inmueble equivalente. Tenga en cuenta también la rentabilidad que podría obtener del ahorro que no destinaría a la entrada.</p>
<h2>Nuestra recomendación</h2>
<p>Antes de decidir, elabore un presupuesto realista y solicite una simulación de financiación. En Twins Real Estate le ayudamos a analizar su caso concreto y a comparar escenarios con datos del mercado local.</p>
"""),
        "senales-revalorizacion-zona": dict(
            slug="senales-revalorizacion-zona", category="Inversión", date_label="12 de enero de 2026",
            title="Cinco señales de que una zona va a revalorizarse",
            excerpt="Aprenda a identificar los indicadores que suelen anticipar el crecimiento del valor de los inmuebles en un barrio.",
            body="""
<p class="lead">Anticipar la evolución de una zona es una de las claves de una buena inversión inmobiliaria. Aunque ningún indicador es infalible, existen señales que, combinadas, suelen preceder a una revalorización.</p>
<h2>1. Nuevas infraestructuras de transporte</h2>
<p>La llegada de una estación de metro, de tren o de nuevas líneas de autobús mejora la accesibilidad y suele tener un impacto directo en la demanda y en los precios.</p>
<h2>2. Planeamiento urbanístico y proyectos públicos</h2>
<p>Consulte el planeamiento municipal: nuevas zonas verdes, equipamientos, reurbanizaciones o cambios de uso del suelo son indicadores relevantes del futuro de un barrio.</p>
<h2>3. Llegada de comercios y servicios</h2>
<p>La apertura de establecimientos de restauración, comercios de proximidad, centros educativos o sanitarios suele reflejar —y reforzar— el interés por la zona.</p>
<h2>4. Rehabilitación de edificios</h2>
<p>Un número creciente de fachadas rehabilitadas, promociones de obra nueva o reformas integrales indica que propietarios y promotores confían en la evolución del entorno.</p>
<h2>5. Demanda de alquiler sostenida y poca oferta</h2>
<p>Cuando los inmuebles en alquiler se ocupan con rapidez y la oferta disponible es escasa, la presión de la demanda tiende a trasladarse también a los precios de venta.</p>
<h2>Una advertencia</h2>
<p>La revalorización pasada no garantiza la futura. Le recomendamos combinar estas señales con un análisis de rentabilidad y con su propio horizonte de inversión. Nuestro equipo puede elaborar para usted un estudio de la zona que le interese.</p>
"""),
        "guia-primera-vivienda": dict(
            slug="guia-primera-vivienda", category="Guías", date_label="8 de enero de 2026",
            title="Guía para comprar su primera vivienda",
            excerpt="Del presupuesto a la firma ante notario: los pasos, los documentos y las comprobaciones que no debe pasar por alto.",
            body="""
<p class="lead">Comprar una vivienda por primera vez implica numerosas decisiones y trámites. Esta guía resume, paso a paso, el proceso habitual en España.</p>
<h2>1. Defina su presupuesto</h2>
<p>Calcule cuánto puede destinar a la entrada, a los gastos de la compraventa y a la cuota mensual. Como referencia prudente, la cuota hipotecaria no debería superar aproximadamente un tercio de los ingresos netos del hogar.</p>
<h2>2. Estudie la financiación antes de buscar</h2>
<p>Solicitar un estudio previo a varias entidades le permitirá conocer el importe que podrían concederle y negociar con mayor seguridad. Compare siempre la TAE y las vinculaciones exigidas.</p>
<h2>3. Busque y visite con criterio</h2>
<p>Además del estado de la vivienda, valore la orientación, el entorno, los servicios cercanos, el estado del edificio y las posibles derramas aprobadas por la comunidad de propietarios.</p>
<h2>4. Compruebe la documentación</h2>
<ul>
<li><strong>Nota simple</strong> del Registro de la Propiedad: titularidad y cargas.</li>
<li>Último recibo del <strong>IBI</strong>.</li>
<li><strong>Certificado de la comunidad</strong> de estar al corriente de pago.</li>
<li><strong>Certificado de eficiencia energética</strong>, obligatorio para vender.</li>
<li><strong>Cédula de habitabilidad</strong> o documento equivalente, según la comunidad autónoma.</li>
</ul>
<h2>5. Firme un contrato de arras</h2>
<p>Una vez acordado el precio, lo habitual es firmar un contrato de arras y entregar una señal. Revise con atención el tipo de arras, los plazos y las condiciones, en especial si la compra depende de obtener financiación.</p>
<h2>6. Escritura pública e inscripción</h2>
<p>La compraventa se formaliza ante notario, que verifica la situación de la finca y la identidad de las partes. Posteriormente, deberá liquidar los impuestos correspondientes e inscribir la escritura en el Registro de la Propiedad.</p>
<h2>Le acompañamos en todo el proceso</h2>
<p>En Twins Real Estate revisamos la documentación, coordinamos la negociación y le acompañamos hasta la entrega de llaves.</p>
"""),
        "preparar-vivienda-alquiler": dict(
            slug="preparar-vivienda-alquiler", category="Alquiler", date_label="2 de enero de 2026",
            title="Cómo preparar su vivienda para alquilarla antes",
            excerpt="Pequeñas mejoras, una buena presentación y un precio ajustado marcan la diferencia a la hora de atraer a buenos inquilinos.",
            body="""
<p class="lead">Una vivienda bien preparada se alquila antes y atrae a inquilinos más solventes. Estos son los aspectos que recomendamos cuidar antes de publicarla.</p>
<h2>1. Puesta a punto</h2>
<p>Revise instalaciones, grifería, persianas y electrodomésticos. Una mano de pintura en tonos neutros y la reparación de pequeños desperfectos mejoran notablemente la primera impresión.</p>
<h2>2. Documentación obligatoria</h2>
<p>Para anunciar y alquilar una vivienda es obligatorio disponer del <strong>certificado de eficiencia energética</strong>. Según la comunidad autónoma, también puede ser necesaria la cédula de habitabilidad. Recuerde, además, que la fianza debe depositarse en el organismo autonómico competente.</p>
<h2>3. Presentación y fotografía</h2>
<p>Unas fotografías profesionales, con buena luz y espacios ordenados, son el primer filtro de los interesados. Un anuncio claro y completo reduce visitas innecesarias.</p>
<h2>4. Un precio ajustado al mercado</h2>
<p>Un precio superior al de mercado alarga el tiempo de desocupación, que tiene un coste real. Compruebe también si la vivienda se encuentra en una zona declarada de mercado residencial tensionado, ya que pueden aplicarse limitaciones a la renta.</p>
<h2>5. Selección del inquilino</h2>
<p>Verifique la solvencia de los candidatos y valore la contratación de un seguro de impago de alquiler. Un contrato bien redactado, conforme a la Ley de Arrendamientos Urbanos, protege a ambas partes.</p>
<h2>Deje la gestión en manos profesionales</h2>
<p>Nuestro servicio de alquiler incluye la valoración, la difusión, la selección del inquilino y la formalización del contrato.</p>
"""),
        "que-revisar-contrato-arras": dict(
            slug="que-revisar-contrato-arras", category="Legal", date_label="28 de diciembre de 2025",
            title="Qué revisar antes de firmar un contrato de arras",
            excerpt="Los elementos esenciales que debe comprobar antes de comprometerse en la compra o la venta de un inmueble.",
            body="""
<p class="lead">El contrato de arras es el documento con el que comprador y vendedor se comprometen a formalizar la compraventa. Antes de firmarlo, conviene revisar con detalle los siguientes aspectos.</p>
<h2>1. El tipo de arras</h2>
<p>Las más habituales son las <strong>arras penitenciales</strong> (artículo 1454 del Código Civil): si el comprador desiste, pierde la señal entregada; si desiste el vendedor, debe devolverla duplicada. Existen también arras confirmatorias y penales, con efectos distintos. El contrato debe indicarlo de forma expresa.</p>
<h2>2. Identificación de las partes y del inmueble</h2>
<p>Compruebe que los datos de los titulares coinciden con la nota simple y que el inmueble se identifica con su referencia registral y catastral, incluidos anejos como plazas de garaje o trasteros.</p>
<h2>3. Precio, señal y forma de pago</h2>
<p>El contrato debe recoger el precio total, el importe entregado como señal y cómo se abonará el resto en el momento de la escritura.</p>
<h2>4. Cargas y situación del inmueble</h2>
<p>Deje constancia de si el inmueble se transmitirá libre de cargas, arrendatarios y ocupantes, y al corriente de pago de impuestos y gastos de comunidad.</p>
<h2>5. Plazo para la escritura</h2>
<p>Fije una fecha límite para la firma ante notario y qué ocurre si no se cumple. Si la compra depende de un préstamo hipotecario, valore incluir una condición relativa a su concesión.</p>
<h2>6. Reparto de gastos e impuestos</h2>
<p>Especifique quién asume cada gasto. Con carácter general, la plusvalía municipal corresponde al vendedor y el impuesto de transmisiones patrimoniales o, en obra nueva, el IVA y el impuesto de actos jurídicos documentados, al comprador.</p>
<h2>Revisión profesional</h2>
<p>Recomendamos que un profesional revise el contrato antes de su firma. En Twins Real Estate preparamos y revisamos los contratos de arras de las operaciones que intermediamos.</p>
"""),
        "tendencias-interiorismo-2026": dict(
            slug="tendencias-interiorismo-2026", category="Diseño", date_label="20 de diciembre de 2025",
            title="Tendencias de interiorismo para 2026",
            excerpt="Materiales naturales, espacios flexibles y eficiencia energética: las claves que definen los hogares de este año.",
            body="""
<p class="lead">El interiorismo de 2026 apuesta por hogares cálidos, versátiles y sostenibles. Estas son las tendencias que observamos con mayor frecuencia en las viviendas más demandadas.</p>
<h2>1. Materiales naturales</h2>
<p>La madera, la piedra, el lino y la cerámica artesanal aportan calidez y durabilidad. Se buscan acabados honestos y texturas que envejezcan bien.</p>
<h2>2. Espacios flexibles</h2>
<p>La consolidación del teletrabajo ha convertido las zonas de trabajo en casa en un requisito. Se valoran los espacios que pueden transformarse según el momento del día.</p>
<h2>3. Paletas cálidas y serenas</h2>
<p>Los tonos arena, terracota, verde oliva y blanco roto sustituyen a los grises fríos y crean ambientes más acogedores.</p>
<h2>4. Eficiencia energética</h2>
<p>Aislamiento, carpinterías eficientes, aerotermia e iluminación LED no solo reducen el consumo: mejoran la calificación energética y, con ella, el atractivo del inmueble en el mercado.</p>
<h2>5. Iluminación por capas</h2>
<p>La combinación de luz general, puntual y ambiental permite adaptar cada estancia a distintos usos y realza la arquitectura del espacio.</p>
<h2>Un valor añadido en la venta</h2>
<p>Una presentación cuidada puede acelerar la venta o el alquiler de un inmueble. Si está pensando en vender, le asesoramos sobre las mejoras con mejor relación entre coste e impacto.</p>
"""),
        "mitos-hipoteca": dict(
            slug="mitos-hipoteca", category="Financiación", date_label="14 de diciembre de 2025",
            title="Hipotecas: cinco mitos que conviene desterrar",
            excerpt="Aclaramos algunas de las ideas más extendidas —y no siempre ciertas— sobre la financiación de la vivienda.",
            body="""
<p class="lead">La hipoteca es, para la mayoría de las familias, el compromiso financiero más importante de su vida. Estos son algunos mitos habituales que conviene matizar.</p>
<h2>Mito 1: «Solo importa el tipo de interés»</h2>
<p>El tipo de interés es relevante, pero no suficiente. La <strong>TAE</strong> incorpora comisiones y otros costes, y es la referencia adecuada para comparar ofertas. Valore también el coste de los productos vinculados que exige cada entidad.</p>
<h2>Mito 2: «Siempre necesitaré el 20 % de entrada»</h2>
<p>Lo habitual es que las entidades financien hasta el 80 % del valor de la vivienda. No obstante, existen programas públicos, como la línea de avales del ICO para jóvenes y familias con menores a cargo, que permiten acceder a una financiación superior si se cumplen determinados requisitos.</p>
<h2>Mito 3: «Una vez firmada, no puedo cambiarla»</h2>
<p>Es posible negociar una novación con su entidad o trasladar el préstamo a otra mediante una subrogación. Conviene analizar los costes y el ahorro de cada alternativa.</p>
<h2>Mito 4: «Amortizar anticipadamente está muy penalizado»</h2>
<p>La Ley 5/2019, reguladora de los contratos de crédito inmobiliario, limita las comisiones por amortización anticipada. Revise su contrato para conocer las condiciones que le son aplicables.</p>
<h2>Mito 5: «Los autónomos no consiguen hipoteca»</h2>
<p>Los trabajadores por cuenta propia pueden obtener financiación. Normalmente se les exige acreditar ingresos estables mediante sus declaraciones de la renta y del IVA de los últimos ejercicios.</p>
<h2>Asesórese antes de firmar</h2>
<p>Le orientamos en la búsqueda de financiación y le ponemos en contacto con profesionales de confianza para que obtenga las mejores condiciones.</p>
"""),
    },

    "contacto": {
        "title": "Contacto",
        "description": "Contacte con Twins Real Estate para comprar, vender o alquilar un inmueble. Atención personalizada con cita previa, presencial o por videollamada.",
        "h1": "Contacto",
        "text": "Estaremos encantados de atenderle. Cuéntenos su caso y un asesor se pondrá en contacto con usted a la mayor brevedad.",
        "section_aria": "Datos de contacto y formulario",
        "email_title": "Correo electrónico",
        "instagram_title": "Instagram",
        "hours_title": "Horario de atención",
        "meetings_title": "Reuniones y visitas",
        "meetings_text": "Atendemos con cita previa, de forma presencial o por videollamada.",
        "form_title": "Envíenos su consulta",
        "form_lead": "Los campos marcados con * son obligatorios.",
        "labels": {
            "nombre": "Nombre y apellidos *",
            "email": "Correo electrónico *",
            "telefono": "Teléfono",
            "asunto": "Motivo de la consulta",
            "referencia": "Referencia del inmueble",
            "mensaje": "Mensaje *",
        },
        "ref_placeholder": "Por ejemplo, TRE-001",
        "ref_hint": "Opcional. Figura en la ficha de cada inmueble.",
        "honeypot": "No rellene este campo",
        "privacy_html": 'He leído y acepto la <a href="%%PRIVACY%%">política de privacidad</a>. *',
        "subject_placeholder": "Seleccione una opción",
        "subjects": ["Compra de un inmueble", "Venta de un inmueble", "Alquiler de un inmueble", "Gestión de alquileres",
                     "Valoración de un inmueble", "Asesoramiento para inversión", "Solicitar una cita", "Otra consulta"],
        "legal_html": '<strong>Información básica sobre protección de datos.</strong> Responsable: Twins Real Estate. Finalidad: atender su consulta y, en su caso, remitirle la información solicitada. Legitimación: su consentimiento. Destinatarios: no se cederán datos a terceros, salvo obligación legal. Derechos: acceso, rectificación, supresión, oposición, limitación del tratamiento y portabilidad, tal como se detalla en la <a href="%%PRIVACY%%">política de privacidad</a>.',
        "submit": "Enviar consulta",
    },

    "owner": {
        "pending": "[pendiente de completar]",
        "rows": [
            ("Titular", "pending", "(nombre y apellidos o razón social)"),
            ("Nombre comercial", "Twins Real Estate", ""),
            ("NIF", "pending", ""),
            ("Domicilio", "pending", ""),
            ("Correo electrónico", "email", ""),
            ("Datos registrales", "pending", "(Registro Mercantil, si se trata de una sociedad)"),
            ("Registro de agentes inmobiliarios", "pending", "(número de inscripción, cuando la normativa autonómica lo exija)"),
        ],
    },

    "legal": {
        "aviso-legal.html": dict(
            title="Aviso legal",
            description="Aviso legal del sitio web de Twins Real Estate: datos identificativos del titular y condiciones de uso.",
            body="""
<h2>1. Datos identificativos</h2>
<p>En cumplimiento del artículo 10 de la Ley 34/2002, de 11 de julio, de servicios de la sociedad de la información y de comercio electrónico (LSSI-CE), se facilitan los siguientes datos del titular de este sitio web:</p>
%%OWNER%%
<h2>2. Objeto y aceptación</h2>
<p>El presente aviso legal regula el acceso y el uso de este sitio web, cuya finalidad es informar sobre los servicios de intermediación y asesoramiento inmobiliario de Twins Real Estate. El acceso al sitio implica la aceptación de estas condiciones.</p>
<h2>3. Condiciones de uso</h2>
<p>El usuario se compromete a hacer un uso adecuado del sitio web y de sus contenidos, de conformidad con la ley, la buena fe y el orden público, y a no emplearlos para actividades ilícitas o que puedan dañar los derechos de terceros o el funcionamiento del sitio.</p>
<h2>4. Información sobre los inmuebles</h2>
<p>La información publicada sobre los inmuebles (precio, superficie, características e imágenes) tiene carácter orientativo y no constituye una oferta contractual. Puede estar sujeta a errores, a modificaciones o a la retirada del inmueble sin previo aviso. Salvo indicación en contrario, los precios no incluyen impuestos ni gastos derivados de la operación.</p>
<p>De conformidad con la normativa de protección de los consumidores en la compraventa y el arrendamiento de viviendas, se encuentra a disposición de los interesados la información legalmente exigible sobre cada inmueble, que puede solicitarse a través de los medios de contacto indicados.</p>
<h2>5. Propiedad intelectual e industrial</h2>
<p>Los contenidos de este sitio web —textos, diseño, logotipos, marcas e imágenes— son titularidad de Twins Real Estate o de terceros que han autorizado su uso. Queda prohibida su reproducción, distribución o transformación sin autorización expresa.</p>
<h2>6. Responsabilidad</h2>
<p>Twins Real Estate no se responsabiliza de los daños derivados de interrupciones del servicio, de errores técnicos ajenos a su control ni del uso indebido del sitio por parte de los usuarios. Tampoco asume responsabilidad por los contenidos de sitios web de terceros a los que pueda enlazarse.</p>
<h2>7. Protección de datos</h2>
<p>El tratamiento de los datos personales se rige por la <a href="%%PRIVACY%%">política de privacidad</a>, y el uso de tecnologías de almacenamiento, por la <a href="%%COOKIES%%">política de cookies</a>.</p>
<h2>8. Idioma</h2>
<p>Este sitio web se ofrece en castellano, catalán e inglés. En caso de discrepancia entre versiones, prevalecerá la versión en castellano.</p>
<h2>9. Legislación aplicable y jurisdicción</h2>
<p>Estas condiciones se rigen por la legislación española. Para la resolución de cualquier controversia, las partes se someten a los juzgados y tribunales que resulten competentes conforme a la normativa aplicable, en particular la de protección de los consumidores y usuarios.</p>
"""),
        "privacidad.html": dict(
            title="Política de privacidad",
            description="Política de privacidad de Twins Real Estate: cómo tratamos sus datos personales conforme al RGPD y a la LOPDGDD.",
            body="""
<p>Twins Real Estate se compromete a proteger su privacidad y a tratar sus datos personales conforme al Reglamento (UE) 2016/679, General de Protección de Datos (RGPD), y a la Ley Orgánica 3/2018, de Protección de Datos Personales y garantía de los derechos digitales (LOPDGDD).</p>
<h2>1. Responsable del tratamiento</h2>
%%OWNER%%
<h2>2. Datos que tratamos</h2>
<p>Tratamos los datos que usted nos facilita a través del formulario de contacto, por correo electrónico o mediante nuestras redes sociales: nombre y apellidos, datos de contacto, el contenido de su consulta y, en su caso, la información necesaria para la prestación de nuestros servicios.</p>
<h2>3. Finalidades y base jurídica</h2>
<ul>
<li><strong>Atender sus consultas</strong> y remitirle la información solicitada. Base jurídica: su consentimiento (art. 6.1.a RGPD).</li>
<li><strong>Gestionar la relación precontractual y contractual</strong> derivada de nuestros servicios de intermediación y asesoramiento inmobiliario. Base jurídica: la ejecución de un contrato o de medidas precontractuales (art. 6.1.b RGPD).</li>
<li><strong>Cumplir las obligaciones legales</strong> aplicables, entre ellas las derivadas de la Ley 10/2010, de prevención del blanqueo de capitales y de la financiación del terrorismo, y de la normativa fiscal. Base jurídica: obligación legal (art. 6.1.c RGPD).</li>
</ul>
<p>No se adoptan decisiones automatizadas ni se elaboran perfiles con sus datos.</p>
<h2>4. Plazo de conservación</h2>
<p>Los datos de las consultas se conservarán durante el tiempo necesario para atenderlas y, como máximo, durante un año si no se inicia una relación contractual. Los datos vinculados a un contrato se conservarán mientras dure la relación y, posteriormente, durante los plazos de prescripción de las responsabilidades legales.</p>
<h2>5. Destinatarios</h2>
<p>No cedemos sus datos a terceros, salvo obligación legal. Pueden acceder a ellos los proveedores que nos prestan servicios de correo electrónico y de alojamiento web, en calidad de encargados del tratamiento y con las garantías exigidas por el RGPD. Cuando alguno de estos proveedores se encuentre fuera del Espacio Económico Europeo, la transferencia se ampara en una decisión de adecuación de la Comisión Europea, como el Marco de Privacidad de Datos UE-EE. UU., o en cláusulas contractuales tipo.</p>
<h2>6. Sus derechos</h2>
<p>Puede ejercer sus derechos de acceso, rectificación, supresión, oposición, limitación del tratamiento y portabilidad, así como retirar su consentimiento en cualquier momento, escribiendo a <a href="mailto:%%EMAIL%%">%%EMAIL%%</a> e indicando el derecho que desea ejercer.</p>
<p>Si considera que el tratamiento de sus datos no se ajusta a la normativa, puede presentar una reclamación ante la Agencia Española de Protección de Datos (<a href="https://www.aepd.es" target="_blank" rel="noopener noreferrer">www.aepd.es</a>).</p>
<h2>7. Seguridad</h2>
<p>Aplicamos medidas técnicas y organizativas adecuadas para garantizar la confidencialidad, integridad y disponibilidad de sus datos, entre ellas el cifrado de las comunicaciones del sitio web mediante HTTPS.</p>
<h2>8. Menores de edad</h2>
<p>Este sitio web no está dirigido a menores de 14 años, y no tratamos conscientemente sus datos personales.</p>
<h2>9. Cambios en esta política</h2>
<p>Podemos actualizar esta política para adaptarla a cambios normativos o de nuestros servicios. La fecha de la última actualización figura al inicio de esta página.</p>
"""),
        "cookies.html": dict(
            title="Política de cookies",
            description="Política de cookies de Twins Real Estate: información sobre las tecnologías de almacenamiento utilizadas en este sitio web.",
            body="""
<h2>1. ¿Utilizamos cookies?</h2>
<p>Este sitio web <strong>no utiliza cookies</strong> propias ni de terceros con fines analíticos, publicitarios o de seguimiento. Por este motivo, no se muestra un aviso de consentimiento de cookies.</p>
<h2>2. Almacenamiento local</h2>
<p>Si usted marca un inmueble como favorito, su navegador guarda únicamente la referencia de ese inmueble mediante la tecnología de almacenamiento local (<em>localStorage</em>). Esta información no incluye datos personales, no se envía a ningún servidor y permanece exclusivamente en su dispositivo. Del mismo modo, si cambia el tema visual del sitio (oscuro o crema), se guarda únicamente esa preferencia.</p>
<p>Se trata de un almacenamiento técnico necesario para prestar una funcionalidad solicitada expresamente por usted, por lo que está exento del deber de consentimiento conforme al artículo 22.2 de la LSSI-CE. Puede eliminarlo en cualquier momento desde la configuración de su navegador.</p>
<div class="table-scroll">
<table>
<thead>
<tr><th scope="col">Nombre</th><th scope="col">Tipo</th><th scope="col">Finalidad</th><th scope="col">Duración</th></tr>
</thead>
<tbody>
<tr><td>twins:favoritos</td><td>Almacenamiento local (propio)</td><td>Recordar los inmuebles marcados como favoritos</td><td>Hasta que el usuario lo elimine</td></tr>
<tr><td>twins:tema</td><td>Almacenamiento local (propio)</td><td>Recordar el tema elegido (oscuro o crema)</td><td>Hasta que el usuario lo elimine</td></tr>
</tbody>
</table>
</div>
<h2>3. Recursos de terceros</h2>
<p>Para mostrar las tipografías del sitio, su navegador descarga archivos del servicio Google Fonts, prestado por Google. Este servicio no instala cookies, aunque, como en cualquier conexión a internet, recibe la dirección IP del dispositivo que realiza la solicitud. Puede consultar la política de privacidad de Google en <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">policies.google.com/privacy</a>.</p>
<p>Los enlaces a Instagram solo le dirigen a esa red social cuando usted hace clic en ellos; este sitio no incorpora contenidos ni complementos de redes sociales.</p>
<h2>4. Cambios en esta política</h2>
<p>Si en el futuro incorporamos cookies que requieran su consentimiento, actualizaremos esta política y habilitaremos el mecanismo de consentimiento correspondiente antes de su instalación.</p>
"""),
    },

    "error404": {
        "title": "Página no encontrada",
        "description": "La página que busca no existe o ha cambiado de dirección.",
        "h1": "Página no encontrada",
        "text": "La página que busca no existe o ha cambiado de dirección. Le invitamos a volver al inicio o a consultar nuestra cartera de inmuebles.",
        "home": "Volver al inicio",
        "props": "Ver inmuebles",
    },
}
