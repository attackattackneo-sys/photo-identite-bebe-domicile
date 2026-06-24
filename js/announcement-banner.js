// Announcement Banner Component
// Affiche un bandeau d'annonce en haut de la page, au-dessus du header
// Utilise localStorage pour mémoriser la fermeture par l'utilisateur

(function() {
  'use strict';

  // Charger la configuration
  let config = {
    announcement: {
      active: true,
      message: "📸 Fermeture estivale pour congés!\nJe serai en vacances du 16 juillet au 6 août 2026.\nAucune séance photo ne sera programmée pendant cette période.\nJe serai ravi de vous retrouver à partir du lundi 10 août 2026 pour de nouvelles aventures photographiques!\nPour toute demande, vous pouvez me contacter par email, je vous répondrai à mon retour.",
      startDate: "2020-01-01",
      endDate: "2030-08-06",
      showOnAllPages: true,
      backgroundColor: "#e60000",
      textColor: "#ffffff",
      icon: "📸",
      closeButtonColor: "#ffffff"
    },
    infoPageUrl: "informations.html",
    infoLinkText: "En savoir plus"
  };

  // Essayer de charger la config depuis /config/site.js
  function loadConfig() {
    // Dans un contexte navigateur, on ne peut pas faire de require, 
    // donc on vérifie si window.siteConfig existe (inclus via script)
    if (window.siteConfig) {
      config = window.siteConfig;
    }
    return config;
  }

  // Vérifier si le bandeau doit être affiché
  function shouldShowBanner() {
    const announcement = config.announcement;
    
    // Désactivé dans la config
    if (!announcement.active) return false;
    
    // Vérifier si on est dans la période de validité
    const now = new Date();
    const startDate = new Date(announcement.startDate);
    const endDate = new Date(announcement.endDate);
    
    // Si la date de fin est passée, ne pas afficher
    if (now > endDate) return false;
    
    // Si la date de début est dans le futur, ne pas afficher
    if (now < startDate) return false;
    
    // Vérifier si l'utilisateur a fermé le bandeau
    const bannerKey = 'announcement-banner-hidden';
    const hidden = localStorage.getItem(bannerKey);
    if (hidden === 'true') return false;
    
    return true;
  }

  // Créer le bandeau HTML
  function createBanner() {
    const announcement = config.announcement;
    
    // Formater le message avec les retours à la ligne
    const messageLines = announcement.message.split('\n');
    const messageHtml = messageLines.map(line => `<span class="block sm:inline">${line}</span>`).join(' ');
    
    // Créer le bandeau
    const banner = document.createElement('div');
    banner.id = 'announcement-banner';
    banner.className = 'fixed top-0 left-0 right-0 z-60';
    banner.setAttribute('role', 'alert');
    banner.setAttribute('aria-live', 'assertive');
    banner.style.backgroundColor = announcement.backgroundColor;
    banner.style.color = announcement.textColor;
    
    // Contenu du bandeau
    banner.innerHTML = `
      <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between gap-3">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <span class="text-xl" aria-hidden="true">${announcement.icon}</span>
          <div class="text-sm sm:text-base font-medium text-center sm:text-left break-words">
            ${messageHtml}
          </div>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <a href="${config.infoPageUrl}" class="text-xs sm:text-sm font-semibold hover:underline whitespace-nowrap" style="color: ${announcement.textColor}">
            ${config.infoLinkText}
          </a>
          <button id="close-announcement-banner" 
                  class="p-1 rounded hover:bg-white/20 transition-colors" 
                  style="color: ${announcement.closeButtonColor}"
                  aria-label="Fermer le bandeau d'annonce">
            <span class="text-lg font-bold" aria-hidden="true">×</span>
          </button>
        </div>
      </div>
    `;
    
    return banner;
  }

  // Gérer la fermeture
  function handleClose() {
    const closeBtn = document.getElementById('close-announcement-banner');
    const banner = document.getElementById('announcement-banner');
    
    if (closeBtn && banner) {
      closeBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        banner.style.display = 'none';
        localStorage.setItem('announcement-banner-hidden', 'true');
      });
    }
  }

  // Ajuster la position du header
  function adjustHeaderPosition() {
    const banner = document.getElementById('announcement-banner');
    const nav = document.querySelector('nav[aria-label="Menu principal"]');
    
    if (banner && nav) {
      const bannerHeight = banner.offsetHeight;
      nav.style.top = bannerHeight + 'px';
    }
  }

  // Créer l'InfoBox pour les pages avec booking-funnel
  function createInfoBox() {
    const announcement = config.announcement;
    
    // Vérifier si on doit afficher l'InfoBox
    if (!announcement.active || !announcement.showOnAllPages) return null;
    
    // Vérifier si on est dans la période de validité
    const now = new Date();
    const startDate = new Date(announcement.startDate);
    const endDate = new Date(announcement.endDate);
    
    if (now > endDate || now < startDate) return null;
    
    const infoBox = document.createElement('div');
    infoBox.id = 'announcement-infobox';
    infoBox.className = 'bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg mb-8';
    infoBox.setAttribute('role', 'note');
    infoBox.setAttribute('aria-label', 'Information importante');
    
    // Formater le message
    const messageLines = announcement.message.split('\n');
    const messageHtml = messageLines.join('<br>');
    
    infoBox.innerHTML = `
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0">
          <span class="text-2xl" aria-hidden="true">${announcement.icon}</span>
        </div>
        <div class="flex-1">
          <p class="font-bold text-dark mb-2">Fermeture estivale pour congés</p>
          <div class="text-sm text-gray-700 space-y-1">
            ${messageHtml}
          </div>
        </div>
      </div>
    `;
    
    return infoBox;
  }

  // Ajouter l'InfoBox sur les pages avec booking-funnel
  function addInfoBox() {
    const bookingFunnel = document.getElementById('booking-funnel');
    if (bookingFunnel) {
      const infoBox = createInfoBox();
      if (infoBox) {
        // Insérer avant le booking-funnel
        bookingFunnel.before(infoBox);
      }
    }
  }

  // Initialiser le bandeau
  function init() {
    loadConfig();
    
    if (shouldShowBanner()) {
      const banner = createBanner();
      document.body.prepend(banner);
      
      // Ajuster le header
      adjustHeaderPosition();
      
      // Gérer la fermeture
      handleClose();
      
      // Recalculer au redimensionnement
      window.addEventListener('resize', adjustHeaderPosition);
    }
    
    // Ajouter l'InfoBox sur les pages avec booking-funnel
    addInfoBox();
  }

  // Initialiser dès que possible
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
