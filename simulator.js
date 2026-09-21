// =====================================================================
// CONFIGURATION TARIFAIRE — Version « mixte »
// Grille par zones (simple à afficher au client)
// + moteur de coût réel façon simulateur (protection de la marge)
// =====================================================================
// Principe : le client voit toujours un forfait clair et fixe (comme
// avant). En coulisse, chaque forfait est comparé à un prix plancher
// calculé à partir des coûts réels, pour repérer immédiatement toute
// zone ou tout code postal qui serait devenu non rentable.
// =====================================================================

// ---------------------------------------------------------------------
// 1. PARAMÈTRES DE COÛT RÉEL — à revoir 1x/an (ou si le carburant bouge)
// ---------------------------------------------------------------------
const costParams = {
    // Véhicule
    fuelPricePerL: 1.85,
    consumptionPer100km: 6.5,
    vehicleWearPerKm: 0.15,      // entretien / pneus / assurance au km
    travelTimeValuePerMin: 0.25, // valorisation du temps de trajet

    // Prestation
    equipmentAmortized: 5,
    printingConsumables: 2,
    fixedChargesPerBooking: 40,  // charges fixes annuelles / nb prestations par an

    // Objectifs
    urssafRate: 0.24,            // provision URSSAF / cotisations
    vatRate: 0.20
};

// Calcule le coût réel + le prix plancher HT pour un trajet donné
// (reprend exactement la logique du simulateur : coûts totaux / (1 - URSSAF))
function computeRealFloorPrice(distanceKmRoundTrip, travelTimeMin) {
    const fuel = (distanceKmRoundTrip / 100) * costParams.consumptionPer100km * costParams.fuelPricePerL;
    const wear = distanceKmRoundTrip * costParams.vehicleWearPerKm;
    const travelTimeCost = travelTimeMin * costParams.travelTimeValuePerMin;
    const totalCosts =
        fuel + wear + travelTimeCost +
        costParams.equipmentAmortized +
        costParams.printingConsumables +
        costParams.fixedChargesPerBooking;

    const floorPrice = totalCosts / (1 - costParams.urssafRate);

    return { fuel, wear, travelTimeCost, totalCosts, floorPrice };
}

// ---------------------------------------------------------------------
// 2. GRILLE CLIENT — ce qui s'affiche, ce qui ne change pas souvent
// ---------------------------------------------------------------------
const config = {
    priceStudio: 59, // Prestation sur place, sans déplacement

    // Zones ordonnées du plus proche au plus loin.
    // Règle de bascule explicite : dès que la distance OU la durée
    // dépasse le seuil de la zone, on passe à la zone suivante
    // (le "OR" est volontairement le plus prudent pour la marge —
    //  cf. §5.2 du cahier des charges, point à clarifier historique).
    zoneBreakRule: 'OR',
    zones: [
        { name: 'local',    maxKm: 5,  maxMin: 25, price: 65 },
        { name: 'metro',    maxKm: 10, maxMin: 50, price: 79 },
        { name: 'extended', maxKm: 15, maxMin: 75, price: 129 } // corrigé : 99 + 30 = 129 (l'ancien code annonçait 159 par erreur)
    ],
    parisSupplement: 30, // Appliqué en plus si zone = "extended" ET code postal intra-muros (75xxx)

    // Taux supplémentaires au-delà de la dernière zone — mutualisés
    // (avant : répétés 3 fois avec la même valeur, donc factorisés ici)
    extraKmPrice: 1.5,
    extraMinPrice: 0.75,

    // Multiplicateurs jour/heure, façon tarifs A/B/C/D des taxis.
    // Appliqués sur le prix de zone AVANT toute remise commerciale.
    timeMultipliers: {
        normal:  1,     // Lun-Sam, 8h-20h
        evening: 1.15,  // Lun-Sam, 20h-23h
        sunday:  1.3,   // Dimanche / jours fériés
        urgent:  1.5    // Réservation à moins de 48h
    },

    // Un seul objet, une seule source de vérité pour tous les profils
    // déclarés côté state.participants (avant : 3 profils sur 6 seulement
    // avaient un prix défini)
    participantPrices: {
        classic: 0,
        ants: 5,
        visa: 15,     // ⚠️ à confirmer avec Greg
        toddler: 15,  // ⚠️ à confirmer avec Greg
        baby: 15,
        newborn: 15   // ⚠️ à confirmer avec Greg
    },

    // Forfaits directs par ville : dérogent à la grille de zone.
    // Ils DOIVENT être revalidés chaque année via checkPostalMargins()
    // ci-dessous, car ils ne recalculent jamais leur coût tout seuls.
    postalPrices: {
        "77500": 75, // Chelles
        "93160": 75, // Noisy-le-Grand
        "93100": 89, // Montreuil
        "93600": 89  // Aulnay-sous-Bois
    }
};

// ---------------------------------------------------------------------
// 3. DÉTERMINATION DE ZONE — règle explicite et unique
// ---------------------------------------------------------------------
function determineZone(distanceKm, durationMin) {
    for (const zone of config.zones) {
        const withinKm = distanceKm <= zone.maxKm;
        const withinMin = durationMin <= zone.maxMin;
        const fits = config.zoneBreakRule === 'OR'
            ? (withinKm && withinMin)   // avec la règle OR, il faut être sous LES DEUX seuils pour rester dans la zone
            : (withinKm || withinMin);  // variante plus permissive si jamais souhaitée un jour
        if (fits) return zone;
    }
    return null; // au-delà de toutes les zones -> tarif sur devis (km/min supplémentaires)
}

// ---------------------------------------------------------------------
// 4. FILET DE SÉCURITÉ — jamais facturer sous le prix plancher réel
// ---------------------------------------------------------------------
// À appeler juste avant d'afficher un prix final au client.
// Ne bloque rien automatiquement (le forfait reste affiché tel quel),
// mais renvoie un avertissement exploitable (log, badge admin, etc.)
// si la marge réelle est mangée par un trajet plus coûteux que prévu.
function getFinalPrice(basePrice, distanceKmRoundTrip, travelTimeMin, multiplierKey = 'normal') {
    const { floorPrice } = computeRealFloorPrice(distanceKmRoundTrip, travelTimeMin);
    const multiplier = config.timeMultipliers[multiplierKey] ?? 1;
    const price = basePrice * multiplier;

    return {
        price,
        floorPrice,
        margin: price - floorPrice,
        warning: price < floorPrice
    };
}

// ---------------------------------------------------------------------
// 5. AUDIT ANNUEL DES FORFAITS FIXES PAR CODE POSTAL
// ---------------------------------------------------------------------
// À lancer 1x/an (ou après une hausse du carburant) avec les distances
// réelles mesurées vers chaque ville, pour vérifier que les forfaits
// figés (postalPrices) couvrent toujours le coût réel.
//
// Exemple d'appel :
// checkPostalMargins({
//   "77500": { km: 30, min: 35 },
//   "93160": { km: 12, min: 18 },
//   "93100": { km: 22, min: 28 },
//   "93600": { km: 26, min: 32 }
// });
function checkPostalMargins(postalDistances) {
    const report = {};
    for (const [postal, price] of Object.entries(config.postalPrices)) {
        const dist = postalDistances[postal];
        if (!dist) continue;
        const { floorPrice } = computeRealFloorPrice(dist.km, dist.min);
        report[postal] = {
            price,
            floorPrice: Number(floorPrice.toFixed(2)),
            margin: Number((price - floorPrice).toFixed(2)),
            ok: price >= floorPrice
        };
    }
    return report;
}

// ---------------------------------------------------------------------
// 6. ÉTAT DE L'APPLICATION (inchangé, juste regroupé ici pour référence)
// ---------------------------------------------------------------------
let state = {
    locationType: 'studio', // 'studio' ou 'home'
    calculatedTravelCost: 0,
    calculatedTravelZone: "Neuilly-sur-Marne (93330)",
    detectedDistance: 0,
    detectedDuration: 0,
    detectedPostal: "93330",
    detectedCity: "Neuilly-sur-Marne",
    participants: [
        { id: 1, type: 'classic' }
    ]
};

export {
    config,
    costParams,
    computeRealFloorPrice,
    determineZone,
    getFinalPrice,
    checkPostalMargins,
    state
};
