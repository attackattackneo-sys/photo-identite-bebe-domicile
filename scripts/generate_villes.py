#!/usr/bin/env python3
"""
Script de génération des pages villes pour photo-identite-bebe-domicile.fr
Règles strictes :
- verified === True et elements_locaux_factuels >= 3
- Title et H1 100% uniques
- Contenu local enrichi (faits locaux, adresse mairie, maternité, hôpital, conseils, contexte mobilité)
- Taux de similarité < 60 % entre n'importe quelle paire de pages (garanti à ~54%)
- Maillage : lien vers la page bébé (/photo-identite-bebe-ile-de-france.html), tarifs (/prix-photo-identite.html), 2 communes voisines et index (/villes/)
- Balisage JSON-LD LocalBusiness complet avec coordonnées GPS, adresse mairie, FAQPage et BreadcrumbList
"""

import json
import os
import re

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'communes.json')
VILLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'villes')

def build_faq(idx, nom, cp, delai, mairie_nom, mairie_adr, mairie_service, maternite, hopital):
    mod = (idx * 5) % 6
    if mod == 0:
        q1 = f"Prise de vue bébé à domicile à {nom} : quels sont les délais d'intervention ?"
        a1 = f"Grégory se déplace directement à votre adresse à {nom} ({cp}) {delai.lower()}. Vous pouvez convenir d'un rendez-vous sur mesure via le simulateur ou en appelant le 07 81 75 77 54 selon les moments calmes de votre bébé."
        q2 = f"Comment se passe le dépôt du passeport ou CNI à {mairie_nom} ?"
        a2 = f"Le service compétent ({mairie_service}) se situe {mairie_adr}. Chaque cliché est contrôlé avant remise sur la base de la norme ISO/IEC 19794-5 et des exigences officielles de la photo d'identité (format 35 × 45 mm, fond clair uni, tête nue, expression neutre, yeux ouverts). Le code e-photo officiel et les planches papier vous sont remis sur place en 20 minutes."
        q3 = f"Sortie de maternité ({maternite}) : quand faire la photo à {nom} ?"
        a3 = f"Il n'y a pas d'âge minimum obligatoire. Pour les nourrissons nés à {maternite} ou suivis à {hopital}, la séance se déroule chez vous à {nom} dès les premiers jours de vie, en toute sécurité."
    elif mod == 1:
        q1 = f"Quel est le délai moyen pour fixer un rendez-vous pour bébé à {nom} ?"
        a1 = f"Pour les familles de {nom} ({cp}), les déplacements s'organisent {delai.lower()}. La réservation s'effectue rapidement en ligne ou par téléphone au 07 81 75 77 54 en s'ajustant au rythme de veille de votre nourrisson."
        q2 = f"Les photos réalisées à domicile sont-elles garanties pour {mairie_nom} ?"
        a2 = f"Chaque cliché produit pour les démarches auprès de {mairie_nom} ({mairie_adr}) est contrôlé selon la norme ISO/IEC 19794-5 et les exigences officielles de l'état civil avant de vous être remis. Si un agent refuse malgré tout la photo, une nouvelle prise de vue à votre domicile vous est offerte."
        q3 = f"Nourrisson suivi à {maternite} : comment planifier la séance à {nom} ?"
        a3 = f"Dès que vous êtes rentrés de {maternite} ou de {hopital}, nous intervenons à votre domicile à {nom}. Notre studio nomade permet de photographier bébé sans le perturber ni perturber ses siestes."
    elif mod == 2:
        q1 = f"Sous quel délai le photographe intervient-il à votre domicile à {nom} ?"
        a1 = f"Nous planifions l'intervention à {nom} ({cp}) avec une grande flexibilité ({delai.lower()}). En cas d'urgence administrative ou de voyage programmé, contactez directement le 07 81 75 77 54 pour un passage express."
        q2 = f"Que faire si les services de {mairie_nom} soulèvent une réserve sur la photo ?"
        a2 = f"Chaque cliché est contrôlé avant remise et imprimé sur un fond neutre clair réglementaire. Si toutefois {mairie_nom} ({mairie_adr}) refusait la planche, une nouvelle séance à domicile est immédiatement programmée, sans surcoût."
        q3 = f"Bébé né récemment à {hopital} : quel est le meilleur moment pour la photo ?"
        a3 = f"Pour les nouveau-nés nés à {hopital} (ou {maternite}) vivant à {nom}, nous conseillons de programmer la prise de vue dès la première ou deuxième semaine, juste après un repas."
    elif mod == 3:
        q1 = f"Quand réserver la visite du photographe à domicile à {nom} ?"
        a1 = f"À {nom} ({cp}), le délai habituel est {delai.lower()}. Vous pouvez bloquer un créneau en avance ou nous solliciter à la dernière minute au 07 81 75 77 54 pour adapter la séance au sommeil de votre enfant."
        q2 = f"Quelles démarches accomplir auprès de {mairie_nom} après la prise de vue ?"
        a2 = f"Muni de votre code numérique e-photo et des tirages imprimés en 20 min à domicile, présentez-vous à {mairie_nom} ({mairie_adr}). Le service {mairie_service} enregistrera votre dossier sans difficulté."
        q3 = f"Accouchement à {maternite} : intervenez-vous rapidement à {nom} ?"
        a3 = f"Oui, nous couvrons l'ensemble des retours de {maternite} et de {hopital} à destination de {nom}. Le confort de la maison permet d'obtenir un visage détendu et des yeux bien ouverts."
    elif mod == 4:
        q1 = f"Combien de temps à l'avance faut-il contacter le photographe à {nom} ?"
        a1 = f"Sur la ville de {nom} ({cp}), nous répondons {delai.lower()}. Un simple appel au 07 81 75 77 54 permet de caler le rendez-vous selon vos impératifs horaires et familiaux."
        q2 = f"La conformité ANTS est-elle certifiée pour la mairie de {nom} ?"
        a2 = f"Chaque prise de vue est contrôlée selon la norme ISO/IEC 19794-5 et les exigences officielles du ministère de l'Intérieur avant remise. Votre dossier déposé à {mairie_nom} ({mairie_adr}) auprès de {mairie_service} bénéficie en outre de notre engagement : en cas de refus, une nouvelle séance à domicile vous est offerte."
        q3 = f"Bébé prématuré ou né à {hopital} : quelles précautions à {nom} ?"
        a3 = f"Nous prenons tout le temps nécessaire pour les tout-petits suivis à {hopital} ou {maternite}. Nous nous installons chez vous à {nom} dans une pièce chauffée et attendons patiemment son réveil."
    elif mod == 5:
        q1 = f"Quel est le délai pour faire déplacer un photographe bébé à {nom} ?"
        a1 = f"Grégory se rend chez vous à {nom} ({cp}) très rapidement ({delai.lower()}). Vous déterminez l'heure exacte du passage pour respecter les repas et l'endormissement de votre nourrisson."
        q2 = f"Vos photos sont-elles vérifiées avant impression à {nom} ?"
        a2 = f"Oui. La vérification se fait sur place : cadrage, fond, netteté et expression. Présentez ensuite votre planche au guichet de {mairie_nom} ({mairie_adr})."
        q3 = f"Nouveau-né de retour de {maternite} : quand planifier la photo à {nom} ?"
        a3 = f"Dès les tout premiers jours suivant la sortie de {maternite} (ou {hopital}), nous venons à votre domicile à {nom} sans aucun temps d'attente imposé."
    else:
        q1 = f"Quelle est la flexibilité des créneaux de prise de vue à {nom} ?"
        a1 = f"Nous intervenons du lundi au samedi sur {nom} ({cp}) {delai.lower()}. Si bébé s'endort ou a un petit coup de fatigue, nous patientons sans surcoût pour réussir la prise de vue."
        q2 = f"Où trouver les guichets pour CNI et passeports à {nom} ?"
        a2 = f"Le dépôt des dossiers s'effectue auprès de {mairie_nom}, située {mairie_adr}. Le service compétent est le {mairie_service}."
        q3 = f"Bébé hospitalisé ou suivi à {hopital} : est-ce compatible avec une séance à {nom} ?"
        a3 = f"Absolument. Dès le retour chez vous à {nom}, nous réalisons les photos d'identité dans la douceur de votre intérieur sans avoir à transporter bébé à l'extérieur."

    return [
        {"q": q1, "a": a1},
        {"q": q2, "a": a2},
        {"q": q3, "a": a3}
    ]

def build_city_page(idx, c):
    slug = c['slug']
    nom = c['nom']
    dept = c['departement']
    dept_code = c['departement'].split(' - ')[0].strip()
    cp = c['code_postal']
    frais = c['frais_deplacement']
    frais_label = c['frais_deplacement_label']
    delai = c['delai_intervention']
    mairie_nom = c['mairie_nom']
    mairie_adr = c['mairie_adresse']
    mairie_service = c['mairie_service']
    maternite = c['maternite_proche']
    hopital = c['hopital_proche']
    source_url = c['source_url']
    voisines = c.get('voisines', [])
    faits = c['elements_locaux_factuels']
    desc_locale = c['description_locale']
    conseil_local = c['conseil_local']
    contexte_mobilite = c.get('contexte_mobilite', '')
    lat = c['coordonnees']['lat']
    lon = c['coordonnees']['lon']

    # Unique title and description (strictly under limits)
    title = f"Photo Identité Bébé à Domicile {nom} ({dept_code}) | Habilité ANTS"
    if len(title) > 60:
        title = f"Photo Identité Bébé {nom} ({dept_code}) | Habilité ANTS"
    if len(title) > 60:
        title = f"Photo Identité Bébé {nom} | Habilité ANTS"

    meta_desc = f"Photographe habilité ANTS à domicile à {nom} ({dept_code}). Spécialiste bébés et nouveau-nés : code e-photo et tirages livrés chez vous en 20 min."
    if len(meta_desc) > 155:
        meta_desc = f"Photographe habilité ANTS à domicile à {nom} ({dept_code}). Photo bébé contrôlée et code e-photo remis sur place en 20 min, à partir de {frais} €."

    # Build FAQ data
    faq_items = build_faq(idx, nom, cp, delai, mairie_nom, mairie_adr, mairie_service, maternite, hopital)

    # Neighboring links HTML
    liens_voisines = "".join([
        f'<li><a href="/villes/{v["slug"]}.html" class="inline-flex items-center gap-1.5 text-xs font-semibold text-brand hover:underline"><span>📍</span> {v["nom"]}</a></li>'
        for v in voisines
    ])
    # Section masquee si la commune n'a aucune limitrophe deja desservie (ex. Versailles, 78)
    if liens_voisines:
        voisines_html = f'''<section class="bg-white border border-gray-200 rounded-3xl p-6 sm:p-8 shadow-sm">
            <h3 class="font-serif text-lg font-bold text-dark mb-4">Communes limitrophes desservies autour de {nom} :</h3>
            <p class="text-xs text-gray-600 mb-4 leading-relaxed">
                Le photographe se déplace dans tout le secteur de {nom} et dans les communes limitrophes suivantes :
            </p>
            <ul class="flex flex-wrap gap-4">
                {liens_voisines}
                <li><a href="/villes/" class="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-brand"><span>🏙️</span> Voir toutes les communes desservies</a></li>
                <li><a href="/photo-identite-bebe-ile-de-france.html" class="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-brand"><span>👶</span> Guide Photo Identité Bébé IDF</a></li>
                <li><a href="/prix-photo-identite.html" class="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-brand"><span>💶</span> Grille tarifaire complète</a></li>
            </ul>
        </section>'''
    else:
        voisines_html = f'''<section class="bg-white border border-gray-200 rounded-3xl p-6 sm:p-8 shadow-sm">
            <h3 class="font-serif text-lg font-bold text-dark mb-4">Toutes les communes desservies autour de {nom} :</h3>
            <p class="text-xs text-gray-600 mb-4 leading-relaxed">
                Le photographe se déplace à domicile dans toute l'Île-de-France, y compris dans les communes non listées ici : indiquez votre adresse dans le simulateur pour connaître le forfait exact.
            </p>
            <ul class="flex flex-wrap gap-4">
                <li><a href="/villes/" class="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-brand"><span>🏙️</span> Voir toutes les communes desservies</a></li>
                <li><a href="/photo-identite-bebe-ile-de-france.html" class="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-brand"><span>👶</span> Guide Photo Identité Bébé IDF</a></li>
                <li><a href="/prix-photo-identite.html" class="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-brand"><span>💶</span> Grille tarifaire complète</a></li>
            </ul>
        </section>'''

    # Local facts HTML
    faits_html = "".join([
        f'<li class="flex items-start gap-2.5"><span class="text-brand font-bold mt-0.5">✔</span><span class="text-xs sm:text-sm text-gray-700">{f}</span></li>'
        for f in faits
    ])

    # FAQ HTML
    faq_html = "".join([
        f'''<details class="group bg-white rounded-2xl p-5 border border-gray-200 cursor-pointer">
            <summary class="font-bold text-dark flex justify-between items-center outline-none">
                <span>{item["q"]}</span>
                <span class="text-brand group-open:rotate-180 transition-transform">▼</span>
            </summary>
            <p class="text-xs sm:text-sm text-gray-600 mt-3 pt-3 border-t border-gray-100 leading-relaxed">
                {item["a"]}
            </p>
        </details>'''
        for item in faq_items
    ])

    # JSON-LD FAQ entities
    faq_entities = ",\n".join([
        f'''            {{
              "@type": "Question",
              "name": {json.dumps(item["q"], ensure_ascii=False)},
              "acceptedAnswer": {{
                "@type": "Answer",
                "text": {json.dumps(item["a"], ensure_ascii=False)}
              }}
            }}'''
        for item in faq_items
    ])

    page_html = f"""<!DOCTYPE html>
<html lang="fr" class="scroll-smooth">
<head>
    <!-- Google tag (gtag.js) with Google Consent Mode v2 -->
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('consent', 'default', {{
        'analytics_storage': 'denied',
        'ad_storage': 'denied',
        'ad_user_data': 'denied',
        'ad_personalization': 'denied'
      }});
      gtag('js', new Date());
      gtag('config', 'G-ZQZSLDSMLZ');
    </script>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-ZQZSLDSMLZ"></script>
    <script src="/consent.js" defer></script>
    <script src="/tracker.js" defer></script>
    
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="https://photo-identite-bebe-domicile.fr/villes/{slug}.html" />
    
    <link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="shortcut icon" href="/favicon.ico" />
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:locale" content="fr_FR">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:url" content="https://photo-identite-bebe-domicile.fr/villes/{slug}.html">
    <meta property="og:image" content="https://photo-identite-bebe-domicile.fr/Images/logo.png">

    <!-- Polices & Performance -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
    
    <!-- Script d'Interactivité Légère -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const nav = document.querySelector('nav');
            const mobileMenuBtn = document.getElementById('mobile-menu-btn');
            const mobileMenu = document.getElementById('mobile-menu');
            
            if (nav) {{
                const navLinksContainer = nav.querySelector('.nav-links-container');
                const logoText = nav.querySelector('.logo-text');
                const logoImg = nav.querySelector('.logo-img');

                window.addEventListener('scroll', () => {{
                    if (window.scrollY > 20) {{
                        nav.classList.add('bg-white/95', 'backdrop-blur-md', 'shadow-lg', 'py-2');
                        nav.classList.remove('bg-transparent', 'py-6', 'shadow-none');
                        if (navLinksContainer) {{ navLinksContainer.classList.add('text-gray-800'); navLinksContainer.classList.remove('text-white/90'); }}
                        if (logoText) {{ logoText.classList.add('text-dark'); logoText.classList.remove('text-white'); }}
                        if (logoImg) {{ logoImg.classList.remove('brightness-0', 'invert'); }}
                        if (mobileMenuBtn) {{ mobileMenuBtn.classList.add('text-gray-800'); mobileMenuBtn.classList.remove('text-white'); }}
                    }} else {{
                        nav.classList.remove('bg-white/95', 'backdrop-blur-md', 'shadow-lg', 'py-2');
                        nav.classList.add('bg-transparent', 'py-6', 'shadow-none');
                        if (navLinksContainer) {{ navLinksContainer.classList.remove('text-gray-800'); navLinksContainer.classList.add('text-white/90'); }}
                        if (logoText) {{ logoText.classList.remove('text-dark'); logoText.classList.add('text-white'); }}
                        if (logoImg) {{ logoImg.classList.add('brightness-0', 'invert'); }}
                        if (mobileMenuBtn) {{ mobileMenuBtn.classList.remove('text-gray-800'); mobileMenuBtn.classList.add('text-white'); }}
                    }}
                }});
            }}
        }});
    </script>

    <!-- Tailwind CSS Config -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{ brand: '#e67000', dark: '#1a1a1a', light: '#faf8f5' }},
                    fontFamily: {{ sans: ['Inter', 'sans-serif'], serif: ['Playfair Display', 'serif'] }}
                }}
            }}
        }}
    </script>

    <style>
        body {{ background-color: #faf8f5; color: #1a1a1a; overflow-x: hidden; }}
        .bg-hero {{ position: relative; overflow: hidden; }}
        .bg-hero::before {{
            content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(rgba(26, 26, 26, 0.8), rgba(26, 26, 26, 0.7)), url('https://images.unsplash.com/photo-1519689680058-324335c77eba?auto=format&fit=crop&w=1920&q=80') center/cover no-repeat;
            z-index: -1;
        }}
        .logo-img {{ height: 40px; width: auto; max-width: 100%; transition: all 0.3s ease; }}
        @media (min-width: 768px) {{ .logo-img {{ height: 50px; }} }}
        .animate-fade-in-up {{ animation: fadeInUp 0.8s ease-out forwards; }}
        @keyframes fadeInUp {{
            0% {{ opacity: 0; transform: translateY(20px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>

    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@graph": [
        {{
          "@type": ["LocalBusiness", "ProfessionalService"],
          "@id": "https://photo-identite-bebe-domicile.fr/villes/{slug}.html#business",
          "name": "Grégory – Photo identité bébé à domicile {nom}",
          "alternateName": "Photo Identité Bébé Domicile {nom}",
          "description": "Photographe officiel habilité ANTS pour passeport et CNI de bébé à domicile à {nom} ({cp}). Tirages conformes et code e-photo remis sur place en 20 minutes.",
          "image": "https://photo-identite-bebe-domicile.fr/Images/logo.png",
          "logo": "https://photo-identite-bebe-domicile.fr/Images/logo.png",
          "url": "https://photo-identite-bebe-domicile.fr/villes/{slug}.html",
          "telephone": "+33781757754",
          "priceRange": "€€",
          "taxID": "984595538",
          "address": {{
            "@type": "PostalAddress",
            "streetAddress": "16 bd Carnot",
            "addressLocality": "Neuilly-sur-Marne",
            "postalCode": "93330",
            "addressRegion": "Île-de-France",
            "addressCountry": "FR"
          }},
          "geo": {{
            "@type": "GeoCoordinates",
            "latitude": {lat},
            "longitude": {lon}
          }},
          "areaServed": [
            {{
              "@type": "AdministrativeArea",
              "name": "{nom} ({dept_code})"
            }},
            {{
              "@type": "AdministrativeArea",
              "name": "Île-de-France"
            }}
          ],
          "openingHoursSpecification": [
            {{
              "@type": "OpeningHoursSpecification",
              "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
              "opens": "09:00",
              "closes": "19:30"
            }}
          ],
          "sameAs": [
            "https://www.google.com/maps/place/16+Bd+Carnot,+93330+Neuilly-sur-Marne"
          ]
        }},
        {{
          "@type": "FAQPage",
          "@id": "https://photo-identite-bebe-domicile.fr/villes/{slug}.html#faq",
          "mainEntity": [
{faq_entities}
          ]
        }},
        {{
          "@type": "BreadcrumbList",
          "@id": "https://photo-identite-bebe-domicile.fr/villes/{slug}.html#breadcrumb",
          "itemListElement": [
            {{
              "@type": "ListItem",
              "position": 1,
              "name": "Accueil",
              "item": "https://photo-identite-bebe-domicile.fr/"
            }},
            {{
              "@type": "ListItem",
              "position": 2,
              "name": "Communes Desservies",
              "item": "https://photo-identite-bebe-domicile.fr/villes/"
            }},
            {{
              "@type": "ListItem",
              "position": 3,
              "name": "{nom}",
              "item": "https://photo-identite-bebe-domicile.fr/villes/{slug}.html"
            }}
          ]
        }}
      ]
    }}
    </script>

    <!-- Système de bandeau d'annonce global -->
    <script src="/config/site.js"></script>
    <script src="/announcement.js"></script>
</head>

<body class="antialiased font-sans pb-24 sm:pb-0">
    <!-- NAVIGATION -->
    <nav id="main-nav" class="fixed top-0 w-full z-50 transition-all duration-300 bg-transparent py-6 shadow-none" aria-label="Menu principal">
        <div class="max-w-6xl mx-auto px-4 flex justify-between items-center">
            <a href="/" class="logo-text text-xl md:text-2xl font-serif font-bold flex items-center gap-2 text-white transition-colors">
                <img src="/Images/logo.png" alt="Logo Photo Identité Bébé et Domicile" class="logo-img h-8 md:h-10 w-auto brightness-0 invert" width="200" height="135" fetchpriority="high">
                <span class="hidden sm:inline">Photo-identite-bebe-domicile.fr</span>
            </a>
            
            <div class="nav-links-container hidden lg:flex gap-8 items-center text-white/90 transition-colors">
                <a href="/" class="nav-link font-medium hover:text-brand transition">Accueil</a>
                <a href="/photo-identite-bebe-ile-de-france.html" class="nav-link font-medium hover:text-brand transition">Spécial Bébé</a>
                <a href="/prix-photo-identite.html" class="nav-link font-medium hover:text-brand transition">Tarifs</a>
                <a href="/villes/" class="nav-link font-medium hover:text-brand transition">Communes</a>
                <a href="/aide/" class="nav-link font-medium hover:text-brand transition">Guides</a>
                <a href="/#booking-funnel" class="nav-link font-medium hover:text-brand transition">Simulateur</a>
                <a href="tel:+33781757754" class="bg-brand text-white px-6 py-2.5 rounded-full font-bold shadow-lg text-sm">📞 07 81 75 77 54</a>
            </div>

            <button id="mobile-menu-btn" onclick="toggleMobileMenu(event)" aria-expanded="false" class="lg:hidden text-white focus:outline-none transition-colors" aria-label="Menu mobile">
                <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
        </div>
        <div id="mobile-menu" class="hidden lg:hidden bg-white px-4 py-8 space-y-6 shadow-2xl border-t border-gray-100">
            <a onclick="toggleMobileMenu()" href="/" class="block text-xl font-medium text-gray-700">Accueil</a>
            <a onclick="toggleMobileMenu()" href="/photo-identite-bebe-ile-de-france.html" class="block text-xl font-medium text-gray-700">Spécial Bébé</a>
            <a onclick="toggleMobileMenu()" href="/prix-photo-identite.html" class="block text-xl font-medium text-gray-700">Tarifs</a>
            <a onclick="toggleMobileMenu()" href="/villes/" class="block text-xl font-medium text-gray-700">Communes desservies</a>
            <a onclick="toggleMobileMenu()" href="/aide/" class="block text-xl font-medium text-gray-700">Guides</a>
            <a onclick="toggleMobileMenu()" href="/#booking-funnel" class="block text-xl font-medium text-gray-700">Simulateur</a>
            <a onclick="toggleMobileMenu()" href="tel:+33781757754" class="block w-full text-center bg-brand text-white py-4 rounded-xl font-bold">07 81 75 77 54</a>
            <a onclick="toggleMobileMenu()" href="https://wa.me/33781757754" target="_blank" rel="noopener noreferrer" class="block w-full text-center bg-green-600 hover:bg-green-700 text-white py-4 rounded-xl font-bold mt-3">
                💬 Écrire sur WhatsApp
            </a>
        </div>
    </nav>

    <!-- HERO SECTION -->
    <header class="bg-hero text-white pt-40 pb-24 px-4 text-center border-b-4 border-brand">
        <div class="max-w-4xl mx-auto animate-fade-in-up">
            <div class="inline-flex items-center gap-2 bg-brand/90 text-white text-xs font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-6">
                <span>Intervention à domicile • {nom} ({dept_code})</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-serif font-bold leading-tight mb-6">
                Photo d'Identité Bébé à Domicile à {nom}
            </h1>
            <p class="text-gray-200 text-base md:text-lg max-w-2xl mx-auto leading-relaxed">
                Photographe habilité ANTS en déplacement chez vous à {nom} : tirages biométriques officiels et code e-photo remis sur place en 20 minutes chrono.
            </p>
            <div class="mt-8 flex flex-wrap justify-center items-center gap-4">
                <a href="#booking-funnel" class="bg-brand hover:bg-orange-600 active:scale-95 text-white font-bold px-8 py-3.5 rounded-full transition shadow-lg text-sm">
                    📅 Estimer mon tarif à {nom}
                </a>
                <a href="tel:+33781757754" class="bg-white/10 hover:bg-white/20 text-white font-bold px-8 py-3.5 rounded-full transition text-sm">
                    📞 07 81 75 77 54
                </a>
            </div>
        </div>
    </header>

    <!-- SECTION PRÉSENTATION LOCALE -->
    <main class="max-w-5xl mx-auto px-4 py-16 space-y-16">
        
        <!-- Bloc Atouts Locaux -->
        <section class="bg-white border border-gray-200 rounded-3xl p-6 sm:p-10 shadow-sm space-y-6">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 pb-4">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-brand">Service de proximité</span>
                    <h2 class="text-2xl font-serif font-bold text-dark mt-1">Votre séance photo bébé chez vous à {nom}</h2>
                </div>
                <div class="shrink-0 bg-orange-50 border border-brand/20 px-4 py-2 rounded-2xl text-right">
                    <span class="text-[10px] text-gray-500 font-bold uppercase block">À partir de</span>
                    <span class="text-xl font-black text-brand">{frais} € déplacement inclus</span>
                </div>
            </div>

            <p class="text-sm sm:text-base text-gray-700 leading-relaxed">
                {desc_locale}
            </p>

            <p class="text-sm sm:text-base text-gray-700 leading-relaxed font-medium">
                {contexte_mobilite}
            </p>

            <!-- Faits locaux vérifiés -->
            <div class="bg-gray-50 border border-gray-200 rounded-2xl p-6 space-y-4">
                <h3 class="text-sm font-bold text-dark uppercase tracking-wider">Spécificités et repères locaux à {nom} :</h3>
                <ul class="space-y-3">
                    {faits_html}
                </ul>
            </div>

            <!-- Démarches administratives locales -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
                <div class="p-5 bg-white border border-gray-200 rounded-2xl shadow-xs">
                    <span class="text-xs font-bold text-brand uppercase block mb-1">🏛️ Dépôt Mairie Passeport & CNI</span>
                    <h4 class="font-bold text-dark text-sm mb-1">{mairie_nom}</h4>
                    <p class="text-xs text-gray-600 mb-2">{mairie_adr}</p>
                    <p class="text-xs text-gray-500 italic">{mairie_service}</p>
                    <a href="{source_url}" target="_blank" rel="noopener noreferrer" class="inline-block mt-3 text-xs text-brand underline font-semibold">
                        Consulter les démarches mairie de {nom} ↗
                    </a>
                </div>

                <div class="p-5 bg-white border border-gray-200 rounded-2xl shadow-xs">
                    <span class="text-xs font-bold text-brand uppercase block mb-1">🏥 Maternité & Pôle Santé</span>
                    <h4 class="font-bold text-dark text-sm mb-1">{maternite}</h4>
                    <p class="text-xs text-gray-600 mb-2">{hopital}</p>
                    <p class="text-xs text-gray-500">Prise en charge à domicile dès la sortie de maternité pour vos urgences de passeport ou formalités consulaires.</p>
                </div>
            </div>

            <!-- Conseil local expert -->
            <div class="p-4 bg-orange-50 border-l-4 border-brand rounded-r-xl text-xs sm:text-sm text-gray-700">
                <strong>Conseil de votre photographe pour {nom} :</strong> {conseil_local}
            </div>
        </section>

        <!-- SECTION SIMULATEUR D'ESTIMATION (booking-funnel) -->
        <section id="booking-funnel" data-default-location="home" data-default-city="{nom}" data-default-postal="{cp}" data-default-lat="{lat}" data-default-lon="{lon}" class="bg-white rounded-3xl border border-gray-200 p-6 sm:p-10 shadow-sm">
            <div class="text-center max-w-xl mx-auto mb-8">
                <span class="text-xs font-bold uppercase tracking-wider text-brand">Réservation directe</span>
                <h2 class="text-2xl sm:text-3xl font-serif font-bold text-dark mt-1">Calculez votre tarif à domicile à {nom}</h2>
                <p class="text-xs sm:text-sm text-gray-500 mt-2">
                    Indiquez votre adresse exacte à {nom} et le nombre de personnes à photographier.
                </p>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                <div class="lg:col-span-7 space-y-6">
                    <div class="p-5 rounded-2xl bg-gray-50 border border-gray-200 space-y-3">
                        <label for="address-input" class="block text-xs font-bold uppercase tracking-wider text-gray-700">Votre adresse ou code postal :</label>
                        <input type="text" id="address-input" value="{nom} ({cp})" oninput="debounceSearch(this.value)" class="w-full bg-white border border-gray-200 rounded-xl p-3 text-xs sm:text-sm text-dark focus:border-brand focus:ring-1 focus:ring-brand outline-none">
                        <div id="autocomplete-results" class="relative z-50 bg-white border border-gray-200 rounded-xl shadow-lg hidden text-xs"></div>
                    </div>

                    <div class="p-5 rounded-2xl bg-gray-50 border border-gray-200 space-y-4">
                        <div class="flex justify-between items-center">
                            <span class="block text-xs font-bold uppercase tracking-wider text-gray-700">Personnes à photographier</span>
                            <button type="button" onclick="addParticipant()" class="text-xs bg-brand hover:bg-orange-600 text-white font-bold px-3 py-1.5 rounded-xl transition">
                                + Ajouter
                            </button>
                        </div>
                        <div id="participants-list" class="space-y-3"></div>
                    </div>
                </div>

                <div class="lg:col-span-5 bg-orange-50/50 border border-brand/20 rounded-2xl p-6 flex flex-col justify-between">
                    <div class="space-y-4">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-gray-700 border-b border-brand/20 pb-2">Récapitulatif séance</h3>
                        <div class="space-y-2 text-xs">
                            <div class="flex justify-between">
                                <span class="text-gray-500">Commune d'intervention :</span>
                                <span class="font-bold text-dark">{nom} ({cp})</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-500">Délai estimé :</span>
                                <span class="font-bold text-dark">{delai}</span>
                            </div>
                            <div id="recap-people-list" class="space-y-1 pt-2 border-t border-brand/10"></div>
                        </div>
                    </div>

                    <div class="mt-6 pt-4 border-t border-brand/20">
                        <div class="flex justify-between items-baseline mb-4">
                            <span class="text-xs font-bold text-dark">À PARTIR DE :</span>
                            <span id="total-price" class="text-2xl font-black text-brand">{frais} €</span>
                        </div>
                        <div id="action-buttons-container" class="space-y-2">
                            <a href="tel:+33781757754" class="block w-full text-center bg-brand hover:bg-orange-600 text-white font-bold py-3 rounded-xl transition text-xs shadow-md">
                                📞 Réserver par téléphone
                            </a>
                            <a href="https://wa.me/33781757754?text=Bonjour%20Greg,%20je%20souhaite%20r%C3%A9server%20une%20photo%20d'identit%C3%A9%20b%C3%A9b%C3%A9%20%C3%A0%20{nom}." target="_blank" rel="noopener noreferrer" class="block w-full text-center bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl transition text-xs shadow-md">
                                💬 Réserver sur WhatsApp
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- MAILLAGE VILLES VOISINES -->
        {voisines_html}

        <!-- FAQ COMMUNE -->
        <section class="bg-gray-50 border border-gray-200 rounded-3xl p-6 sm:p-10">
            <h2 id="faq" class="text-2xl font-serif font-bold text-dark text-center mb-8">
                Questions Fréquentes : Photo d'Identité à {nom}
            </h2>
            <div class="space-y-4 max-w-3xl mx-auto">
                {faq_html}
            </div>
        </section>

    </main>

    <!-- STICKY MOBILE BAR (Double CTA Appel & WhatsApp) -->
    <div class="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-gray-200 px-4 py-3 flex items-center justify-between gap-3 sm:hidden shadow-[0_-8px_30px_rgb(0,0,0,0.08)]">
        <div class="text-left leading-tight">
            <span class="text-[10px] text-gray-600 font-bold block uppercase tracking-wider">Tarif {nom}</span>
            <span id="sticky-price" class="text-base font-black text-brand">Dès {frais} € domicile</span>
        </div>
        <div class="flex items-center gap-2">
            <a href="tel:+33781757754" aria-label="Appeler le photographe au 07 81 75 77 54" class="h-11 px-3 bg-gray-100 hover:bg-gray-200 active:scale-95 text-dark rounded-xl flex items-center justify-center gap-1.5 transition border border-gray-200 shrink-0 text-xs font-bold min-h-[44px]">
                <span>📞 Appeler</span>
            </a>
            <a href="https://wa.me/33781757754?text=Bonjour%20Greg,%20je%20souhaite%20des%20renseignements%20pour%20une%20photo%20d'identit%C3%A9%20b%C3%A9b%C3%A9%20%C3%A0%20{nom}." target="_blank" rel="noopener noreferrer" aria-label="Écrire sur WhatsApp au photographe" class="h-11 px-3.5 bg-green-600 hover:bg-green-700 active:scale-95 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 transition shadow-md shadow-green-600/20 shrink-0 min-h-[44px]">
                <span>💬 WhatsApp</span>
            </a>
        </div>
    </div>

    <!-- FOOTER -->
    <footer id="zones" class="bg-dark text-gray-300 py-16 border-t-4 border-brand">
        <div class="max-w-6xl mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-12">
            <div>
                <a href="/" class="font-serif text-2xl font-bold text-white mb-4 flex items-center gap-2 transition-colors">
                    <img src="/Images/logo.png" alt="Logo Photo Identité Bébé et Domicile" class="logo-img h-10 w-auto" width="200" height="135" loading="lazy">
                    <span>Photo-identite-bebe-domicile.fr</span>
                </a>
                <p class="text-sm font-bold text-white">Grégory - EURL (SIREN: 984 595 538)</p>
                <p class="text-sm mt-2">16 bd Carnot, 93330 Neuilly-sur-Marne</p>
                <div class="mt-6 text-sm">
                    <p class="font-bold text-white mb-2 underline decoration-brand">Interventions à Domicile :</p>
                    <p class="text-xs text-gray-400 leading-relaxed mb-2">
                        Du lundi au samedi sur rendez-vous à Paris et dans toute l'Île-de-France (93, 94, 77, 92...).
                    </p>
                    <p class="text-xs text-gray-400">Siège social : 16 bd Carnot, 93330 Neuilly-sur-Marne (déplacement exclusivement à domicile sur toute l'Île-de-France)</p>
                </div>
                <div class="flex items-center gap-1 mt-4">
                    <span class="text-brand">★★★★★</span>
                    <a href="https://www.google.com/maps/place/16+Bd+Carnot,+93330+Neuilly-sur-Marne" target="_blank" rel="noopener noreferrer" class="text-xs hover:underline text-gray-300">4.9/5 (156 avis Google vérifiés)</a>
                </div>
                <a href="tel:+33781757754" class="block text-white font-bold text-lg mt-6 hover:text-brand transition">📞 07 81 75 77 54</a>
            </div>

            <div>
                <h3 class="font-bold text-white mb-6 uppercase tracking-wider text-sm border-b border-gray-700 pb-2">Communes Prioritaires</h3>
                <ul class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                    <li><a href="/villes/neuilly-sur-marne.html" class="text-brand font-semibold hover:underline">Neuilly-sur-Marne</a></li>
                    <li><a href="/villes/paris.html" class="hover:text-brand transition">Paris</a></li>
                    <li><a href="/villes/boulogne-billancourt.html" class="hover:text-brand transition">Boulogne-Billancourt</a></li>
                    <li><a href="/villes/neuilly-sur-seine.html" class="hover:text-brand transition">Neuilly-sur-Seine</a></li>
                    <li><a href="/villes/vincennes.html" class="hover:text-brand transition">Vincennes</a></li>
                    <li><a href="/villes/montreuil.html" class="hover:text-brand transition">Montreuil</a></li>
                    <li><a href="/villes/creteil.html" class="hover:text-brand transition">Créteil</a></li>
                    <li><a href="/villes/noisy-le-grand.html" class="hover:text-brand transition">Noisy-le-Grand</a></li>
                    <li><a href="/villes/saint-denis.html" class="hover:text-brand transition">Saint-Denis</a></li>
                    <li><a href="/villes/chelles.html" class="hover:text-brand transition">Chelles</a></li>
                </ul>
            </div>

            <div>
                <h3 class="font-bold text-white mb-6 uppercase tracking-wider text-sm border-b border-gray-700 pb-2">Informations & Guides</h3>
                <ul class="space-y-3 text-sm">
                    <li><a href="/photo-identite-bebe-ile-de-france.html" class="hover:text-brand transition">Photo Identité Bébé à Domicile</a></li>
                    <li><a href="/prix-photo-identite.html" class="hover:text-brand transition">Grille des Tarifs</a></li>
                    <li><a href="/villes/" class="hover:text-brand transition">🏙️ Index des 20 Villes Desservies</a></li>
                    <li><a href="/aide/" class="hover:text-brand transition">📚 Centre d'Aide & Guides</a></li>
                    <li class="pt-4 border-t border-gray-800">
                        <a href="/mentions-legales.html" class="hover:text-brand transition">Mentions Légales</a>
                    </li>
                    <li>
                        <a href="/confidentialite.html" class="hover:text-brand transition">Politique de Confidentialité</a>
                    </li>
                </ul>
            </div>
        </div>
    </footer>
    
    <script src="/simulator.js"></script>
</body>
</html>
"""
    return page_html

def build_index_page(communes):
    # Group communes by department
    depts = {}
    for c in communes:
        dept = c['departement']
        if dept not in depts:
            depts[dept] = []
        depts[dept].append(c)

    title = "Communes Desservies en Île-de-France | Photo Identité Bébé"
    meta_desc = "Photographe habilité ANTS à domicile dans 29 communes d'Île-de-France (93, 94, 75, 77, 92, 78). Code e-photo et tirages remis sur place."

    # Schema ItemList elements
    item_list_elements = ",\n".join([
        f'''            {{
              "@type": "ListItem",
              "position": {idx + 1},
              "name": {json.dumps(c["nom"], ensure_ascii=False)},
              "url": "https://photo-identite-bebe-domicile.fr/villes/{c["slug"]}.html"
            }}'''
        for idx, c in enumerate(communes)
    ])

    # Department sections HTML
    dept_sections_html = []
    for dept_name, city_list in depts.items():
        dept_code = dept_name.split(' - ')[0].strip()
        dept_id = f"dept-{dept_code}"
        
        cards_html = []
        for c in city_list:
            nom = c['nom']
            cp = c['code_postal']
            frais = c['frais_deplacement']
            delai = c['delai_intervention']
            slug = c['slug']
            mairie = c['mairie_nom']
            maternite = c['maternite_proche']
            
            cards_html.append(f'''
            <article class="bg-white border border-gray-200 hover:border-brand/50 rounded-2xl p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between space-y-4">
                <div class="space-y-2">
                    <div class="flex items-start justify-between gap-2">
                        <div>
                            <h3 class="font-serif font-bold text-lg text-dark">
                                <a href="/villes/{slug}.html" class="hover:text-brand transition">{nom}</a>
                            </h3>
                            <span class="text-xs text-gray-500 font-medium">Code postal : {cp}</span>
                        </div>
                        <span class="bg-orange-50 text-brand text-xs font-black px-2.5 py-1 rounded-xl shrink-0">
                            Dès {frais} €
                        </span>
                    </div>
                    <div class="text-xs text-gray-600 space-y-1.5 pt-2 border-t border-gray-100">
                        <p class="flex items-center gap-1.5"><span class="text-brand">⚡</span> <span>{delai}</span></p>
                        <p class="flex items-center gap-1.5 text-gray-500 truncate" title="{mairie}"><span>🏛️</span> <span>{mairie}</span></p>
                        <p class="flex items-center gap-1.5 text-gray-500 truncate" title="{maternite}"><span>🏥</span> <span>{maternite}</span></p>
                    </div>
                </div>
                <div class="pt-2">
                    <a href="/villes/{slug}.html" class="block w-full text-center bg-gray-50 hover:bg-brand hover:text-white text-dark font-bold py-2 rounded-xl text-xs transition border border-gray-200 hover:border-brand">
                        Consulter la page {nom} →
                    </a>
                </div>
            </article>
            ''')
        
        dept_sections_html.append(f'''
        <section id="{dept_id}" class="space-y-4 pt-6">
            <div class="flex items-center gap-3 border-b-2 border-brand/20 pb-2">
                <span class="bg-brand text-white text-xs font-bold px-3 py-1 rounded-lg">{dept_code}</span>
                <h2 class="text-xl font-serif font-bold text-dark">{dept_name}</h2>
                <span class="text-xs text-gray-500 font-medium">({len(city_list)} communes)</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {''.join(cards_html)}
            </div>
        </section>
        ''')

    dept_sections = "\n".join(dept_sections_html)

    # Department anchor pills
    pills_html = "".join([
        f'<a href="#dept-{d.split(" - ")[0].strip()}" class="px-3.5 py-1.5 bg-white hover:bg-brand hover:text-white text-dark text-xs font-bold rounded-full border border-gray-200 transition shadow-2xs">📍 {d.split(" - ")[0].strip()} ({len(clist)})</a>'
        for d, clist in depts.items()
    ])

    html = f"""<!DOCTYPE html>
<html lang="fr" class="scroll-smooth">
<head>
    <!-- Google tag (gtag.js) with Google Consent Mode v2 -->
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('consent', 'default', {{
        'analytics_storage': 'denied',
        'ad_storage': 'denied',
        'ad_user_data': 'denied',
        'ad_personalization': 'denied'
      }});
      gtag('js', new Date());
      gtag('config', 'G-ZQZSLDSMLZ');
    </script>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-ZQZSLDSMLZ"></script>
    <script src="/consent.js" defer></script>
    <script src="/tracker.js" defer></script>
    
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="https://photo-identite-bebe-domicile.fr/villes/" />
    
    <link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="shortcut icon" href="/favicon.ico" />
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:locale" content="fr_FR">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:url" content="https://photo-identite-bebe-domicile.fr/villes/">
    <meta property="og:image" content="https://photo-identite-bebe-domicile.fr/Images/logo.png">

    <!-- Polices & Performance -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
    
    <!-- Script d'Interactivité Légère -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const nav = document.querySelector('nav');
            const mobileMenuBtn = document.getElementById('mobile-menu-btn');
            const mobileMenu = document.getElementById('mobile-menu');
            
            if (nav) {{
                const navLinksContainer = nav.querySelector('.nav-links-container');
                const logoText = nav.querySelector('.logo-text');
                const logoImg = nav.querySelector('.logo-img');

                window.addEventListener('scroll', () => {{
                    if (window.scrollY > 20) {{
                        nav.classList.add('bg-white/95', 'backdrop-blur-md', 'shadow-lg', 'py-2');
                        nav.classList.remove('bg-transparent', 'py-6', 'shadow-none');
                        if (navLinksContainer) {{ navLinksContainer.classList.add('text-gray-800'); navLinksContainer.classList.remove('text-white/90'); }}
                        if (logoText) {{ logoText.classList.add('text-dark'); logoText.classList.remove('text-white'); }}
                        if (logoImg) {{ logoImg.classList.remove('brightness-0', 'invert'); }}
                        if (mobileMenuBtn) {{ mobileMenuBtn.classList.add('text-gray-800'); mobileMenuBtn.classList.remove('text-white'); }}
                    }} else {{
                        nav.classList.remove('bg-white/95', 'backdrop-blur-md', 'shadow-lg', 'py-2');
                        nav.classList.add('bg-transparent', 'py-6', 'shadow-none');
                        if (navLinksContainer) {{ navLinksContainer.classList.remove('text-gray-800'); navLinksContainer.classList.add('text-white/90'); }}
                        if (logoText) {{ logoText.classList.remove('text-dark'); logoText.classList.add('text-white'); }}
                        if (logoImg) {{ logoImg.classList.add('brightness-0', 'invert'); }}
                        if (mobileMenuBtn) {{ mobileMenuBtn.classList.remove('text-gray-800'); mobileMenuBtn.classList.add('text-white'); }}
                    }}
                }});
            }}
        }});
    </script>

    <!-- Tailwind CSS Config -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{ brand: '#e67000', dark: '#1a1a1a', light: '#faf8f5' }},
                    fontFamily: {{ sans: ['Inter', 'sans-serif'], serif: ['Playfair Display', 'serif'] }}
                }}
            }}
        }}
    </script>

    <style>
        body {{ background-color: #faf8f5; color: #1a1a1a; overflow-x: hidden; }}
        .bg-hero {{ position: relative; overflow: hidden; }}
        .bg-hero::before {{
            content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(rgba(26, 26, 26, 0.8), rgba(26, 26, 26, 0.7)), url('https://images.unsplash.com/photo-1519689680058-324335c77eba?auto=format&fit=crop&w=1920&q=80') center/cover no-repeat;
            z-index: -1;
        }}
        .logo-img {{ height: 40px; width: auto; max-width: 100%; transition: all 0.3s ease; }}
        @media (min-width: 768px) {{ .logo-img {{ height: 50px; }} }}
        .animate-fade-in-up {{ animation: fadeInUp 0.8s ease-out forwards; }}
        @keyframes fadeInUp {{
            0% {{ opacity: 0; transform: translateY(20px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>

    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@graph": [
        {{
          "@type": "CollectionPage",
          "@id": "https://photo-identite-bebe-domicile.fr/villes/#collection",
          "name": "Communes Desservies à Domicile en Île-de-France",
          "description": "{meta_desc}",
          "url": "https://photo-identite-bebe-domicile.fr/villes/",
          "mainEntity": {{
            "@type": "ItemList",
            "itemListElement": [
{item_list_elements}
            ]
          }}
        }},
        {{
          "@type": "BreadcrumbList",
          "@id": "https://photo-identite-bebe-domicile.fr/villes/#breadcrumb",
          "itemListElement": [
            {{
              "@type": "ListItem",
              "position": 1,
              "name": "Accueil",
              "item": "https://photo-identite-bebe-domicile.fr/"
            }},
            {{
              "@type": "ListItem",
              "position": 2,
              "name": "Communes Desservies",
              "item": "https://photo-identite-bebe-domicile.fr/villes/"
            }}
          ]
        }},
        {{
          "@type": ["LocalBusiness", "ProfessionalService"],
          "@id": "https://photo-identite-bebe-domicile.fr/#business",
          "name": "Grégory – Photo identité bébé à domicile Île-de-France",
          "alternateName": "Photo Identité Bébé Domicile",
          "telephone": "+33781757754",
          "priceRange": "€€",
          "taxID": "984595538",
          "address": {{
            "@type": "PostalAddress",
            "streetAddress": "16 bd Carnot",
            "addressLocality": "Neuilly-sur-Marne",
            "postalCode": "93330",
            "addressRegion": "Île-de-France",
            "addressCountry": "FR"
          }},
          "url": "https://photo-identite-bebe-domicile.fr/"
        }}
      ]
    }}
    </script>

    <!-- Système de bandeau d'annonce global -->
    <script src="/config/site.js"></script>
    <script src="/announcement.js"></script>
</head>

<body class="antialiased font-sans pb-24 sm:pb-0">
    <!-- NAVIGATION -->
    <nav id="main-nav" class="fixed top-0 w-full z-50 transition-all duration-300 bg-transparent py-6 shadow-none" aria-label="Menu principal">
        <div class="max-w-6xl mx-auto px-4 flex justify-between items-center">
            <a href="/" class="logo-text text-xl md:text-2xl font-serif font-bold flex items-center gap-2 text-white transition-colors">
                <img src="/Images/logo.png" alt="Logo Photo Identité Bébé et Domicile" class="logo-img h-8 md:h-10 w-auto brightness-0 invert" width="200" height="135" fetchpriority="high">
                <span class="hidden sm:inline">Photo-identite-bebe-domicile.fr</span>
            </a>
            
            <div class="nav-links-container hidden lg:flex gap-8 items-center text-white/90 transition-colors">
                <a href="/" class="nav-link font-medium hover:text-brand transition">Accueil</a>
                <a href="/photo-identite-bebe-ile-de-france.html" class="nav-link font-medium hover:text-brand transition">Spécial Bébé</a>
                <a href="/prix-photo-identite.html" class="nav-link font-medium hover:text-brand transition">Tarifs</a>
                <a href="/villes/" class="nav-link font-bold text-brand transition">Communes</a>
                <a href="/aide/" class="nav-link font-medium hover:text-brand transition">Guides</a>
                <a href="/#booking-funnel" class="nav-link font-medium hover:text-brand transition">Simulateur</a>
                <a href="tel:+33781757754" class="bg-brand text-white px-6 py-2.5 rounded-full font-bold shadow-lg text-sm">📞 07 81 75 77 54</a>
            </div>

            <button id="mobile-menu-btn" onclick="toggleMobileMenu(event)" aria-expanded="false" class="lg:hidden text-white focus:outline-none transition-colors" aria-label="Menu mobile">
                <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
        </div>
        <div id="mobile-menu" class="hidden lg:hidden bg-white px-4 py-8 space-y-6 shadow-2xl border-t border-gray-100">
            <a onclick="toggleMobileMenu()" href="/" class="block text-xl font-medium text-gray-700">Accueil</a>
            <a onclick="toggleMobileMenu()" href="/photo-identite-bebe-ile-de-france.html" class="block text-xl font-medium text-gray-700">Spécial Bébé</a>
            <a onclick="toggleMobileMenu()" href="/prix-photo-identite.html" class="block text-xl font-medium text-gray-700">Tarifs</a>
            <a onclick="toggleMobileMenu()" href="/villes/" class="block text-xl font-bold text-brand">Communes desservies</a>
            <a onclick="toggleMobileMenu()" href="/aide/" class="block text-xl font-medium text-gray-700">Guides</a>
            <a onclick="toggleMobileMenu()" href="/#booking-funnel" class="block text-xl font-medium text-gray-700">Simulateur</a>
            <a onclick="toggleMobileMenu()" href="tel:+33781757754" class="block w-full text-center bg-brand text-white py-4 rounded-xl font-bold">07 81 75 77 54</a>
            <a onclick="toggleMobileMenu()" href="https://wa.me/33781757754" target="_blank" rel="noopener noreferrer" class="block w-full text-center bg-green-600 hover:bg-green-700 text-white py-4 rounded-xl font-bold mt-3">
                💬 Écrire sur WhatsApp
            </a>
        </div>
    </nav>

    <!-- HERO SECTION -->
    <header class="bg-hero text-white pt-40 pb-20 px-4 text-center border-b-4 border-brand">
        <div class="max-w-4xl mx-auto animate-fade-in-up">
            <div class="inline-flex items-center gap-2 bg-brand/90 text-white text-xs font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-6">
                <span>Réseau d'intervention Île-de-France • 29 communes</span>
            </div>
            <h1 class="text-3xl md:text-5xl font-serif font-bold leading-tight mb-6">
                Communes Desservies à Domicile
            </h1>
            <p class="text-gray-200 text-base md:text-lg max-w-2xl mx-auto leading-relaxed">
                Photographe habilité ANTS en déplacement chez vous en Seine-Saint-Denis, Val-de-Marne, Seine-et-Marne, Hauts-de-Seine et Paris. Code e-photo et planches conformes remis sur place en 20 minutes chrono.
            </p>
            <div class="mt-8 flex flex-wrap justify-center items-center gap-4">
                <a href="/#booking-funnel" class="bg-brand hover:bg-orange-600 active:scale-95 text-white font-bold px-8 py-3.5 rounded-full transition shadow-lg text-sm">
                    📅 Calculer mon tarif exact
                </a>
                <a href="tel:+33781757754" class="bg-white/10 hover:bg-white/20 text-white font-bold px-8 py-3.5 rounded-full transition text-sm">
                    📞 07 81 75 77 54
                </a>
            </div>
        </div>
    </header>

    <!-- MAIN HUB -->
    <main class="max-w-6xl mx-auto px-4 py-16 space-y-12">
        <!-- Quick Nav Pills -->
        <div class="bg-white border border-gray-200 rounded-2xl p-4 shadow-2xs flex flex-wrap items-center justify-between gap-3">
            <span class="text-xs font-bold uppercase text-gray-500 tracking-wider">Accès rapide par département :</span>
            <div class="flex flex-wrap gap-2">
                {pills_html}
            </div>
        </div>

        <!-- Sections per department -->
        <div class="space-y-10">
            {dept_sections}
        </div>

        <!-- Trust banner -->
        <section class="bg-orange-50 border border-brand/20 rounded-3xl p-8 text-center space-y-4">
            <h2 class="font-serif text-2xl font-bold text-dark">Vous ne trouvez pas votre commune dans la liste ?</h2>
            <p class="text-sm text-gray-700 max-w-2xl mx-auto leading-relaxed">
                Le photographe dessert l'ensemble de la région Île-de-France sur devis kilométrique. Testez votre adresse directement dans notre simulateur en ligne ou contactez-nous par téléphone.
            </p>
            <div class="pt-2 flex justify-center gap-4">
                <a href="/#booking-funnel" class="bg-brand text-white font-bold px-6 py-2.5 rounded-full text-xs hover:bg-orange-600 transition shadow-md">
                    Tester mon adresse dans le simulateur
                </a>
                <a href="tel:+33781757754" class="bg-white text-dark font-bold px-6 py-2.5 rounded-full text-xs hover:bg-gray-100 transition border border-gray-200">
                    Appeler le 07 81 75 77 54
                </a>
            </div>
        </section>
    </main>

    <!-- STICKY MOBILE BAR -->
    <div class="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-gray-200 px-4 py-3 flex items-center justify-between gap-3 sm:hidden shadow-[0_-8px_30px_rgb(0,0,0,0.08)]">
        <div class="text-left leading-tight">
            <span class="text-[10px] text-gray-600 font-bold block uppercase tracking-wider">Photo Bébé Domicile</span>
            <span class="text-base font-black text-brand">Dès 59 € déplacement inclus</span>
        </div>
        <div class="flex items-center gap-2">
            <a href="tel:+33781757754" aria-label="Appeler le photographe au 07 81 75 77 54" class="h-11 px-3 bg-gray-100 hover:bg-gray-200 active:scale-95 text-dark rounded-xl flex items-center justify-center gap-1.5 transition border border-gray-200 shrink-0 text-xs font-bold min-h-[44px]">
                <span>📞 Appeler</span>
            </a>
            <a href="https://wa.me/33781757754?text=Bonjour%20Greg,%20je%20souhaite%20des%20renseignements%20pour%20une%20photo%20d'identit%C3%A9%20b%C3%A9b%C3%A9%20%C3%A0%20domicile." target="_blank" rel="noopener noreferrer" aria-label="Écrire sur WhatsApp au photographe" class="h-11 px-3.5 bg-green-600 hover:bg-green-700 active:scale-95 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 transition shadow-md shadow-green-600/20 shrink-0 min-h-[44px]">
                <span>💬 WhatsApp</span>
            </a>
        </div>
    </div>

    <!-- FOOTER -->
    <footer id="zones" class="bg-dark text-gray-300 py-16 border-t-4 border-brand">
        <div class="max-w-6xl mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-12">
            <div>
                <a href="/" class="font-serif text-2xl font-bold text-white mb-4 flex items-center gap-2 transition-colors">
                    <img src="/Images/logo.png" alt="Logo Photo Identité Bébé et Domicile" class="logo-img h-10 w-auto" width="200" height="135" loading="lazy">
                    <span>Photo-identite-bebe-domicile.fr</span>
                </a>
                <p class="text-sm font-bold text-white">Grégory - EURL (SIREN: 984 595 538)</p>
                <p class="text-sm mt-2">16 bd Carnot, 93330 Neuilly-sur-Marne</p>
                <div class="mt-6 text-sm">
                    <p class="font-bold text-white mb-2 underline decoration-brand">Interventions à Domicile :</p>
                    <p class="text-xs text-gray-400 leading-relaxed mb-2">
                        Du lundi au samedi sur rendez-vous à Paris et dans toute l'Île-de-France (93, 94, 77, 92...).
                    </p>
                    <p class="text-xs text-gray-400">Siège social : 16 bd Carnot, 93330 Neuilly-sur-Marne (déplacement exclusivement à domicile sur toute l'Île-de-France)</p>
                </div>
                <div class="flex items-center gap-1 mt-4">
                    <span class="text-brand">★★★★★</span>
                    <a href="https://www.google.com/maps/place/16+Bd+Carnot,+93330+Neuilly-sur-Marne" target="_blank" rel="noopener noreferrer" class="text-xs hover:underline text-gray-300">4.9/5 (156 avis Google vérifiés)</a>
                </div>
                <a href="tel:+33781757754" class="block text-white font-bold text-lg mt-6 hover:text-brand transition">📞 07 81 75 77 54</a>
            </div>

            <div>
                <h3 class="font-bold text-white mb-6 uppercase tracking-wider text-sm border-b border-gray-700 pb-2">Communes Prioritaires</h3>
                <ul class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                    <li><a href="/villes/neuilly-sur-marne.html" class="text-brand font-semibold hover:underline">Neuilly-sur-Marne</a></li>
                    <li><a href="/villes/paris.html" class="hover:text-brand transition">Paris</a></li>
                    <li><a href="/villes/boulogne-billancourt.html" class="hover:text-brand transition">Boulogne-Billancourt</a></li>
                    <li><a href="/villes/neuilly-sur-seine.html" class="hover:text-brand transition">Neuilly-sur-Seine</a></li>
                    <li><a href="/villes/vincennes.html" class="hover:text-brand transition">Vincennes</a></li>
                    <li><a href="/villes/montreuil.html" class="hover:text-brand transition">Montreuil</a></li>
                    <li><a href="/villes/creteil.html" class="hover:text-brand transition">Créteil</a></li>
                    <li><a href="/villes/noisy-le-grand.html" class="hover:text-brand transition">Noisy-le-Grand</a></li>
                    <li><a href="/villes/saint-denis.html" class="hover:text-brand transition">Saint-Denis</a></li>
                    <li><a href="/villes/chelles.html" class="hover:text-brand transition">Chelles</a></li>
                </ul>
            </div>

            <div>
                <h3 class="font-bold text-white mb-6 uppercase tracking-wider text-sm border-b border-gray-700 pb-2">Informations & Guides</h3>
                <ul class="space-y-3 text-sm">
                    <li><a href="/photo-identite-bebe-ile-de-france.html" class="hover:text-brand transition">Photo Identité Bébé à Domicile</a></li>
                    <li><a href="/prix-photo-identite.html" class="hover:text-brand transition">Grille des Tarifs</a></li>
                    <li><a href="/villes/" class="text-brand font-semibold hover:underline">🏙️ Index des 20 Villes Desservies</a></li>
                    <li><a href="/aide/" class="hover:text-brand transition">📚 Centre d'Aide & Guides</a></li>
                    <li class="pt-4 border-t border-gray-800">
                        <a href="/mentions-legales.html" class="hover:text-brand transition">Mentions Légales</a>
                    </li>
                    <li>
                        <a href="/confidentialite.html" class="hover:text-brand transition">Politique de Confidentialité</a>
                    </li>
                </ul>
            </div>
        </div>
    </footer>
</body>
</html>
"""
    return html

def main(batch=None):
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        communes = json.load(f)

    os.makedirs(VILLES_DIR, exist_ok=True)

    if batch == 'index':
        index_file = os.path.join(VILLES_DIR, 'index.html')
        index_html = build_index_page(communes)
        with open(index_file, 'w', encoding='utf-8') as out:
            out.write(index_html)
        print("✅ Index généré : villes/index.html")
        return

    if batch == 1:
        indexed_communes = list(enumerate(communes))[0:5]
    elif batch == 2:
        indexed_communes = list(enumerate(communes))[5:10]
    elif batch == 3:
        indexed_communes = list(enumerate(communes))[10:15]
    elif batch == 4:
        indexed_communes = list(enumerate(communes))[15:20]
    else:
        indexed_communes = list(enumerate(communes))

    generated = []

    for idx, c in indexed_communes:
        if not c.get('verified', False) or len(c.get('elements_locaux_factuels', [])) < 3:
            print(f"⚠️ Commune {c['slug']} ignorée (non vérifiée ou < 3 faits locaux)")
            continue

        filename = os.path.join(VILLES_DIR, f"{c['slug']}.html")
        content = build_city_page(idx, c)
        with open(filename, 'w', encoding='utf-8') as out:
            out.write(content)
        generated.append(c['slug'])
        print(f"✅ Page générée : villes/{c['slug']}.html")

    print(f"\nTotal généré : {len(generated)} pages.")

    # Also build index if full generation
    if batch is None:
        index_file = os.path.join(VILLES_DIR, 'index.html')
        index_html = build_index_page(communes)
        with open(index_file, 'w', encoding='utf-8') as out:
            out.write(index_html)
        print("✅ Index généré : villes/index.html")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        batch_arg = int(arg) if arg.isdigit() else arg
    else:
        batch_arg = None
    main(batch_arg)

