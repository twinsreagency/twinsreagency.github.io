"""Website copy in English (British English)."""

C = {
    "code": "en",
    "lang": "en",
    "locale": "en_GB",
    "label": "English",
    "abbr": "EN",
    "slugs": {"index": "home", "propiedades": "properties", "servicios": "services", "nosotros": "about", "blog": "blog",
              "contacto": "contact", "aviso-legal": "legal-notice", "privacidad": "privacy", "cookies": "cookies"},

    "ui": {
        "skip": "Skip to main content",
        "home_aria": "Twins Real Estate, go to the home page",
        "nav_aria": "Main navigation",
        "nav": {
            "index.html": "Home",
            "propiedades.html": "Properties",
            "servicios.html": "Services",
            "nosotros.html": "About us",
            "blog.html": "Blog",
            "contacto.html": "Contact",
        },
        "cta_nav": "Book a meeting",
        "menu_open": "Open menu",
        "menu_close": "Close menu",
        "lang_aria": "Language",
        "footer_about": "Real estate agency specialising in sales, lettings and investment. Personal, rigorous and transparent advice on every transaction.",
        "footer_nav_title": "Navigation",
        "footer_nav_aria": "Site links",
        "footer_services_title": "Services",
        "footer_contact_title": "Contact",
        "hours_html": "Monday to Friday: 9:00&nbsp;–&nbsp;18:00<br>Saturday: 10:00&nbsp;–&nbsp;14:00",
        "rights": "All rights reserved.",
        "legal_aria": "Legal information",
        "legal": {
            "aviso-legal.html": "Legal notice",
            "privacidad.html": "Privacy policy",
            "cookies.html": "Cookie policy",
        },
        "instagram_aria": "Twins Real Estate on Instagram (opens in a new tab)",
        "mail_aria": "Send an email to Twins Real Estate",
        "new_tab": "(opens in a new tab)",
        "back_top": "Back to top",
        "breadcrumb_aria": "Breadcrumb",
        "home": "Home",
        "cta_primary": "Book a meeting",
        "cta_mail": "Email us",
        "more_info": "Learn more",
        "about": "about",
        "read_article": "Read article",
        "min_read": "{} min read",
        "featured": "Featured",
        "other_posts": "More articles",
        "back_blog": "Back to the blog",
        "consult": "Speak to an adviser",
        "article_notice": "This article is for information purposes only and does not constitute legal, tax or financial advice. Regulations may vary between Spanish regions; please consult a professional about your specific case.",
        "updated": "Last updated: {}",
        "updated_date": "27 September 2026",
        "theme_to_light": "Switch to light theme",
        "theme_to_dark": "Switch to dark theme",
        "scroll_hint": "Scroll to explore",
        "commitments_title": "Our commitments",
    },

    "search": {
        "title_home": "Find your property",
        "title_filter": "Filter properties",
        "submit": "Search",
        "reset": "Reset",
        "fields": {
            "operacion": ("Transaction", "All"),
            "tipo": ("Property type", "All"),
            "zona": ("Area", "All"),
            "precio": ("Maximum price", "No limit"),
            "dormitorios": ("Bedrooms", "Any"),
        },
        "options": {
            "operacion": ["For sale", "For rent"],
            "tipo": ["Flat or apartment", "Penthouse", "House or villa", "Plot of land", "Office", "Commercial premises"],
            "zona": ["City centre", "North", "South", "East", "West", "Outskirts and countryside"],
            "precio": ["Up to €200,000", "Up to €400,000", "Up to €700,000", "Up to €1,000,000"],
            "dormitorios": ["1 or more", "2 or more", "3 or more", "4 or more", "5 or more"],
        },
    },

    "prop": {
        "sale": "For sale",
        "rent": "For rent",
        "per_month": "/ month",
        "bed": ("bedroom", "bedrooms"),
        "bath": ("bathroom", "bathrooms"),
        "request": "Request information",
        "fav": "Save {} to favourites",
        "features_aria": "Features",
        "ref": "Ref.",
    },

    "properties": {
        "TRE-001": ("Modern house with lake views", "North · Los Lagos residential estate", "Featured"),
        "TRE-002": ("Penthouse in the old town", "City centre · Old town", "New"),
        "TRE-003": ("Bright flat with terrace", "South · Jardines del Valle", None),
        "TRE-004": ("Contemporary villa with swimming pool", "East · Club de Campo", "Exclusive"),
        "TRE-005": ("Loft in the creative district", "West · Creative District", None),
        "TRE-006": ("Country house with garden", "Countryside · Valle Verde", "Price reduced"),
        "TRE-007": ("Flat with panoramic views", "City centre · Torre Mirador", "New"),
        "TRE-008": ("Family home with large garden", "North · Los Bosques", None),
        "TRE-009": ("Minimalist designer residence", "East · Colinas del Sol", "Exclusive"),
    },

    "commitments": [
        ("Verified information", "We review the land registry extract, any charges and the energy certificate before listing each property."),
        ("Transparent fees", "All financial terms are agreed in writing before any work begins."),
        ("Confidentiality", "We process your personal data in accordance with the GDPR and Spanish data protection law."),
        ("Support through to completion", "We coordinate the notary, financing and all post-sale formalities."),
    ],

    "services": {
        "compraventa": ("Property sales and purchases",
                        "We guide you through the sale or purchase of your property, from the initial valuation to the signing of the title deed.",
                        ["Market study and pricing", "Professional photography and marketing",
                         "Viewings and negotiation", "Deposit contract and coordination with the notary"]),
        "alquiler": ("Residential lettings",
                     "We select the right tenant through a rigorous process and draw up a tenancy agreement in accordance with the Spanish Urban Leases Act.",
                     ["Tenant referencing and solvency checks", "Drafting and review of the agreement",
                      "Lodging the deposit with the regional authority", "Inventory and handover of keys"]),
        "gestion-alquileres": ("Full rental management",
                               "We manage your property so that you earn a return without having to deal with the day-to-day.",
                               ["Rent collection and arrears monitoring", "Coordination of repairs and maintenance",
                                "Tenant liaison", "Regular reports to the owner"]),
        "inversion": ("Investment advice",
                      "We identify opportunities and assess their return using objective criteria tailored to your profile.",
                      ["Gross and net yield analysis", "Study of the area and demand",
                       "Selection of assets to match your goals", "Guidance on financing"]),
        "valoracion": ("Property valuation",
                       "We determine the market value of your property based on real transactions and the local supply.",
                       ["Study of comparable properties", "On-site technical visit",
                        "Written valuation report", "Recommendations to optimise the price"]),
        "asesoramiento-juridico": ("Legal and documentary advice",
                                   "Working with legal professionals, we review all documentation to ensure every transaction is secure.",
                                   ["Land registry extract and charges check", "Energy certificate and certificate of occupancy",
                                    "Contract review", "Estimate of taxes and transaction costs"]),
    },
    "footer_services": ["Sales and purchases", "Residential lettings", "Rental management", "Property investment", "Property valuation"],

    "index": {
        "title": "Twins Real Estate | Real estate agency",
        "description": "Real estate agency specialising in sales, lettings and investment in Spain. Personal advice, verified information and support through to signing before a notary.",
        "eyebrow": "Real estate agency",
        "h1": "Because every new chapter deserves a place to call <em>home</em>.",
        "slogan": "Because every new chapter deserves a place to call home.",
        "text": "We support individuals, families and investors in buying, selling and renting property, with personal, rigorous and transparent advice at every stage of the transaction.",
        "btn_props": "View properties",
        "btn_advice": "Request advice",
        "pillars": ["Legally secure transactions", "Clear fees from the outset", "Personal service"],
        "featured_eyebrow": "Property portfolio",
        "featured_title": "Featured properties",
        "featured_lead": "A selection of available homes, reviewed by our team in terms of documentation, condition and market price.",
        "featured_all": "View all properties",
        "about_eyebrow": "About us",
        "about_title": "More than an estate agency, a trusted partner",
        "about_paras": [
            "Twins Real Estate was founded with a clear purpose: to make buying, selling or renting a home a secure, understandable process with no surprises. That is why we handle every transaction on a personal basis and with complete transparency.",
            "We assess each property before marketing it, verify its land registry status and advise our clients with objective market data, so that every decision is made with complete information.",
        ],
        "about_checks": [
            "Personal advice from start to finish",
            "Documentary and land registry checks on every property",
            "Fees and terms agreed in writing",
            "Coordination with notaries, lenders and agents",
            "Follow-up after completion",
        ],
        "about_btn": "Discover our agency",
        "quote": "No obligation, complete confidence.",
        "services_eyebrow": "Services",
        "services_title": "Comprehensive property solutions",
        "services_lead": "A complete service for owners, buyers, tenants and investors, with the same high standards in every task.",
        "services_all": "View all services",
        "cta_title": "Are you looking to sell, buy or rent a property?",
        "cta_text": "Book an initial meeting with no obligation. We will review your situation and propose the strategy best suited to your goals.",
    },

    "propiedades": {
        "title": "Properties for sale and rent",
        "description": "Flats, penthouses, houses and villas for sale and rent. Browse the Twins Real Estate portfolio and filter by area, property type, price and number of bedrooms.",
        "h1": "Properties for sale and rent",
        "text": "Browse our portfolio and use the filters to find the property that best suits your needs.",
        "list_title": "Property listings",
        "found": "properties found",
        "prices_note": "Sale prices exclude taxes and transaction costs.",
        "empty_title": "No properties match these criteria",
        "empty_text": "Adjust the filters or tell us what you are looking for: we will let you know about available options, including those not yet published.",
        "empty_btn": "Tell us what you need",
        "cta_title": "Can’t find what you are looking for?",
        "cta_text": "Tell us what type of property you need and we will let you know as soon as a suitable option becomes available.",
    },

    "nosotros": {
        "title": "About us",
        "description": "Discover Twins Real Estate: a people-focused real estate agency offering personal, rigorous and transparent advice.",
        "h1": "More than an estate agency, your trusted partner",
        "text": "Find out who we are, how we work and the principles that guide each of our transactions.",
        "eyebrow": "Our agency",
        "h2": "A project built on trust",
        "paras": [
            "Twins Real Estate was born from a simple conviction: buying, selling or renting a home is one of the most important decisions in a person’s life, and it deserves professional, honest and personal support.",
            "That is why we have built a people-focused agency, where every client has a dedicated adviser, clear information at all times and an orderly process from the first meeting to the handover of keys.",
            "We work with a carefully selected portfolio and a network of trusted professionals —notaries, lawyers, administrative agents and lenders— that allows us to offer a comprehensive service.",
        ],
        "btn": "Speak to an adviser",
        "purpose_eyebrow": "Purpose",
        "purpose_title": "Mission and vision",
        "mission": ("Our mission", "To support our clients in every property decision with rigour, transparency and a personal approach, protecting their interests as if they were our own."),
        "vision": ("Our vision", "To be the agency of choice for those seeking a personal service of the highest quality, building lasting relationships based on trust."),
        "values_eyebrow": "What defines us",
        "values_title": "Our values",
        "values_lead": "The principles that guide every decision and every relationship with our clients.",
        "values": [
            ("Transparency", "Clear and accurate information at every stage, with terms agreed in writing and no small print."),
            ("Rigour", "We verify the documentation of every property and base our recommendations on real market data."),
            ("Commitment", "We defend our clients’ interests before, during and after every transaction."),
            ("Personal approach", "A dedicated adviser who knows your case and is available whenever you need them."),
        ],
        "cta_title": "Let’s talk about your next project",
        "cta_text": "We would be delighted to learn about your needs and explain, with no obligation, how we can help.",
        "cta_secondary": "View properties",
    },

    "servicios": {
        "title": "Real estate services",
        "description": "Sales, lettings, full rental management, investment, property valuation and documentary advice. Discover the services of Twins Real Estate.",
        "h1": "Real estate services",
        "text": "Complete solutions for owners, buyers, tenants and investors, with the same high standards in every task.",
        "list_title": "Our services",
        "process_eyebrow": "Methodology",
        "process_title": "How we work",
        "process_lead": "A clear, structured process designed to keep every stage simple and ensure you always have the information you need.",
        "steps": [
            ("Initial meeting", "We discuss your needs, goals and timescales, and explain our terms clearly."),
            ("Study and strategy", "We value the property or select the options that best match your profile."),
            ("Management and negotiation", "We coordinate viewings, negotiate the terms and review all documentation."),
            ("Completion and follow-up", "We accompany you at the signing before the notary and through the subsequent formalities."),
        ],
        "faq_eyebrow": "Frequently asked questions",
        "faq_title": "Answers to your questions",
        "faqs": [
            ("What are your fees?",
             "Our fees depend on the type of service and the characteristics of the transaction. In every case they are set out and agreed in writing before any work begins, with no hidden costs."),
            ("What documents do I need to sell my home?",
             "As a general rule: the owners’ ID (DNI, NIE or passport), the title deed, the latest property tax (IBI) receipt, the energy performance certificate, a certificate from the homeowners’ association confirming that payments are up to date and, depending on the region, the certificate of occupancy. If there is an outstanding mortgage, the certificate of outstanding debt is also required. We will help you gather all the documentation."),
            ("Who pays the agency fees when renting out a home?",
             "Under Spanish Law 12/2023 on the right to housing, estate agency fees and the costs of formalising a residential tenancy agreement are payable by the landlord."),
            ("Do you carry out valuations for mortgage applications?",
             "Valuations valid for mortgage purposes can only be issued by appraisal companies approved by the Bank of Spain. We carry out market valuations aimed at setting a realistic sale or rental price and, if required, we can put you in touch with an approved appraisal company."),
            ("How long does it take to sell a property?",
             "It depends on the location, the condition of the property and, above all, its price. A price in line with the market from day one is the factor that most shortens the timescale. At our first meeting we will give you a realistic estimate for your case."),
        ],
        "cta_title": "Do you need advice on a specific service?",
        "cta_text": "Tell us about your situation and we will propose a solution tailored to your needs.",
    },

    "blog": {
        "title": "Real estate blog",
        "description": "Guides, analysis and advice on buying, selling, renting, financing and property investment in Spain, written by the Twins Real Estate team.",
        "h1": "Blog and property news",
        "text": "Practical guides, market analysis and advice to help you make informed property decisions.",
        "list_title": "Articles",
        "cta_title": "Do you have a question about your specific case?",
        "cta_text": "Our team will advise you personally and with no obligation.",
    },

    "posts": {
        "comprar-o-alquilar-en-2026": dict(
            slug="buy-or-rent-in-2026", category="Market", date_label="15 January 2026",
            title="Buying or renting a home in 2026? Key factors to decide",
            excerpt="How long you plan to stay, available savings, interest rates and flexibility: the factors worth analysing before making a decision.",
            body="""
<p class="lead">There is no universal answer. Whether to buy or rent depends on your personal circumstances, your ability to save and how long you expect to live in the property. These are the factors we recommend analysing.</p>
<h2>1. How long you plan to stay</h2>
<p>Buying a home involves significant upfront costs —taxes, notary and land registry fees and, where applicable, administrative agent and valuation fees— which are only recovered over time. As a general rule, the longer you expect to live in the property, the more sense buying makes.</p>
<h2>2. Available savings</h2>
<p>Spanish lenders usually finance up to 80% of the appraised value or the purchase price, whichever is lower. In addition to the deposit, you therefore need savings to cover the costs and taxes of the purchase, which in practice represent a significant share of the price.</p>
<h2>3. The cost of financing</h2>
<p>Compare not only the interest rate but also the <strong>APR (TAE)</strong>, which includes fees and charges. Consider too whether a fixed-rate loan, which offers stable repayments, or a variable or mixed-rate loan, whose repayments follow the Euribor, suits you better.</p>
<h2>4. Flexibility</h2>
<p>Renting offers greater mobility in the event of changes in work or family circumstances and avoids tying up savings. Buying, on the other hand, allows you to build wealth and fix your housing costs over the long term.</p>
<h2>5. A real cost comparison</h2>
<p>To compare both options rigorously, add property tax (IBI), homeowners’ association fees, insurance and maintenance to the mortgage repayment, and compare the total with the rent for an equivalent property. Also consider the return you could earn on the savings you would not use for the deposit.</p>
<h2>Our recommendation</h2>
<p>Before deciding, draw up a realistic budget and request a financing simulation. At Twins Real Estate we help you analyse your specific case and compare scenarios using local market data.</p>
"""),
        "senales-revalorizacion-zona": dict(
            slug="signs-area-value-growth", category="Investment", date_label="12 January 2026",
            title="Five signs that an area is set to increase in value",
            excerpt="Learn to identify the indicators that often anticipate rising property values in a neighbourhood.",
            body="""
<p class="lead">Anticipating how an area will evolve is one of the keys to a sound property investment. Although no indicator is infallible, there are signs which, taken together, often precede an increase in value.</p>
<h2>1. New transport infrastructure</h2>
<p>A new metro or railway station, or new bus routes, improves accessibility and usually has a direct impact on demand and prices.</p>
<h2>2. Urban planning and public projects</h2>
<p>Check the local urban plan: new green spaces, public facilities, redevelopment schemes or changes in land use are relevant indicators of a neighbourhood’s future.</p>
<h2>3. New shops and services</h2>
<p>The opening of restaurants, local shops, schools or health centres tends to reflect —and reinforce— interest in the area.</p>
<h2>4. Building refurbishment</h2>
<p>A growing number of renovated façades, new-build developments or full refurbishments shows that owners and developers are confident about the area’s prospects.</p>
<h2>5. Sustained rental demand and limited supply</h2>
<p>When rental properties are let quickly and available supply is scarce, the pressure of demand tends to carry over into sale prices as well.</p>
<h2>A word of caution</h2>
<p>Past growth in value is no guarantee of future growth. We recommend combining these signs with a yield analysis and your own investment horizon. Our team can prepare a study of any area that interests you.</p>
"""),
        "guia-primera-vivienda": dict(
            slug="first-home-buying-guide", category="Guides", date_label="8 January 2026",
            title="A guide to buying your first home",
            excerpt="From budget to signing before a notary: the steps, documents and checks you should not overlook.",
            body="""
<p class="lead">Buying a home for the first time involves many decisions and formalities. This guide summarises, step by step, the usual process in Spain.</p>
<h2>1. Set your budget</h2>
<p>Work out how much you can put towards the deposit, the purchase costs and the monthly repayment. As a prudent guideline, the mortgage repayment should not exceed roughly one third of the household’s net income.</p>
<h2>2. Look into financing before you search</h2>
<p>Requesting a preliminary assessment from several lenders will tell you how much they could lend you and allow you to negotiate with greater confidence. Always compare the APR (TAE) and any products you are required to take out.</p>
<h2>3. Search and view with care</h2>
<p>In addition to the condition of the property, consider its orientation, surroundings, nearby services, the state of the building and any special levies approved by the homeowners’ association.</p>
<h2>4. Check the documentation</h2>
<ul>
<li><strong>Land registry extract (nota simple)</strong>: ownership and charges.</li>
<li>Latest <strong>property tax (IBI)</strong> receipt.</li>
<li><strong>Homeowners’ association certificate</strong> confirming that payments are up to date.</li>
<li><strong>Energy performance certificate</strong>, mandatory for any sale.</li>
<li><strong>Certificate of occupancy</strong> or equivalent document, depending on the region.</li>
</ul>
<h2>5. Sign a deposit contract</h2>
<p>Once the price has been agreed, the usual practice is to sign a deposit contract (<em>contrato de arras</em>) and pay a deposit. Review the type of deposit, deadlines and conditions carefully, especially if the purchase depends on obtaining financing.</p>
<h2>6. Public deed and registration</h2>
<p>The sale is completed before a notary, who verifies the status of the property and the identity of the parties. You must then pay the applicable taxes and register the deed with the Land Registry.</p>
<h2>We are with you throughout the process</h2>
<p>At Twins Real Estate we review the documentation, coordinate the negotiation and support you until the keys are handed over.</p>
"""),
        "preparar-vivienda-alquiler": dict(
            slug="prepare-home-for-rent", category="Lettings", date_label="2 January 2026",
            title="How to prepare your home to let it faster",
            excerpt="Small improvements, good presentation and a realistic price make all the difference in attracting good tenants.",
            body="""
<p class="lead">A well-prepared home lets faster and attracts more solvent tenants. These are the aspects we recommend taking care of before advertising it.</p>
<h2>1. Get it ready</h2>
<p>Check the installations, taps, blinds and appliances. A coat of paint in neutral tones and the repair of minor defects make a noticeably better first impression.</p>
<h2>2. Mandatory documentation</h2>
<p>An <strong>energy performance certificate</strong> is mandatory to advertise and let a home. Depending on the region, a certificate of occupancy may also be required. Remember, too, that the tenant’s deposit must be lodged with the competent regional authority.</p>
<h2>3. Presentation and photography</h2>
<p>Professional photographs, with good light and tidy spaces, are the first filter for prospective tenants. A clear, complete listing reduces unnecessary viewings.</p>
<h2>4. A market-based price</h2>
<p>A price above the market rate prolongs the vacancy period, which has a real cost. Also check whether the property is located in a designated stressed residential market area, as rent limits may apply.</p>
<h2>5. Choosing the tenant</h2>
<p>Check the applicants’ solvency and consider taking out rent guarantee insurance. A well-drafted agreement, in line with the Spanish Urban Leases Act, protects both parties.</p>
<h2>Leave the management to professionals</h2>
<p>Our lettings service includes valuation, marketing, tenant selection and formalisation of the agreement.</p>
"""),
        "que-revisar-contrato-arras": dict(
            slug="deposit-contract-checklist", category="Legal", date_label="28 December 2025",
            title="What to check before signing a deposit contract",
            excerpt="The essential points to verify before committing to the purchase or sale of a property in Spain.",
            body="""
<p class="lead">The deposit contract (<em>contrato de arras</em>) is the document in which buyer and seller commit to completing the sale. Before signing it, the following aspects should be reviewed in detail.</p>
<h2>1. The type of deposit</h2>
<p>The most common are <strong>penitential deposits</strong> (<em>arras penitenciales</em>, Article 1454 of the Spanish Civil Code): if the buyer withdraws, they forfeit the deposit paid; if the seller withdraws, they must return double the amount. There are also confirmatory and penalty deposits, with different effects. The contract must state the type expressly.</p>
<h2>2. Identification of the parties and the property</h2>
<p>Check that the owners’ details match the land registry extract and that the property is identified by its registry and cadastral references, including annexes such as parking spaces or storage rooms.</p>
<h2>3. Price, deposit and method of payment</h2>
<p>The contract must set out the total price, the amount paid as a deposit and how the balance will be paid when the deed is signed.</p>
<h2>4. Charges and status of the property</h2>
<p>Record whether the property will be transferred free of charges, tenants and occupants, and with taxes and homeowners’ association fees paid up to date.</p>
<h2>5. Deadline for the deed</h2>
<p>Set a deadline for signing before the notary and what happens if it is not met. If the purchase depends on a mortgage, consider including a condition relating to its approval.</p>
<h2>6. Allocation of costs and taxes</h2>
<p>Specify who bears each cost. As a general rule, the municipal capital gains tax (<em>plusvalía</em>) is payable by the seller, while property transfer tax or, for new builds, VAT and stamp duty are payable by the buyer.</p>
<h2>Professional review</h2>
<p>We recommend having the contract reviewed by a professional before signing. At Twins Real Estate we prepare and review the deposit contracts for the transactions we broker.</p>
"""),
        "tendencias-interiorismo-2026": dict(
            slug="interior-design-trends-2026", category="Design", date_label="20 December 2025",
            title="Interior design trends for 2026",
            excerpt="Natural materials, flexible spaces and energy efficiency: the keys that define this year’s homes.",
            body="""
<p class="lead">Interior design in 2026 favours warm, versatile and sustainable homes. These are the trends we see most often in the most sought-after properties.</p>
<h2>1. Natural materials</h2>
<p>Wood, stone, linen and handmade ceramics bring warmth and durability. Honest finishes and textures that age well are in demand.</p>
<h2>2. Flexible spaces</h2>
<p>The rise of remote working has made a home workspace a requirement. Spaces that can be adapted to different times of the day are highly valued.</p>
<h2>3. Warm, calm palettes</h2>
<p>Sand, terracotta, olive green and off-white tones are replacing cold greys, creating more welcoming interiors.</p>
<h2>4. Energy efficiency</h2>
<p>Insulation, efficient windows, aerothermal heat pumps and LED lighting not only reduce consumption: they improve the energy rating and, with it, the property’s appeal on the market.</p>
<h2>5. Layered lighting</h2>
<p>Combining general, task and ambient lighting allows each room to adapt to different uses and enhances the architecture of the space.</p>
<h2>Added value when selling</h2>
<p>Careful presentation can speed up the sale or letting of a property. If you are thinking of selling, we can advise you on the improvements that offer the best balance between cost and impact.</p>
"""),
        "mitos-hipoteca": dict(
            slug="mortgage-myths", category="Financing", date_label="14 December 2025",
            title="Mortgages: five myths worth dispelling",
            excerpt="We clarify some of the most widespread —and not always accurate— ideas about home financing in Spain.",
            body="""
<p class="lead">For most families, a mortgage is the most important financial commitment of their lives. These are some common myths that deserve a closer look.</p>
<h2>Myth 1: “Only the interest rate matters”</h2>
<p>The interest rate is relevant but not sufficient. The <strong>APR (TAE)</strong> includes fees and other costs, and is the right benchmark for comparing offers. Also consider the cost of any linked products each lender requires.</p>
<h2>Myth 2: “I will always need a 20% deposit”</h2>
<p>Lenders usually finance up to 80% of the property’s value. However, there are public schemes, such as the ICO guarantee line for young people and families with dependent children, which allow higher financing if certain requirements are met.</p>
<h2>Myth 3: “Once signed, I cannot change it”</h2>
<p>You can negotiate a novation with your lender or transfer the loan to another lender through a subrogation. It is worth analysing the costs and savings of each option.</p>
<h2>Myth 4: “Early repayment is heavily penalised”</h2>
<p>Spanish Law 5/2019 on real estate credit agreements caps early repayment fees. Check your contract to find out the terms that apply to you.</p>
<h2>Myth 5: “The self-employed cannot get a mortgage”</h2>
<p>Self-employed workers can obtain financing. They are normally required to prove stable income through their income tax and VAT returns for recent years.</p>
<h2>Get advice before you sign</h2>
<p>We guide you in your search for financing and put you in touch with trusted professionals so that you obtain the best terms.</p>
"""),
    },

    "contacto": {
        "title": "Contact",
        "description": "Contact Twins Real Estate to buy, sell or rent a property. Personal service by appointment, in person or by video call.",
        "h1": "Contact",
        "text": "We will be pleased to assist you. Tell us about your situation and an adviser will contact you as soon as possible.",
        "section_aria": "Contact details and form",
        "email_title": "Email",
        "instagram_title": "Instagram",
        "hours_title": "Opening hours",
        "meetings_title": "Meetings and viewings",
        "meetings_text": "By appointment, in person or by video call.",
        "form_title": "Send us your enquiry",
        "form_lead": "Fields marked with * are required.",
        "labels": {
            "nombre": "Full name *",
            "email": "Email *",
            "telefono": "Phone",
            "asunto": "Reason for your enquiry",
            "referencia": "Property reference",
            "mensaje": "Message *",
        },
        "ref_placeholder": "For example, TRE-001",
        "ref_hint": "Optional. Shown on each property listing.",
        "honeypot": "Do not fill in this field",
        "privacy_html": 'I have read and accept the <a href="%%PRIVACY%%">privacy policy</a>. *',
        "subject_placeholder": "Select an option",
        "subjects": ["Buying a property", "Selling a property", "Renting a property", "Rental management",
                     "Property valuation", "Investment advice", "Booking a meeting", "Other enquiry"],
        "legal_html": '<strong>Basic data protection information.</strong> Controller: Twins Real Estate. Purpose: to handle your enquiry and, where applicable, send you the information requested. Legal basis: your consent. Recipients: your data will not be disclosed to third parties unless required by law. Rights: access, rectification, erasure, objection, restriction of processing and portability, as detailed in the <a href="%%PRIVACY%%">privacy policy</a>.',
        "submit": "Send enquiry",
    },

    "owner": {
        "pending": "[to be completed]",
        "rows": [
            ("Owner", "pending", "(full name or company name)"),
            ("Trading name", "Twins Real Estate", ""),
            ("Tax ID (NIF)", "pending", ""),
            ("Registered address", "pending", ""),
            ("Email", "email", ""),
            ("Registration details", "pending", "(Companies Register, if a company)"),
            ("Real estate agents register", "pending", "(registration number, where required by regional law)"),
        ],
    },

    "legal": {
        "aviso-legal.html": dict(
            title="Legal notice",
            description="Legal notice for the Twins Real Estate website: owner identification details and terms of use.",
            body="""
<h2>1. Identification details</h2>
<p>In compliance with Article 10 of Spanish Law 34/2002 of 11 July on information society services and electronic commerce (LSSI-CE), the following details of the owner of this website are provided:</p>
%%OWNER%%
<h2>2. Purpose and acceptance</h2>
<p>This legal notice governs access to and use of this website, whose purpose is to provide information about the real estate brokerage and advisory services of Twins Real Estate. Accessing the website implies acceptance of these terms.</p>
<h2>3. Terms of use</h2>
<p>Users undertake to make appropriate use of the website and its content, in accordance with the law, good faith and public order, and not to use them for unlawful activities or activities that could harm the rights of third parties or the operation of the website.</p>
<h2>4. Property information</h2>
<p>The information published about properties (price, floor area, features and images) is for guidance only and does not constitute a contractual offer. It may contain errors, be subject to change or the property may be withdrawn without notice. Unless otherwise stated, prices do not include taxes or transaction costs.</p>
<p>In accordance with consumer protection regulations on the sale and rental of homes, the information legally required for each property is available to interested parties and may be requested through the contact details provided.</p>
<h2>5. Intellectual and industrial property</h2>
<p>The content of this website —texts, design, logos, trademarks and images— belongs to Twins Real Estate or to third parties who have authorised its use. Reproduction, distribution or modification without express authorisation is prohibited.</p>
<h2>6. Liability</h2>
<p>Twins Real Estate accepts no liability for damage arising from service interruptions, technical errors beyond its control or improper use of the website by users. Nor does it accept liability for the content of third-party websites to which it may link.</p>
<h2>7. Data protection</h2>
<p>The processing of personal data is governed by the <a href="%%PRIVACY%%">privacy policy</a>, and the use of storage technologies by the <a href="%%COOKIES%%">cookie policy</a>.</p>
<h2>8. Language</h2>
<p>This website is available in Spanish, Catalan and English. In the event of any discrepancy between versions, the Spanish version shall prevail.</p>
<h2>9. Governing law and jurisdiction</h2>
<p>These terms are governed by Spanish law. Any dispute shall be submitted to the courts and tribunals with jurisdiction under the applicable regulations, in particular those on the protection of consumers and users.</p>
"""),
        "privacidad.html": dict(
            title="Privacy policy",
            description="Twins Real Estate privacy policy: how we process your personal data in accordance with the GDPR and Spanish data protection law.",
            body="""
<p>Twins Real Estate is committed to protecting your privacy and processing your personal data in accordance with Regulation (EU) 2016/679, the General Data Protection Regulation (GDPR), and Spanish Organic Law 3/2018 on the Protection of Personal Data and Guarantee of Digital Rights (LOPDGDD).</p>
<h2>1. Data controller</h2>
%%OWNER%%
<h2>2. Data we process</h2>
<p>We process the data you provide through the contact form, by email or via our social media channels: your full name, contact details, the content of your enquiry and, where applicable, the information required to provide our services.</p>
<h2>3. Purposes and legal basis</h2>
<ul>
<li><strong>Handling your enquiries</strong> and sending you the information requested. Legal basis: your consent (Art. 6(1)(a) GDPR).</li>
<li><strong>Managing the pre-contractual and contractual relationship</strong> arising from our real estate brokerage and advisory services. Legal basis: performance of a contract or pre-contractual measures (Art. 6(1)(b) GDPR).</li>
<li><strong>Complying with applicable legal obligations</strong>, including those arising from Spanish Law 10/2010 on the prevention of money laundering and terrorist financing, and from tax regulations. Legal basis: legal obligation (Art. 6(1)(c) GDPR).</li>
</ul>
<p>No automated decisions are made and no profiles are created using your data.</p>
<h2>4. Retention period</h2>
<p>Enquiry data will be kept for as long as necessary to handle the enquiry and, at most, for one year if no contractual relationship begins. Data linked to a contract will be kept for the duration of the relationship and thereafter for the applicable statutory limitation periods.</p>
<h2>5. Recipients</h2>
<p>We do not disclose your data to third parties unless required by law. Providers of email and web hosting services may access it as data processors, with the safeguards required by the GDPR. Where any of these providers is located outside the European Economic Area, the transfer is based on a European Commission adequacy decision, such as the EU-US Data Privacy Framework, or on standard contractual clauses.</p>
<h2>6. Your rights</h2>
<p>You may exercise your rights of access, rectification, erasure, objection, restriction of processing and portability, and withdraw your consent at any time, by writing to <a href="mailto:%%EMAIL%%">%%EMAIL%%</a> and stating the right you wish to exercise.</p>
<p>If you consider that the processing of your data does not comply with the regulations, you may lodge a complaint with the Spanish Data Protection Agency (<a href="https://www.aepd.es" target="_blank" rel="noopener noreferrer">www.aepd.es</a>).</p>
<h2>7. Security</h2>
<p>We apply appropriate technical and organisational measures to ensure the confidentiality, integrity and availability of your data, including encryption of the website’s communications via HTTPS.</p>
<h2>8. Minors</h2>
<p>This website is not intended for children under 14, and we do not knowingly process their personal data.</p>
<h2>9. Changes to this policy</h2>
<p>We may update this policy to reflect regulatory changes or changes to our services. The date of the last update is shown at the top of this page.</p>
"""),
        "cookies.html": dict(
            title="Cookie policy",
            description="Twins Real Estate cookie policy: information about the storage technologies used on this website.",
            body="""
<h2>1. Do we use cookies?</h2>
<p>This website <strong>does not use</strong> first-party or third-party <strong>cookies</strong> for analytics, advertising or tracking purposes. For this reason, no cookie consent banner is displayed.</p>
<h2>2. Local storage</h2>
<p>If you mark a property as a favourite, your browser stores only the reference of that property using local storage technology (<em>localStorage</em>). This information contains no personal data, is not sent to any server and remains exclusively on your device. Likewise, if you change the website’s visual theme (dark or cream), only that preference is stored.</p>
<p>This is technical storage necessary to provide a feature you have expressly requested, and is therefore exempt from the consent requirement under Article 22.2 of the LSSI-CE. You can delete it at any time from your browser settings.</p>
<div class="table-scroll">
<table>
<thead>
<tr><th scope="col">Name</th><th scope="col">Type</th><th scope="col">Purpose</th><th scope="col">Duration</th></tr>
</thead>
<tbody>
<tr><td>twins:favoritos</td><td>Local storage (first-party)</td><td>Remembering properties marked as favourites</td><td>Until deleted by the user</td></tr>
<tr><td>twins:tema</td><td>Local storage (first-party)</td><td>Remembering the chosen theme (dark or cream)</td><td>Until deleted by the user</td></tr>
</tbody>
</table>
</div>
<h2>3. Third-party resources</h2>
<p>To display the website’s typefaces, your browser downloads files from the Google Fonts service, provided by Google. This service does not set cookies, although, as with any internet connection, it receives the IP address of the device making the request. You can read Google’s privacy policy at <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">policies.google.com/privacy</a>.</p>
<p>Links to Instagram only take you to that social network when you click on them; this website does not embed any social media content or plug-ins.</p>
<h2>4. Changes to this policy</h2>
<p>If we introduce cookies that require your consent in the future, we will update this policy and enable the corresponding consent mechanism before they are set.</p>
"""),
    },

    "error404": {
        "title": "Page not found",
        "description": "The page you are looking for does not exist or has moved.",
        "h1": "Page not found",
        "text": "The page you are looking for does not exist or has moved. Please return to the home page or browse our property portfolio.",
        "home": "Back to home",
        "props": "View properties",
    },
}
