#!/usr/bin/env python3
"""Controle qualite du site avant upload.

Lance tous les controles en une commande :
    python3 scripts/verifier_site.py

Sortie : un rapport lisible + code de sortie 1 si un controle bloquant echoue.
Aucune dependance externe.
"""
import glob
import html
import json
import os
import re
import subprocess
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLOCKING = 0


def plat(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', t))).strip()


def titre(label, ok, detail=''):
    global BLOCKING
    if not ok:
        BLOCKING = 1
    print(f"  {'OK ' if ok else 'ECHEC'}  {label}" + (f" — {detail}" if detail else ''))


def main():
    html_files = sorted(set(glob.glob('*.html') + glob.glob('villes/*.html')
                           + glob.glob('aide/*/index.html') + glob.glob('aide/*.html')))
    js_files = ['simulator.js', 'tracker.js', 'consent.js', 'announcement.js', 'config/site.js']
    # Perimetre public uniquement : les scripts d'outillage contiennent volontairement
    # les motifs recherches, ils ne doivent pas etre scannes.
    all_files = html_files + js_files

    print(f"\n=== CONTROLE QUALITE — {len(html_files)} pages HTML ===\n")

    print("1. Formulations a risque (factuelles / juridiques)")
    forbidden = {
        "'20 km' / '20 kilomètres'": ['20 km', '20 kilomètres'],
        "'22 normes' / '22 critères'": ['22 normes', '22 critères'],
        "'Zéro Rejet'": ['Zéro Rejet', 'zéro rejet'],
        "'100 % conforme'": ['100% conforme', '100 % conforme', '100% Conforme'],
        "'conformité préfecture garantie'": ['conformité préfecture garantie'],
        "'certification officielle'": ['certification officielle'],
        "'numéro d'agrément'": ["numéro d'agrément"],
        "'agréé ANTS' (hors mention d'alias)": ['agréé ANTS'],
        'durée de visite erronée': ['15-20 min', '20-30m'],
        'sans réserve / scanners mairie': ['sans réserve', 'scanners de dernière'],
    }
    for label, pats in forbidden.items():
        hits = [f for f in all_files if any(p in open(f, encoding='utf-8').read() for p in pats)]
        allow_alias = "agréé ANTS" in label
        if allow_alias:
            # une seule occurrence toleree : la phrase d'alias de la page habilitation
            hits = [f for f in hits if f != 'photographe-agree-ants-ile-de-france.html']
        titre(label, not hits, ', '.join(hits[:3]))

    print("\n2. SEO technique")
    bad = []
    for f in html_files:
        s = open(f, encoding='utf-8').read()
        t = re.search(r'<title>(.*?)</title>', s, re.S)
        m = re.search(r'<meta\s+name="description"\s+content="(.*?)"', s, re.S)
        lt = len(plat(t.group(1))) if t else 0
        lm = len(plat(m.group(1))) if m else 0
        if lt > 60 or lm > 155 or len(re.findall(r'<h1', s)) != 1 or not t or not m:
            bad.append(f"{f} (title={lt}, meta={lm})")
    titre('title <= 60, meta <= 155, un seul H1', not bad, ', '.join(bad[:3]))

    n_ld = 0
    err_ld = []
    for f in html_files:
        s = open(f, encoding='utf-8').read()
        for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                json.loads(b)
                n_ld += 1
            except Exception as e:
                err_ld.append(f"{f}: {str(e)[:50]}")
    titre(f'JSON-LD valides ({n_ld} blocs)', not err_ld, ', '.join(err_ld[:3]))

    canon = [f for f in html_files if f != '404.html'
             and not re.search(r'<link rel="canonical"', open(f, encoding='utf-8').read())]
    titre('canonical present sur toutes les pages', not canon, ', '.join(canon[:3]))

    print("\n3. Coherence tarifaire")
    rows = json.load(open('data/communes.json', encoding='utf-8'))
    sj = open('simulator.js', encoding='utf-8').read()
    blk = re.search(r'"postalPrices": \{\n(.*?)\n    \}', sj, re.S)
    moteur = {m.group(1): int(m.group(2)) for m in re.finditer(r'"(\d{5})": (\d+)', blk.group(1))}
    data = {r['code_postal']: r['frais_deplacement'] for r in rows}
    titre('moteur et data/communes.json identiques', moteur == data,
          str({k: (moteur.get(k), v) for k, v in data.items() if moteur.get(k) != v})[:120])

    non_ronds = [p for p in set(data.values()) if not str(p).endswith('9')]
    titre('tous les forfaits finissent par 9', not non_ronds, str(sorted(non_ronds)))

    ko = []
    for f in glob.glob('villes/*.html'):
        s = open(f, encoding='utf-8').read()
        if 'id="booking-funnel"' not in s:
            continue
        cp = re.search(r'data-default-postal="(\d{5})"', s)
        if not cp:
            ko.append(f + ' (sans code postal)')
            continue
        cp = cp.group(1)
        try:
            badge = int(re.search(r'À partir de</span>\s*<span class="text-xl font-black text-brand">(\d+) €', s).group(1))
            total = int(re.search(r'id="total-price"[^>]*>(\d+) €', s).group(1))
            sticky = int(re.search(r'id="sticky-price"[^>]*>Dès (\d+) €', s).group(1))
        except AttributeError:
            ko.append(f + ' (prix introuvable)')
            continue
        if not (badge == total == sticky == data.get(cp)):
            ko.append(f"{f} ({badge}/{total}/{sticky} vs {data.get(cp)})")
    titre(f'pages villes coherentes ({len(glob.glob("villes/*.html")) - 1} pages)', not ko, '; '.join(ko[:3]))

    print("\n4. Simulateur et robustesse")
    non_protege = re.findall(r"document\.getElementById\('[a-z-]+'\)\.(?:innerText|innerHTML|classList|value)", sj)
    titre('aucun acces DOM non protege dans simulator.js', not non_protege, str(set(non_protege)))
    defaut = re.search(r"locationType: '(\w+)'", sj)
    titre("mode domicile par defaut", defaut and defaut.group(1) == 'home',
          f"valeur = {defaut.group(1) if defaut else '?'}")
    villes_home = len([f for f in glob.glob('villes/*.html')
                       if 'data-default-location="home"' in open(f, encoding='utf-8').read()])
    n_villes = len([f for f in glob.glob('villes/*.html')
                    if 'id="booking-funnel"' in open(f, encoding='utf-8').read()])
    titre(f'simulateur en mode domicile sur les pages villes ({villes_home}/{n_villes})',
          villes_home == n_villes)

    js_ko = []
    for f in js_files:
        r = subprocess.run(['node', '--check', f], capture_output=True)
        if r.returncode != 0:
            js_ko.append(f)
    titre('syntaxe JavaScript valide', not js_ko, ', '.join(js_ko))

    print("\n5. Classes CSS inexistantes")
    invalides = []
    for f in html_files:
        s = open(f, encoding='utf-8').read()
        for c in ('gray-150', 'gray-250', 'gray-350', 'gray-750', 'gray-850'):
            if c in s:
                invalides.append(f"{f}: {c}")
    titre('aucune classe Tailwind invalide', not invalides, ', '.join(invalides[:3]))

    print("\n6. Anti-duplication des pages villes")
    r = subprocess.run([sys.executable, 'scripts/check_similarity.py'],
                       capture_output=True, text=True)
    lignes = [l for l in r.stdout.splitlines() if 'similarit' in l or 'SUCC' in l or 'CHEC' in l]
    for l in lignes:
        print("      " + l.strip())
    titre('similarite inter-villes < 60 %', r.returncode == 0)

    print("\n" + "=" * 62)
    if BLOCKING:
        print("RESULTAT : au moins un controle a echoue — ne pas uploader en l'etat.")
    else:
        print("RESULTAT : tous les controles passent — pret a uploader.")
    print("=" * 62 + "\n")
    return BLOCKING


if __name__ == '__main__':
    sys.exit(main())
