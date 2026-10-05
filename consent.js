// consent.js - Gestionnaire de consentement ultra-léger (Google Consent Mode v2)
(function() {
  var CONSENT_KEY = 'cookie_consent_status';

  function initConsentBanner() {
    var storedConsent = localStorage.getItem(CONSENT_KEY);

    // Si déjà accepté
    if (storedConsent === 'granted') {
      if (typeof window.gtag === 'function') {
        window.gtag('consent', 'update', {
          'analytics_storage': 'granted'
        });
      }
      return;
    }

    // Si déjà refusé
    if (storedConsent === 'denied') {
      if (typeof window.gtag === 'function') {
        window.gtag('consent', 'update', {
          'analytics_storage': 'denied'
        });
      }
      return;
    }

    // Afficher le bandeau de consentement
    var banner = document.createElement('div');
    banner.id = 'consent-banner';
    banner.className = 'fixed bottom-20 sm:bottom-4 left-4 right-4 sm:left-auto sm:right-4 sm:max-w-md z-50 bg-white/95 backdrop-blur-md border border-gray-200 rounded-2xl p-4 shadow-2xl text-xs text-gray-700 transition-all duration-300 animate-fade-in-up';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Gestion des cookies');
    banner.innerHTML = [
      '<div class="flex items-start gap-3">',
      '  <div class="text-xl">🍪</div>',
      '  <div class="flex-1 leading-relaxed">',
      '    <p class="font-bold text-gray-900 mb-1">Respect de votre vie privée</p>',
      '    <p class="text-gray-600 mb-3">Nous utilisons des cookies anonymisés pour mesurer l\'audience de notre site et améliorer votre expérience de prise de rendez-vous. <a href="/confidentialite.html" class="text-brand underline hover:text-orange-600">En savoir plus</a>.</p>',
      '    <div class="flex items-center gap-2">',
      '      <button type="button" id="consent-btn-accept" class="bg-brand hover:bg-orange-600 text-white font-bold px-3.5 py-2 rounded-xl transition shadow-sm text-xs min-h-[38px]">Accepter</button>',
      '      <button type="button" id="consent-btn-deny" class="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium px-3.5 py-2 rounded-xl transition text-xs min-h-[38px]">Continuer sans accepter</button>',
      '    </div>',
      '  </div>',
      '</div>'
    ].join('\n');

    document.body.appendChild(banner);

    var acceptBtn = document.getElementById('consent-btn-accept');
    var denyBtn = document.getElementById('consent-btn-deny');

    if (acceptBtn) {
      acceptBtn.addEventListener('click', function() {
        localStorage.setItem(CONSENT_KEY, 'granted');
        if (typeof window.gtag === 'function') {
          window.gtag('consent', 'update', {
            'analytics_storage': 'granted'
          });
        }
        banner.remove();
      });
    }

    if (denyBtn) {
      denyBtn.addEventListener('click', function() {
        localStorage.setItem(CONSENT_KEY, 'denied');
        if (typeof window.gtag === 'function') {
          window.gtag('consent', 'update', {
            'analytics_storage': 'denied'
          });
        }
        banner.remove();
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initConsentBanner);
  } else {
    initConsentBanner();
  }
})();
