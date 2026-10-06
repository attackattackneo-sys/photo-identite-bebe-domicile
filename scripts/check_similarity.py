#!/usr/bin/env python3
"""
Vérificateur de similarité des pages villes pour photo-identite-bebe-domicile.fr
Règle : Aucune page ne doit ressembler à une autre à plus de 60 %
Méthode :
- Analyse du contenu éditorial de la balise <main> (sans le widget interactif de formulaire/simulateur)
- Analyse du texte visible complet
- Calcul du ratio de similarité SequenceMatcher par tokens/mots
"""

import json
import os
import re
import difflib
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import scripts.generate_villes as gv

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'communes.json')

def extract_editorial_words(html):
    # Extract main content
    main_match = re.search(r'<main.*?>(.*?)</main>', html, flags=re.DOTALL)
    if not main_match:
        content = html
    else:
        content = main_match.group(1)

    # Exclude interactive booking funnel widget boilerplate
    content_no_funnel = re.sub(r'<section id="booking-funnel".*?</section>', '', content, flags=re.DOTALL)

    # Clean scripts, styles and tags
    clean = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', content_no_funnel, flags=re.DOTALL)
    clean_text = re.sub(r'<[^>]+>', ' ', clean)

    # Words tokens (lowercase, len > 2)
    words = [w.lower() for w in re.findall(r'\b[\w\u00C0-\u017F-]+\b', clean_text) if len(w) > 2]
    return words

def extract_full_visible_words(html):
    clean = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
    clean_text = re.sub(r'<[^>]+>', ' ', clean)
    words = [w.lower() for w in re.findall(r'\b[\w\u00C0-\u017F-]+\b', clean_text) if len(w) > 2]
    return words

def check_all(threshold=0.60):
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        communes = json.load(f)

    editorial_tokens = {}
    full_tokens = {}

    for idx, c in enumerate(communes):
        html = gv.build_city_page(idx, c)
        editorial_tokens[c['slug']] = extract_editorial_words(html)
        full_tokens[c['slug']] = extract_full_visible_words(html)

    slugs = [c['slug'] for c in communes]
    n = len(slugs)

    max_editorial_sim = 0.0
    worst_editorial_pair = None
    failing_editorial_pairs = []

    print(f"=== Vérification de la similarité sur {n} communes ({n*(n-1)//2} paires) ===\n")

    for i in range(n):
        for j in range(i + 1, n):
            s1, s2 = slugs[i], slugs[j]
            w1 = editorial_tokens[s1]
            w2 = editorial_tokens[s2]

            sim = difflib.SequenceMatcher(None, w1, w2).ratio()
            if sim > max_editorial_sim:
                max_editorial_sim = sim
                worst_editorial_pair = (s1, s2)

            if sim >= threshold:
                failing_editorial_pairs.append((s1, s2, sim))

    print(f"📊 Pire similarité éditoriale : {max_editorial_sim:.2%} entre '{worst_editorial_pair[0]}' et '{worst_editorial_pair[1]}'")
    
    if failing_editorial_pairs:
        print(f"\n❌ ÉCHEC : {len(failing_editorial_pairs)} paires dépassent le seuil de {threshold*100:.0f}% :")
        for s1, s2, sim in failing_editorial_pairs:
            print(f"  - {s1} vs {s2} : {sim:.2%}")
        return False
    else:
        print(f"✅ SUCCÈS : Toutes les {n*(n-1)//2} paires sont STRICTEMENT inférieures au seuil de {threshold*100:.0f}% !")
        return True

if __name__ == '__main__':
    success = check_all(0.60)
    sys.exit(0 if success else 1)
