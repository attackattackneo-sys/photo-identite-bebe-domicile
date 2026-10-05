// tracker.js - Instrumentation centralisée des événements de conversion GA4
(function() {
  function sendEvent(eventName, params) {
    if (typeof window.gtag === 'function') {
      params = params || {};
      params.transport_type = 'beacon';
      window.gtag('event', eventName, params);
      // Log utile en développement
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('[GA4 Tracker]', eventName, params);
      }
    }
  }

  window.trackGAEvent = sendEvent;

  // Hook global pour le simulateur de tarif
  var _lastEstimateSignature = '';
  window.trackSimulatorEstimate = function(city, postal, price, distance, duration) {
    var signature = [city, postal, price].join('-');
    if (signature === _lastEstimateSignature) return; // Évite les doublons
    _lastEstimateSignature = signature;

    sendEvent('simulator_estimate', {
      'calculated_city': city || 'Neuilly-sur-Marne',
      'postal_code': postal || '93330',
      'price_eur': price,
      'distance_km': distance ? parseFloat(distance.toFixed(1)) : 0,
      'duration_min': duration || 0,
      'page_path': window.location.pathname
    });
  };

  // Hook global pour la conversion formulaire lead
  window.trackGenerateLead = function(form) {
    var zipInput = form ? form.querySelector('input[name*="zipcode"]') : null;
    var cityInput = form ? form.querySelector('input[name*="city"]') : null;
    sendEvent('generate_lead', {
      'session_type': 'domicile',
      'lead_source': 'modal_fotostudio',
      'postal_code': zipInput ? zipInput.value : '',
      'city': cityInput ? cityInput.value : '',
      'page_path': window.location.pathname
    });
  };

  document.addEventListener('DOMContentLoaded', function() {
    // 1. Détection des clics sur les numéros de téléphone (tel:)
    document.addEventListener('click', function(e) {
      var link = e.target.closest ? e.target.closest('a[href^="tel:"]') : null;
      if (link) {
        var location = link.closest('#main-nav') ? 'header' :
                       link.closest('#mobile-menu') ? 'mobile_menu' :
                       link.closest('#zones') || link.closest('footer') ? 'footer' :
                       link.closest('.fixed.bottom-0') ? 'sticky_bar' : 'body';
        sendEvent('click_phone', {
          'link_url': link.href,
          'button_location': location,
          'page_path': window.location.pathname
        });
      }
    });

    // 2. Détection des clics sur WhatsApp (wa.me)
    document.addEventListener('click', function(e) {
      var link = e.target.closest ? e.target.closest('a[href*="wa.me"]') : null;
      if (link) {
        var location = link.closest('.fixed.bottom-0') ? 'sticky_bar' :
                       link.closest('#mobile-menu') ? 'mobile_menu' :
                       link.closest('#zones') || link.closest('footer') ? 'footer' : 'body';
        sendEvent('click_whatsapp', {
          'link_url': link.href,
          'button_location': location,
          'page_path': window.location.pathname
        });
      }
    });

    // 3. Détection des clics sur SMS (sms:)
    document.addEventListener('click', function(e) {
      var link = e.target.closest ? e.target.closest('a[href^="sms:"]') : null;
      if (link) {
        sendEvent('click_sms', {
          'link_url': link.href,
          'page_path': window.location.pathname
        });
      }
    });

    // 4. Détection globale de soumission de formulaire valide (generate_lead)
    document.addEventListener('submit', function(e) {
      var form = e.target;
      if (form && (form.id === 'lead-booking-form' || form.closest('#booking-modal') || form.getAttribute('action') || form.getAttribute('data-action'))) {
        window.trackGenerateLead(form);
      }
    });
  });
})();
