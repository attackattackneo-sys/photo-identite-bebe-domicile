# Rapport Final : Recentrage sur la prestation Photo d'Identité à Domicile

> **Date d'exécution :** 16 septembre 2026  
> **Statut :** Livré, testé et validé  
> **Auteur :** Développeur Web Senior  

---

## 1. Résumé de l'objectif business

Le site **Photo-identite-bebe-domicile.fr** a pour cœur de métier la réalisation de photos d'identité officielles et certifiées ANTS **directement au domicile des clients** (nourrissons, bébés, familles, seniors et personnes à mobilité réduite) partout en Île-de-France.

### Problématique initiale résolue :
* La présence sur la page d'accueil de boutons proéminents et de tarifs en atelier (« Au Studio dès 10 € ») créait une forte **confusion commerciale** : les prospects pensaient que la séance complète était à 10 €, ce qui dévalorisait la prestation de déplacement à domicile (dès 59 € déplacement inclus) et générait des frictions lors de la réservation.
* **Solution apportée :**
  1. Recentrer 100% de la proposition de valeur de la page d'accueil sur la prestation **à domicile**.
  2. Mettre en valeur le **simulateur de calcul de déplacement** en le rendant immédiatement accessible, intuitif et lisible dès l'arrivée sur le site.
  3. Remplacer les gros blocs de tarifs studio par une **passerelle externe discrète et configurable** pointant vers le site vitrine du studio physique (`https://www.gregstudiophoto.fr/`).
  4. Conserver **strictement le design global** (couleurs, polices, composants, animations) et l'ensemble de la logique de calcul existante.

---

## 2. Analyse initiale (Rappel court)

L'audit technique préliminaire a révélé :
* **Stack Zero-Build :** Site statique multi-pages pur (HTML5 / Vanilla JavaScript ES6), Tailwind CSS v3 injecté via CDN (`cdn.tailwindcss.com`) et Lucide Icons. Aucun bundler ni fichier `.env` côté client.
* **Moteur du Simulateur :** Logique puissante couplée aux APIs Nominatim (OpenStreetMap) pour le géocodage et OSRM pour le routage routier réel depuis Neuilly-sur-Marne, combinée à des forfaits postaux spécifiques (Chelles, Noisy-le-Grand, Montreuil, Aulnay-sous-Bois) et un barème kilométrique / temps.
* **Couplage technique fort :** Le script `simulator.js` ciblait directement des identifiants DOM stricts (`#btn-loc-studio`, `#btn-loc-home`, `#travel-panel`, etc.). La neutralisation visuelle du Studio devait impérativement préserver ces éléments sous forme masquée (`hidden`) pour éviter tout plantage JavaScript.

---

## 3. Liste des fichiers modifiés et leurs rôles

| Fichier | Nature & Rôle des modifications |
| :--- | :--- |
| [`index.html`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/index.html) | **Page d'accueil principale :**<br>• Retrait des liens « Studio » dans la barre de navigation desktop et le menu mobile.<br>• Harmonisation du badge Hero : remplacement de `Dès 59€ domicile / 10€ studio` par `Dès 59 € à domicile (IDF)`.<br>• Mise en avant du CTA principal : *« 🚗 Estimer mon tarif à domicile »* (scroll fluide vers `#booking-funnel`).<br>• Passage du simulateur en mode domicile natif via `data-default-location="home"`.<br>• Remplacement du sélecteur Studio/Domicile par un badge de confirmation rassurant (*Studio mobile IDF*).<br>• Réorganisation séquentielle des étapes du formulaire : (1) Localisation en IDF, (2) Sujets à photographier.<br>• Intégration du lien discret sous le simulateur et en pied de page du footer vers `https://www.gregstudiophoto.fr/`.<br>• Remplacement du tableau d'horaires d'ouverture physique par les horaires et zones de déplacement à domicile. |
| [`photo-identite-a-domicile-ile-de-france.html`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/photo-identite-a-domicile-ile-de-france.html) | **Page d'atterrissage Service Domicile IDF :**<br>• Retrait du lien studio dans la navigation.<br>• Simulateur refondu en mode domicile natif (boutons studio/domicile masqués, carte de réassurance, champ de commune en étape 1).<br>• Ajout de la passerelle discrète studio sous le simulateur et dans le footer. |
| [`photo-identite-bebe-ile-de-france.html`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/photo-identite-bebe-ile-de-france.html) | **Page d'atterrissage Photo Bébé :**<br>• Navigation nettoyée, simulateur 100% domicile natif, passerelle externe studio ajoutée. |
| [`photographe-agree-ants-ile-de-france.html`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/photographe-agree-ants-ile-de-france.html) | **Page d'atterrissage Agrément ANTS :**<br>• Navigation nettoyée, simulateur 100% domicile natif, passerelle externe studio ajoutée. |
| [`prix-photo-identite.html`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/prix-photo-identite.html) | **Page Tarifs & Devis :**<br>• Navigation nettoyée, simulateur 100% domicile natif, passerelle externe studio ajoutée. |
| `villes/*.html` (11 pages villes) | **Pages d'atterrissage locales :**<br>• *Paris, Neuilly-sur-Marne, Boulogne, Neuilly-sur-Seine, Vincennes, Montreuil, Créteil, Noisy-le-Grand, Saint-Denis, Chelles, Bussy-Saint-Georges* : toutes alignées sur la navigation sans lien studio, simulateur domicile natif et passerelle discrète. |
| `404.html`, `confidentialite.html`, `informations.html`, `mentions-legales.html`, `aide/*.html` | **Pages d'informations & d'aide :**<br>• Remplacement des horaires de présence studio physique par les horaires d'interventions à domicile avec lien direct vers le studio. |
| [`config/site.js`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/config/site.js) | **Configuration centralisée & Contrôleur global :**<br>• Objet `studio` contenant l'URL externe (`https://www.gregstudiophoto.fr/`) et le nom (`Greg Studio Photo`).<br>• Routine Javascript autonome (Zero-Build) qui synchronise automatiquement tous les éléments du DOM portant les attributs `data-studio-link` et `data-studio-name`. |
| [`studio-photo.html`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/studio-photo.html) | **Page d'archive du Studio physique :**<br>• Insertion en tête de document d'un en-tête documentaire complet précisant son statut et les instructions de réactivation dans le menu principal si nécessaire.<br>• Maintien de la page en ligne pour préserver le référencement naturel existant. |

---

## 4. Fichiers et composants désactivés / archivés & Méthode de réactivation

Aucun composant ni fichier n'a été supprimé. Tout est archivé proprement dans le code source :

### A. Sélecteur Studio dans le simulateur (`index.html`)
* **État actuel :** Les boutons `#btn-loc-studio` et `#btn-loc-home` sont conservés dans un conteneur `<div class="hidden">` avec `aria-hidden="true"` et `tabindex="-1"`. Cela permet à `simulator.js` de continuer à fonctionner sans aucune erreur JS.
* **Pour réactiver le choix Studio dans le simulateur :**
  1. Ouvrir [`index.html`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/index.html) à la ligne 760.
  2. Retirer la classe `hidden` du conteneur `<div>` englobant `#btn-loc-studio` et `#btn-loc-home`.
  3. Supprimer l'attribut `data-default-location="home"` sur la balise `<main id="booking-funnel">`.

### B. Page dédiée au Studio (`studio-photo.html`)
* **État actuel :** La page existe toujours sur le serveur mais n'est plus liée dans les menus de navigation de la page principale pour éviter la déperdition de trafic.
* **Pour réactiver la page dans la navigation :**
  1. Dans [`index.html`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/index.html), ajouter dans `.nav-links-container` :
     ```html
     <a href="studio-photo.html" class="hover:text-brand transition">Studio</a>
     ```
  2. Dans [`index.html`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/index.html), ajouter dans `#mobile-menu` :
     ```html
     <a onclick="toggleMobileMenu()" href="studio-photo.html" class="flex items-center gap-3 text-lg font-medium text-gray-800 hover:text-brand transition-colors py-2 border-b border-gray-50">📸 Studio Photo</a>
     ```

---

## 5. Où et comment changer l'URL du site Studio à l'avenir

L'adresse du studio externe est **centralisée en un seul endroit** dans le fichier [`config/site.js`](file:///Users/gregphotographe/Sites/Photo%20Identite%20Be%CC%81be%CC%81%20Domicile%20.fr/config/site.js) (lignes 3 à 8) :

```javascript
// config/site.js
const siteConfig = {
  studio: {
    name: "Greg Studio Photo",
    url: "https://www.gregstudiophoto.fr/", // <-- MODIFIER ICI L'URL POUR TOUT LE SITE
    address: "16 bd Carnot, 93330 Neuilly-sur-Marne"
  },
  ...
};
```

### Comportement automatique :
* Dès que la variable `url` est modifiée dans `config/site.js`, la routine JavaScript met à jour automatiquement tous les liens marqués `data-studio-link` au chargement de la page.
* Les attributs de sécurité et d'accessibilité sont pré-configurés : `target="_blank"`, `rel="noopener noreferrer"` et `aria-label`.
* Texte exact affiché :  
  *« Vous préférez venir en studio ? Voir les tarifs sur Greg Studio Photo → »*

---

## 6. Ce qui a été rigoureusement préservé

1. **Design System & Tokens :**
   * Palette officielle : couleur primaire `#e67000` (`brand`), fond sombre `#1a1a1a` (`dark`), fond doux `#faf8f5` (`light`).
   * Polices de caractères : *Inter* (sans-serif) et *Playfair Display* (serif).
   * Animations Tailwind : `ken-burns` (zoom d'arrière-plan), `fade-in-up` (apparition au défilement), `float` (flottement léger).
2. **Moteur mathématique de calcul (`simulator.js`) :**
   * Zéro modification de la logique financière.
   * Tarification de base (59 € à Neuilly-sur-Marne, déplacement offert).
   * Forfaits postaux directs intacts (Chelles 75 €, Noisy-le-Grand 75 €, Montreuil 89 €, Aulnay-sous-Bois 89 €).
   * Calcul d'itinéraire temps/distance en temps réel via l'API OSRM avec arrondi commercial aux 5 € supérieurs et majoration Paris intra-muros (+30 €).
3. **Tunnels de conversion & CRM :**
   * Tunnel WhatsApp avec génération du récapitulatif détaillé pré-rempli.
   * Formulaire modal connecté en POST à Fotostudio CRM (`/f/f69154aabb2ef71649b1d57fde2b3c14`).
4. **Référencement naturel (SEO) & Données structurées :**
   * Schémas JSON-LD `LocalBusiness`, `FAQPage`, `HowTo` conservés intacts.
   * Maillage interne des villes prioritaires d'Île-de-France (93, 94, 75, 77) préservé dans le footer.
5. **Responsive & Accessibilité (A11y) :**
   * Sticky mobile bar opérationnelle sur smartphone (< 640px) avec affichage du prix dynamique en direct.
   * Ratios de contrastes validés WCAG AA et attributs `aria-hidden` sur tous les éléments masqués.

---

## 7. Points d'attention & Prochaines étapes éventuelles

1. **Vérification en production :**  
   Lors du déploiement Vercel, tester la saisie d'une commune dans le champ d'adresse pour s'assurer que l'API publique OSRM répond rapidement sans blocage réseau.
2. **Harmonisation globale achevée :**  
   L'ensemble des pages d'atterrissage régionales, thématiques (`photo-identite-a-domicile-ile-de-france.html`, `prix-photo-identite.html`, `photo-identite-bebe-ile-de-france.html`, `photographe-agree-ants-ile-de-france.html`) et locales (`villes/*.html`) bénéficient désormais d'une cohérence totale : simulateur domicile natif, retrait du lien de nav studio, et présence de la passerelle externe discrète vers le studio.
3. **Suivi des conversions (Analytics) :**  
   Le tag Google Analytics 4 (`G-ZQZSLDSMLZ`) est en place et mesurera l'impact positif de la clarification de l'offre (diminution du taux de rebond lié à l'incompréhension des tarifs et augmentation des prises de contact WhatsApp / devis).
