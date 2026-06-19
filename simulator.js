// Coordinates of Greg Studio in Neuilly-sur-Marne
const STUDIO_COORDS = { lat: 48.8569, lon: 2.5317 };

// Original financial config structure
const config = {
    "priceStudio": 59, // Baseline price for at-home setups
    "localMaxKm": 5,
    "localMaxMin": 10,
    "priceLocal": 79,
    "localExtraKmPrice": 2,
    "localExtraMinPrice": 1,
    "metroMaxKm": 10,
    "metroMaxMin": 15,
    "priceMetro": 95,
    "metroExtraKmPrice": 2,
    "metroExtraMinPrice": 1,
    "extendedMaxKm": 13,
    "extendedMaxMin": 30,
    "priceExtended": 129,
    "parisSupplement": 35,
    "extendedExtraKmPrice": 1.5,
    "extendedExtraMinPrice": 0.5,
    "priceBaby": 15,
    "priceExtraPers": 15,
    "priceAnts": 5,
    "postalPrices": {
        "77500": 95,
        "93160": 95
    }
};

// System states
let state = {
    locationType: 'studio', // 'studio' or 'home'
    calculatedTravelCost: 0,
    calculatedTravelZone: "Neuilly-sur-Marne (93330)",
    detectedDistance: 0,
    detectedDuration: 0,
    detectedPostal: "93330",
    detectedCity: "Neuilly-sur-Marne",
    participants: [
        { id: 1, type: 'classic' } // profiles: 'classic', 'ants', 'visa', 'baby', 'newborn'
    ]
};

let participantCounter = 1;
let searchTimeout = null;

// Custom profiles studio rates mapping
const profiles = {
    classic: { label: "Adulte/Enfant +3 ans (Classique)", price: 10, optionCost: 0, desc: "Planche de 6 photos" },
    ants: { label: "Adulte/Enfant +3 ans (ANTS)", price: 15, optionCost: 5, desc: "Planche + Code e-photo" },
    visa: { label: "Visas Internationaux (USA, etc.)", price: 15, optionCost: 5, desc: "Format 5x5 cm / Spécifique" },
    baby: { label: "Bébé (1 à 3 mois)", price: 25, optionCost: 15, desc: "Séance adaptée de 10-20 min" },
    newborn: { label: "Nourrisson (3 jours à 1 mois)", price: 30, optionCost: 20, desc: "Séance ultra-douce de 30 min" }
};

function scrollToSimulator() {
    const el = document.getElementById('booking-funnel');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
}

// Switch location format (Studio vs. Domicile)
function selectLocationType(type) {
    state.locationType = type;
    
    const btnStudio = document.getElementById('btn-loc-studio');
    const btnHome = document.getElementById('btn-loc-home');
    const travelPanel = document.getElementById('travel-panel');
    const travelRow = document.getElementById('recap-travel-row');

    if (!btnStudio || !btnHome) return;

    if (type === 'studio') {
        btnStudio.className = "py-4 px-3 rounded-2xl border transition text-center focus:outline-none flex flex-col items-center justify-center gap-1.5 active:scale-95 border-brand bg-orange-50 text-dark";
        btnHome.className = "py-4 px-3 rounded-2xl border transition text-center focus:outline-none flex flex-col items-center justify-center gap-1.5 active:scale-95 border-gray-200 bg-white text-gray-400 hover:border-brand";
        if (travelPanel) travelPanel.classList.add('hidden');
        if (travelRow) travelRow.classList.add('hidden');
    } else {
        btnHome.className = "py-4 px-3 rounded-2xl border transition text-center focus:outline-none flex flex-col items-center justify-center gap-1.5 active:scale-95 border-brand bg-orange-50 text-dark";
        btnStudio.className = "py-4 px-3 rounded-2xl border transition text-center focus:outline-none flex flex-col items-center justify-center gap-1.5 active:scale-95 border-gray-200 bg-white text-gray-400 hover:border-brand";
        if (travelPanel) travelPanel.classList.remove('hidden');
        if (travelRow) travelRow.classList.remove('hidden');
    }
    renderParticipantsUI();
    runIDCalculation();
}

// Address Autocomplete Debounce Trigger
function debounceSearch(query) {
    clearTimeout(searchTimeout);
    const clearBtn = document.getElementById('clear-search-btn');
    
    if (!query || query.trim().length < 3) {
        document.getElementById('autocomplete-results').classList.add('hidden');
        if (clearBtn) clearBtn.classList.add('hidden');
        return;
    }
    
    if (clearBtn) clearBtn.classList.remove('hidden');
    searchTimeout = setTimeout(() => {
        fetchAddressSuggestions(query);
    }, 450);
}

// Clear Address Field
function clearAddressSearch() {
    const input = document.getElementById('address-input');
    if (input) input.value = '';
    document.getElementById('autocomplete-results').classList.add('hidden');
    const clearBtn = document.getElementById('clear-search-btn');
    if (clearBtn) clearBtn.classList.add('hidden');
    document.getElementById('route-calc-info').classList.add('hidden');
    
    // Reset to Neuilly defaults
    state.detectedDistance = 0;
    state.detectedDuration = 0;
    state.detectedPostal = "93330";
    state.detectedCity = "Neuilly-sur-Marne";
    runIDCalculation();
}

// Fetch Address Nominatim OpenStreetMap (Limited to Île-de-France)
async function fetchAddressSuggestions(query) {
    const loading = document.getElementById('address-loading');
    const resultsBox = document.getElementById('autocomplete-results');
    
    if (loading) loading.classList.remove('hidden');
    
    try {
        // Focus search exclusively to Île-de-France region, France
        const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&viewbox=1.4,49.2,3.6,48.1&bounded=1&format=json&addressdetails=1&limit=5&countrycodes=fr`;
        const response = await fetch(url, {
            headers: { 'Accept-Language': 'fr' }
        });
        const data = await response.json();
        
        if (!resultsBox) return;
        resultsBox.innerHTML = '';
        
        if (data && data.length > 0) {
            data.forEach(item => {
                const div = document.createElement('div');
                div.className = "p-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition text-dark";
                
                // Parse name cleanly
                const displayName = item.display_name.split(',').slice(0, 3).join(',');
                const postcode = item.address.postcode || "";
                const city = item.address.city || item.address.town || item.address.village || item.address.suburb || "";
                
                div.innerText = `${displayName} (${postcode})`;
                div.onclick = () => selectAddress(item.lat, item.lon, city, postcode, displayName);
                resultsBox.appendChild(div);
            });
            resultsBox.classList.remove('hidden');
        } else {
            resultsBox.innerHTML = `<div class="p-3 text-gray-400 italic">Aucune ville correspondante en IDF</div>`;
            resultsBox.classList.remove('hidden');
        }
    } catch (err) {
        console.error("Geocoding Error:", err);
    } finally {
        if (loading) loading.classList.add('hidden');
    }
}

// Handle selected autocomplete item
async function selectAddress(lat, lon, city, postcode, displayName) {
    document.getElementById('autocomplete-results').classList.add('hidden');
    const addrInput = document.getElementById('address-input');
    if (addrInput) addrInput.value = displayName;
    
    const infoBox = document.getElementById('route-calc-info');
    if (!infoBox) return;
    infoBox.classList.remove('hidden');
    infoBox.innerHTML = `
        <div class="flex items-center gap-2 text-gray-500">
            <svg class="animate-spin h-4 w-4 text-brand" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Calcul de l'itinéraire le plus rapide en cours...</span>
        </div>
    `;

    try {
        // Calculate real road distance and time via OSRM API (No keys required, reliable open routing)
        const routeUrl = `https://router.project-osrm.org/route/v1/driving/${STUDIO_COORDS.lon},${STUDIO_COORDS.lat};${lon},${lat}?overview=false`;
        const response = await fetch(routeUrl);
        const routeData = await response.json();

        if (routeData && routeData.routes && routeData.routes.length > 0) {
            const route = routeData.routes[0];
            const distanceKm = route.distance / 1000; // Meters to Kilometers
            const durationMin = Math.ceil(route.duration / 60); // Seconds to Minutes

            state.detectedDistance = distanceKm;
            state.detectedDuration = durationMin;
            state.detectedPostal = postcode || "75000";
            state.detectedCity = city || "Paris";

            // Update UI info badge
            infoBox.innerHTML = `
                <div class="flex items-center justify-between text-dark">
                    <div class="flex items-center gap-1.5 font-semibold">
                        <i data-lucide="navigation" class="w-4 h-4 text-brand"></i>
                        <span>Itinéraire trouvé : ${distanceKm.toFixed(1)} km &bull; ~${durationMin} min</span>
                    </div>
                    <span class="text-[9px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded uppercase">Calculé</span>
                </div>
                <p class="text-[10px] text-gray-400 mt-1">Trajet calculé par la route au départ de Neuilly-sur-Marne (93330).</p>
            `;
            if (window.lucide) window.lucide.createIcons();
        } else {
            // Fallback to straight line (Haversine) calculation if routing service is offline
            const dist = calculateHaversine(STUDIO_COORDS.lat, STUDIO_COORDS.lon, parseFloat(lat), parseFloat(lon));
            const estDur = Math.ceil(dist * 2.2); // Approximate standard Paris traffic ratio

            state.detectedDistance = dist;
            state.detectedDuration = estDur;
            state.detectedPostal = postcode || "75000";
            state.detectedCity = city || "Paris";

            infoBox.innerHTML = `
                <div class="flex items-center justify-between text-dark">
                    <div class="flex items-center gap-1.5 font-semibold">
                        <i data-lucide="navigation" class="w-4 h-4 text-brand"></i>
                        <span>Itinéraire estimé : ${dist.toFixed(1)} km &bull; ~${estDur} min</span>
                    </div>
                    <span class="text-[9px] bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded uppercase">Estimé</span>
                </div>
            `;
            if (window.lucide) window.lucide.createIcons();
        }
    } catch (err) {
        console.error("OSRM Route Engine Error, falling back:", err);
        // Simple straight-line fallback to ensure zero pricing interruptions
        const dist = calculateHaversine(STUDIO_COORDS.lat, STUDIO_COORDS.lon, parseFloat(lat), parseFloat(lon));
        const estDur = Math.ceil(dist * 2);
        state.detectedDistance = dist;
        state.detectedDuration = estDur;
        state.detectedPostal = postcode || "75000";
        state.detectedCity = city || "Paris";
        
        infoBox.innerHTML = `
            <div class="flex items-center justify-between text-dark">
                <div class="flex items-center gap-1.5 font-semibold">
                    <i data-lucide="navigation" class="w-4 h-4 text-brand"></i>
                    <span>Itinéraire estimé : ${dist.toFixed(1)} km &bull; ~${estDur} min</span>
                </div>
                <span class="text-[9px] bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded uppercase">Estimé</span>
            </div>
        `;
        if (window.lucide) window.lucide.createIcons();
    }

    runIDCalculation();
}

// Math auxiliary for Haversine fallback distance
function calculateHaversine(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth km radius
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Multi-people managers
function addParticipant() {
    participantCounter++;
    state.participants.push({ id: participantCounter, type: 'classic' });
    renderParticipantsUI();
    runIDCalculation();
}

// Remove Participant
function removeParticipant(id) {
    if (state.participants.length <= 1) return;
    state.participants = state.participants.filter(p => p.id !== id);
    renderParticipantsUI();
    runIDCalculation();
}

function handleParticipantTypeChange(id, newType) {
    const index = state.participants.findIndex(p => p.id === id);
    if (index !== -1) {
        state.participants[index].type = newType;
    }
    runIDCalculation();
}

// Render input blocks for every person
function renderParticipantsUI() {
    const container = document.getElementById('participants-list');
    if (!container) return;
    container.innerHTML = '';

    state.participants.forEach((p, index) => {
        const div = document.createElement('div');
        div.className = "flex items-center justify-between p-3 rounded-xl bg-white border border-gray-150 gap-3 shadow-sm";
        
        let selectOptions = '';
        for (const [key, value] of Object.entries(profiles)) {
            const isSelected = p.type === key ? 'selected' : '';
            selectOptions += `<option value="${key}" ${isSelected}>${value.label}</option>`;
        }

        div.innerHTML = `
            <div class="flex items-center gap-2.5 grow">
                <span class="w-5.5 h-5.5 rounded-full bg-orange-50 text-brand font-extrabold text-[10px] flex items-center justify-center shrink-0 border border-brand/20">
                    ${index + 1}
                </span>
                <div class="grow">
                    <select onchange="handleParticipantTypeChange(${p.id}, this.value)" class="w-full bg-gray-50 border border-gray-200 rounded-lg p-2 text-xs text-dark focus:outline-none focus:border-brand">
                        ${selectOptions}
                    </select>
                </div>
            </div>
            ${state.participants.length > 1 ? `
                <button type="button" onclick="removeParticipant(${p.id})" class="text-red-400 hover:text-red-500 p-1.5 transition shrink-0">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
            ` : ''}
        `;
        container.appendChild(div);
    });
    if (window.lucide) window.lucide.createIcons();
}

// Core Mathematical Calculation Engine
function runIDCalculation() {
    let finalPrice = 0;
    let travelCost = 0;
    let travelZoneName = "";

    const recapPeopleList = document.getElementById('recap-people-list');
    if (!recapPeopleList) return;
    recapPeopleList.innerHTML = '';

    if (state.locationType === 'studio') {
        document.getElementById('recap-location-type').innerText = "Au Studio (Neuilly-sur-Marne)";
        
        state.participants.forEach((p) => {
            const profile = profiles[p.type];
            finalPrice += profile.price;
            
            const pLine = document.createElement('div');
            pLine.className = "flex justify-between items-baseline text-gray-600";
            pLine.innerHTML = `<span>👤 ${profile.label} :</span> <strong class="text-dark">${profile.price.toFixed(2).replace('.', ',')} €</strong>`;
            recapPeopleList.appendChild(pLine);
        });

    } else {
        document.getElementById('recap-location-type').innerText = "À Domicile (Chez vous)";

        const firstParticipant = state.participants[0];
        const firstProfile = profiles[firstParticipant.type];
        
        // Base cost at domicile is 59€
        finalPrice += config.priceStudio; 

        const firstLine = document.createElement('div');
        firstLine.className = "flex justify-between items-baseline text-gray-600";
        if (firstProfile.optionCost > 0) {
            firstLine.innerHTML = `<span>👤 Prise de vue principale (${firstProfile.label}) :</span> <strong class="text-dark">59,00 € <span class="text-brand">+${firstProfile.optionCost.toFixed(2).replace('.', ',')} €</span></strong>`;
            finalPrice += firstProfile.optionCost;
        } else {
            firstLine.innerHTML = `<span>👤 Prise de vue principale (${firstProfile.label}) :</span> <strong class="text-dark">59,00 €</strong>`;
        }
        recapPeopleList.appendChild(firstLine);

        // For extra people beyond the first one
        if (state.participants.length > 1) {
            for (let i = 1; i < state.participants.length; i++) {
                const nextPart = state.participants[i];
                const nextProfile = profiles[nextPart.type];
                
                let personCost = config.priceExtraPers + nextProfile.optionCost; // 15€ + specific profile cost
                finalPrice += personCost;

                const line = document.createElement('div');
                line.className = "flex justify-between items-baseline text-gray-600";
                line.innerHTML = `<span>👤 Personne sup. (${nextProfile.label}) :</span> <strong class="text-dark">${personCost.toFixed(2).replace('.', ',')} €</strong>`;
                recapPeopleList.appendChild(line);
            }
        }

        // Domicile travel calculations based on GPS detected coordinates
        const normalizedCity = state.detectedCity.toLowerCase();
        const normalizedPostal = state.detectedPostal;

        if (normalizedCity.includes("neuilly-sur-marne") || normalizedPostal === "93330" || state.detectedDistance === 0) {
            // Neuilly-sur-Marne has 0€ travel supplement! Total base = 59€
            travelCost = 0;
            travelZoneName = "Neuilly-sur-Marne (93330)";
        } else if (normalizedPostal === "77500") {
            travelCost = config.postalPrices["77500"] - config.priceStudio; // 95 - 59 = 36€
            travelZoneName = "Chelles (77500) - Forfait Direct";
        } else if (normalizedPostal === "93160") {
            travelCost = config.postalPrices["93160"] - config.priceStudio; // 95 - 59 = 36€
            travelZoneName = "Noisy-le-Grand (93160) - Forfait Direct";
        } else {
            // General algorithm matching Greg's original vercel app config rules
            let calculatedBase = config.priceLocal; // default 79€ starting local
            let currentIsParis = normalizedPostal.startsWith("75") || normalizedCity.includes("paris");

            if (state.detectedDistance <= config.localMaxKm && state.detectedDuration <= config.localMaxMin) {
                calculatedBase = config.priceLocal;
                let extraKm = Math.max(0, state.detectedDistance - config.localMaxKm);
                let extraMin = Math.max(0, state.detectedDuration - config.localMaxMin);
                calculatedBase += (extraKm * config.localExtraKmPrice) + (extraMin * config.localExtraMinPrice);
            } else if (state.detectedDistance <= config.metroMaxKm && state.detectedDuration <= config.metroMaxMin) {
                calculatedBase = config.priceMetro;
                let extraKm = Math.max(0, state.detectedDistance - config.metroMaxKm);
                let extraMin = Math.max(0, state.detectedDuration - config.metroMaxMin);
                calculatedBase += (extraKm * config.metroExtraKmPrice) + (extraMin * config.metroExtraMinPrice);
            } else {
                calculatedBase = config.priceExtended;
                let extraKm = Math.max(0, state.detectedDistance - config.extendedMaxKm);
                let extraMin = Math.max(0, state.detectedDuration - config.extendedMaxMin);
                calculatedBase += (extraKm * config.extendedExtraKmPrice) + (extraMin * config.extendedExtraMinPrice);
            }

            if (currentIsParis) {
                calculatedBase += config.parisSupplement;
            }

            travelCost = calculatedBase - config.priceStudio;
            travelZoneName = `${state.detectedCity} (${state.detectedDistance.toFixed(1)} km / ${state.detectedDuration} min)`;
        }

        finalPrice += travelCost;

        document.getElementById('recap-travel-zone').innerText = travelZoneName;
        document.getElementById('recap-travel-price').innerText = travelCost === 0 ? "Offert" : `+${travelCost.toFixed(2).replace('.', ',')} €`;
    }

    const formattedTotal = `${finalPrice.toFixed(2).replace('.', ',')} €`;
    document.getElementById('total-price').innerText = formattedTotal;
    document.getElementById('sticky-price').innerText = formattedTotal;

    // Render buttons layout dynamically based on state
    renderCheckoutButtons();
}

// Render action buttons based on selected Studio vs Domicile location
function renderCheckoutButtons() {
    const container = document.getElementById('action-buttons-container');
    if (!container) return;
    container.innerHTML = '';

    if (state.locationType === 'studio') {
        // STUDIO TUNNELS: Official online booking
        container.innerHTML = `
            <a href="https://www.fotostudio.io/client/res/gregphotographe-fr" target="_blank" class="w-full bg-brand hover:bg-orange-600 active:scale-98 text-white font-bold py-3.5 rounded-xl transition flex items-center justify-center gap-2 text-xs shadow-md shadow-brand/10 min-h-[44px]">
                <i data-lucide="calendar" class="w-4 h-4 shrink-0"></i> Réserver en ligne au Studio
            </a>
            <button type="button" onclick="triggerWhatsAppBooking()" class="w-full bg-[#25D366] hover:bg-[#20ba59] active:scale-98 text-white font-bold py-3 rounded-xl transition flex items-center justify-center gap-2 text-xs shadow-sm min-h-[44px]">
                <i data-lucide="message-square" class="w-4 h-4 shrink-0"></i> Poser une question sur WhatsApp
            </button>
        `;
    } else {
        // DOMICILE TUNNELS: WhatsApp & Dynamic lead Form popup
        container.innerHTML = `
            <button type="button" onclick="triggerWhatsAppBooking()" class="w-full bg-[#25D366] hover:bg-[#20ba59] active:scale-98 text-white font-bold py-3.5 rounded-xl transition flex items-center justify-center gap-2 text-xs shadow-md shadow-emerald-600/10 min-h-[44px]">
                <i data-lucide="message-square" class="w-4 h-4 shrink-0"></i> Réserver par WhatsApp (Rapide)
            </button>
            <button type="button" onclick="openBookingModal()" class="w-full bg-brand hover:bg-orange-600 active:scale-98 text-white font-bold py-3 rounded-xl transition flex items-center justify-center gap-2 text-xs shadow-sm min-h-[44px]">
                <i data-lucide="calendar" class="w-4 h-4 shrink-0"></i> Faire une demande de créneau
            </button>
        `;
    }
    if (window.lucide) window.lucide.createIcons();
}

// Summary builder text with exact breakdown details for both Studio & Home prices
function getSummaryText() {
    let text = `Simulation Photo d'Identité :\n`;
    if (state.locationType === 'studio') {
        text += `- Lieu : Au Studio (Neuilly-sur-Marne)\n`;
        text += `- Nombre de sujets : ${state.participants.length}\n`;
        state.participants.forEach((p, idx) => {
            const profile = profiles[p.type];
            text += `  • Sujet ${idx + 1} : ${profile.label} ➔ ${profile.price},00 €\n`;
        });
    } else {
        let zone = document.getElementById('recap-travel-zone').innerText;
        let zonePrice = document.getElementById('recap-travel-price').innerText;
        text += `- Lieu : À Domicile (Chez vous)\n`;
        text += `- Déplacement : ${zone} (${zonePrice})\n`;
        if (state.detectedDistance > 0) {
            text += `- Itinéraire GPS : ${state.detectedDistance.toFixed(1)} km (~${state.detectedDuration} min)\n`;
        }
        text += `- Nombre de sujets : ${state.participants.length}\n`;
        
        // First participant
        const firstProfile = profiles[state.participants[0].type];
        text += `  • Sujet 1 (Principal) : ${firstProfile.label} ➔ 59,00 €${firstProfile.optionCost > 0 ? ` (+ option ${firstProfile.optionCost},00 €)` : ''}\n`;
        
        // Extra participants
        if (state.participants.length > 1) {
            for (let i = 1; i < state.participants.length; i++) {
                const nextProfile = profiles[state.participants[i].type];
                let personCost = config.priceExtraPers + nextProfile.optionCost;
                text += `  • Sujet ${i + 1} (Supplémentaire) : ${nextProfile.label} ➔ ${personCost},00 €\n`;
            }
        }
    }

    const total = document.getElementById('total-price').innerText;
    text += `\n=== TOTAL NET ESTIMÉ : ${total} ===`;
    return text;
}

// Open Fotostudio Modal
function openBookingModal() {
    const modal = document.getElementById('booking-modal');
    const messageArea = document.getElementById('form-message');
    const projectSelect = document.getElementById('form-project-type');

    if (!modal) return;
    
    // Prefill message body with calculated quote details automatically
    if (messageArea) {
        messageArea.value = `Bonjour Greg,\nJe vous contacte suite à ma simulation sur votre outil d'estimation en ligne. Voici les détails de mes besoins :\n\n${getSummaryText()}\n\nMerci de me recontacter pour bloquer une date.`;
    }
    
    // Map travel inputs to form address if possible
    const formZip = document.getElementById('form-zipcode');
    const formCity = document.getElementById('form-city');

    if (formZip) formZip.value = state.detectedPostal || "";
    if (formCity) formCity.value = state.detectedCity || "";

    // Mapped CRM Session Type selection automatically
    if (projectSelect) {
        if (state.locationType === 'studio') {
            projectSelect.value = "34544"; // Studio Id
        } else {
            projectSelect.value = "241706"; // Domicile Id
        }
    }

    modal.classList.remove('hidden');
}

function closeBookingModal() {
    const modal = document.getElementById('booking-modal');
    if (modal) modal.classList.add('hidden');
}

// Booking on WhatsApp
function triggerWhatsAppBooking() {
    const bodyText = encodeURIComponent(
        `Bonjour Greg, je souhaite réserver une séance d'identité ${state.locationType === 'studio' ? 'au studio' : 'à domicile'}.\n\n` +
        getSummaryText() +
        `\n\nMerci de me recontacter pour bloquer la date de passage.`
    );
    window.location.href = `https://wa.me/33781757754?text=${bodyText}`;
}

document.addEventListener('DOMContentLoaded', () => {
    const nav = document.getElementById('main-nav') || document.querySelector('nav');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    // Navbar dynamique avec gestion du contraste
    if (nav && !nav.dataset.bound) {
        nav.dataset.bound = "true";
        const navLinksContainer = nav.querySelector('.nav-links-container');
        const logoText = nav.querySelector('.logo-text');
        const logoImg = nav.querySelector('.logo-img');

        const updateNavScroll = () => {
            if (window.scrollY > 20) {
                nav.classList.add('bg-white/95', 'backdrop-blur-md', 'shadow-lg', 'py-2');
                nav.classList.remove('bg-transparent', 'py-6', 'shadow-none');
                
                if (navLinksContainer) {
                    navLinksContainer.classList.add('text-gray-800');
                    navLinksContainer.classList.remove('text-white/90');
                }
                if (logoText) {
                    logoText.classList.add('text-dark');
                    logoText.classList.remove('text-white');
                }
                if (logoImg) {
                    logoImg.classList.remove('brightness-0', 'invert');
                }
                if (mobileMenuBtn) {
                    mobileMenuBtn.classList.add('text-gray-800');
                    mobileMenuBtn.classList.remove('text-white');
                }
            } else {
                nav.classList.remove('bg-white/95', 'backdrop-blur-md', 'shadow-lg', 'py-2');
                nav.classList.add('bg-transparent', 'py-6', 'shadow-none');
                
                if (navLinksContainer) {
                    navLinksContainer.classList.remove('text-gray-800');
                    navLinksContainer.classList.add('text-white/90');
                }
                if (logoText) {
                    logoText.classList.remove('text-dark');
                    logoText.classList.add('text-white');
                }
                if (logoImg) {
                    logoImg.classList.add('brightness-0', 'invert');
                }
                if (mobileMenuBtn) {
                    mobileMenuBtn.classList.remove('text-gray-800');
                    mobileMenuBtn.classList.add('text-white');
                }
            }
        };

        window.addEventListener('scroll', updateNavScroll);
        updateNavScroll();
    }

    // Menu Mobile
    if (mobileMenuBtn && mobileMenu && !mobileMenuBtn.dataset.bound) {
        mobileMenuBtn.dataset.bound = "true";
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Bouton retour en haut (Back to Top)
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn && !backToTopBtn.dataset.bound) {
        backToTopBtn.dataset.bound = "true";
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                backToTopBtn.classList.remove('opacity-0', 'invisible');
                backToTopBtn.classList.add('opacity-100', 'visible');
              } else {
                backToTopBtn.classList.add('opacity-0', 'invisible');
                backToTopBtn.classList.remove('opacity-100', 'visible');
            }
        });
        
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Intersection Observer pour les animations au défilement
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                entry.target.style.opacity = 1;
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));

    // Init Simulator reading dynamic config attributes from container
    const funnel = document.getElementById('booking-funnel');
    if (funnel) {
        const defaultLoc = funnel.getAttribute('data-default-location') || 'studio';
        const defaultCity = funnel.getAttribute('data-default-city');
        const defaultPostal = funnel.getAttribute('data-default-postal');
        const defaultLat = funnel.getAttribute('data-default-lat');
        const defaultLon = funnel.getAttribute('data-default-lon');

        if (defaultLoc === 'home' && defaultCity && defaultPostal && defaultLat && defaultLon) {
            // First render simple HTML UI
            selectLocationType('home');
            renderParticipantsUI();
            
            // Trigger routing and calculations
            selectAddress(parseFloat(defaultLat), parseFloat(defaultLon), defaultCity, defaultPostal, `${defaultCity} (${defaultPostal})`);
        } else {
            selectLocationType(defaultLoc);
            renderParticipantsUI();
        }
    } else {
        selectLocationType('studio');
        renderParticipantsUI();
    }
});
