#!/usr/bin/env python3
"""Integration des 9 nouvelles communes (donnees recherchees et sourcees).

Usage : ecrire les 9 objets JSON dans /tmp/nouvelles_communes.json puis executer ce script.
Le script valide, enrichit, integre, regenere, met a jour le sitemap et les compteurs,
puis lance les controles de coherence.
"""
import json, os, re, sys, subprocess, math

ROOT = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
os.chdir(ROOT if os.path.exists(os.path.join(ROOT, 'simulator.js')) else os.getcwd())

DATA = 'data/communes.json'
SRC = '/tmp/nouvelles_communes.json'

# --- Prix valides par le proprietaire (leviers A + B) ---
PRIX = {
    'Sevran': 89, 'Courbevoie': 139, 'Nanterre': 149, 'Rueil-Malmaison': 149,
    'Asnières-sur-Seine': 129, 'Clichy': 129, 'Puteaux': 139,
    'Versailles': 149, 'Saint-Germain-en-Laye': 149,
}
# Stationnement reel integre au forfait (levees B). Versailles et Saint-Germain-en-Laye
# restent a 0 : le stationnement y est majoritairement gratuit, et leur forfait de 149 EUR
# est deja au plafond du marche.
PARK_NOM = {'Courbevoie', 'Nanterre', 'Rueil-Malmaison', 'Asnières-sur-Seine',
            'Clichy', 'Puteaux'}
DELAI_PROCHE = 'Intervention sous 24h à 48h à domicile'
DELAI_LOIN = 'Intervention sur rendez-vous à domicile'
LOIN = {'Versailles', 'Saint-Germain-en-Laye'}

REQUIS = ['slug', 'nom', 'departement', 'code_postal', 'coordonnees', 'mairie_nom',
          'mairie_adresse', 'mairie_service', 'source_url', 'maternite_proche',
          'hopital_proche', 'elements_locaux_factuels',
          'description_locale', 'contexte_mobilite', 'conseil_local']

INTERDITS = ['zéro rejet', 'zero rejet', '100 % conforme', '100% conforme', 'agréé ANTS',
             'agrément ANTS', 'garantie d\'acceptation', 'certification officielle',
             'scanners de dernière', 'sans réserve', '22 critères', '22 normes']


def valider(c):
    err = []
    for k in REQUIS:
        if k not in c or c[k] in (None, '', []):
            err.append(f"champ manquant ou vide : {k}")
    co = c.get('coordonnees') or {}
    if not (isinstance(co, dict) and 'lat' in co and 'lon' in co):
        err.append('coordonnees invalides')
    else:
        if not (47.5 < float(co['lat']) < 49.5):
            err.append(f"latitude hors IDF : {co['lat']}")
        if not (1.3 < float(co['lon']) < 3.7):
            err.append(f"longitude hors IDF : {co['lon']}")
    faits = c.get('elements_locaux_factuels') or []
    faits = [f for f in faits if f and f.strip() and 'NON VÉRIFIÉ' not in f.upper()]
    if len(faits) < 3:
        err.append(f"moins de 3 faits locaux verifies ({len(faits)})")
    texte = ' '.join(str(v) for v in c.values() if isinstance(v, str)) + ' ' + ' '.join(faits)
    for mot in INTERDITS:
        if mot.lower() in texte.lower():
            err.append(f"formulation interdite : « {mot} »")
    if 'NON VÉRIFIÉ' in json.dumps(c, ensure_ascii=False).upper():
        err.append('contient des champs NON VÉRIFIÉ (a completer ou retirer)')
    return err, faits


def main():
    if not os.path.exists(SRC):
        sys.exit(f"Fichier source absent : {SRC}")
    nouvelles = json.load(open(SRC, encoding='utf-8'))
    rows = json.load(open(DATA, encoding='utf-8'))
    slugs_existants = {r['slug'] for r in rows}

    erreurs = {}
    for c in nouvelles:
        e, faits = valider(c)
        if e:
            erreurs[c.get('nom', '?')] = e
        c['elements_locaux_factuels'] = faits

    if erreurs:
        print("❌ Validation bloquante :")
        for nom, e in erreurs.items():
            print(f"   {nom} : " + ' | '.join(e))
        sys.exit(1)

    # Annuaire slug -> nom, pour convertir les voisines en {'slug','nom'}
    annuaire = {r['slug']: r['nom'] for r in rows}
    for c in nouvelles:
        annuaire[c['slug']] = c['nom']

    for c in nouvelles:
        if c['slug'] in slugs_existants:
            sys.exit(f"❌ Slug deja present : {c['slug']}")
        inconnues = [v for v in c.get('voisines', []) if v not in annuaire]
        if inconnues:
            sys.exit(f"❌ {c['nom']} : communes voisines inconnues {inconnues}")
        c['voisines'] = [{'slug': v, 'nom': annuaire[v]} for v in c.get('voisines', [])]
        c['frais_deplacement'] = PRIX[c['nom']]
        c['frais_deplacement_label'] = f"Forfait déplacement inclus — à partir de {PRIX[c['nom']]} €"
        c['delai_intervention'] = DELAI_LOIN if c['nom'] in LOIN else DELAI_PROCHE
        c['stationnement_reel'] = 20 if c['nom'] in PARK_NOM else 0
        c.setdefault('voisines', [])
        if not c['voisines']:
            c['voisines'] = []
        c['verified'] = True
        rows.append(c)

    json.dump(rows, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"✅ {len(nouvelles)} communes integrees — total {len(rows)}")

    # Sitemap
    sm = open('sitemap.xml', encoding='utf-8').read()
    ajouts = []
    for c in nouvelles:
        loc = f"https://photo-identite-bebe-domicile.fr/villes/{c['slug']}.html"
        if loc in sm:
            continue
        ajouts.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>2026-10-06</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>""")
    if ajouts:
        sm = sm.replace('</urlset>', '\n'.join(ajouts) + '\n</urlset>')
        open('sitemap.xml', 'w', encoding='utf-8').write(sm)
    print(f"✅ sitemap : {len(ajouts)} URL ajoutees ({sm.count('<url>')} au total)")

    # Compteurs
    n = len(rows)
    for f in ('scripts/generate_villes.py', 'index.html'):
        s = open(f, encoding='utf-8').read()
        s = re.sub(r'dans \d+ communes', f'dans {n} communes', s)
        s = re.sub(r'Réseau d\'intervention Île-de-France • \d+ communes',
                   f"Réseau d'intervention Île-de-France • {n} communes", s)
        s = re.sub(r'Toutes les \d+ communes desservies', f'Toutes les {n} communes desservies', s)
        s = s.replace("(93, 94, 75, 77, 92)", "(93, 94, 75, 77, 92, 78)")
        open(f, 'w', encoding='utf-8').write(s)
    print(f"✅ compteurs mis a jour ({n} communes)")

    subprocess.run([sys.executable, 'scripts/generate_villes.py'], check=True,
                   stdout=subprocess.DEVNULL)
    print("✅ pages villes regenerees")


if __name__ == '__main__':
    main()
