(function() {
  document.addEventListener('DOMContentLoaded', () => {
    // 1. Check configuration
    const siteConfig = window.siteConfig;
    if (!siteConfig || !siteConfig.announcement) return;

    const announcement = siteConfig.announcement;
    if (!announcement.active) return;

    // Determine paths for links (root vs subdirectory)
    const isSubdir = window.location.pathname.includes('/villes/');
    const rootPrefix = isSubdir ? '../' : './';
    const infoPageUrl = rootPrefix + 'informations.html';

    // 2. LocalStorage Key for Session Dismissal
    // We append the start and end dates to the key. If dates change, the banner reappears automatically.
    const storageKey = 'announcement_dismissed_' + (announcement.startDate || '') + '_' + (announcement.endDate || '');
    const isDismissed = localStorage.getItem(storageKey) === 'true';

    // 3. Render and Inject the Banner (if not dismissed and not on the info page itself)
    const isInfoPage = window.location.pathname.endsWith('informations.html') || window.location.pathname.endsWith('informations');

    if (!isDismissed && !isInfoPage) {
      createBanner(announcement, infoPageUrl, storageKey);
    }

    // 4. Render and Inject the InfoBox in Booking Funnel (if present)
    const bookingFunnel = document.getElementById('booking-funnel');
    if (bookingFunnel) {
      createInfoBox(announcement, bookingFunnel);
    }
  });

  function createBanner(announcement, infoPageUrl, storageKey) {
    const banner = document.createElement('div');
    banner.id = 'announcement-banner';
    banner.role = 'alert';
    banner.ariaLive = 'polite';
    
    // Tailwind classes for a thin, modern, premium sticky banner
    // z-index must be high (60) to stay above navigation (50)
    banner.className = `sticky top-0 left-0 w-full ${announcement.bgColor || 'bg-indigo-600'} ${announcement.textColor || 'text-white'} font-sans text-[11px] sm:text-xs md:text-sm py-2 px-4 z-[60] shadow-md transition-all duration-300 overflow-hidden flex items-center justify-between`;
    
    banner.innerHTML = `
      <div class="flex-1 text-center pr-8 pl-4 flex items-center justify-center gap-1.5 flex-wrap leading-normal font-medium">
        <span>${announcement.bannerText}</span>
        <a href="${infoPageUrl}" class="underline hover:text-orange-200 transition-colors font-bold inline-flex items-center gap-0.5 whitespace-nowrap">
          En savoir plus <span class="text-[9px]">➔</span>
        </a>
      </div>
      <button id="announcement-close-btn" class="absolute right-3 top-1/2 -translate-y-1/2 text-white/80 hover:text-white hover:bg-white/10 active:scale-95 transition font-bold text-lg p-1.5 focus:outline-none rounded-lg flex items-center justify-center w-7 h-7" aria-label="Fermer l'annonce">
        &times;
      </button>
    `;

    // Inject at the very beginning of the body
    document.body.insertBefore(banner, document.body.firstChild);

    // Dynamic Navigation and body height adjustments
    const nav = document.querySelector('nav');
    
    function adjustNavPosition() {
      if (nav && banner.parentNode) {
        const bannerHeight = banner.offsetHeight;
        nav.style.top = bannerHeight + 'px';
      }
    }

    // Initial position adjustment
    // Wait for a brief moment to ensure layout is computed
    setTimeout(adjustNavPosition, 50);

    // Handle window resize dynamically
    window.addEventListener('resize', adjustNavPosition);

    // Dismiss button behavior
    const closeBtn = banner.querySelector('#announcement-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        localStorage.setItem(storageKey, 'true');
        
        // Premium sliding micro-animation
        banner.style.height = '0px';
        banner.style.opacity = '0';
        banner.style.paddingTop = '0px';
        banner.style.paddingBottom = '0px';
        banner.style.border = 'none';
        
        if (nav) {
          nav.style.top = '0px';
        }
        
        window.removeEventListener('resize', adjustNavPosition);
        
        setTimeout(() => {
          banner.remove();
        }, 300);
      });
    }
  }

  function createInfoBox(announcement, bookingFunnel) {
    const infoBox = document.createElement('div');
    infoBox.id = 'announcement-infobox';
    infoBox.role = 'region';
    infoBox.ariaLabel = 'Informations de fermeture';
    
    // Style coordinates with the visual palette: warm, elegant borders, clean background
    infoBox.className = 'w-full max-w-4xl mx-auto bg-orange-50/60 border border-orange-100 border-l-4 border-l-[#e67000] p-6 md:p-8 rounded-2xl mb-8 shadow-sm text-left animate-fade-in-up';
    
    infoBox.innerHTML = `
      <div class="flex gap-4 items-start">
        <span class="text-2xl md:text-3xl mt-0.5">⚠️</span>
        <div class="flex-1">
          <h3 class="font-serif text-lg md:text-xl font-bold text-dark mb-3">
            Période de congés : Informations importantes pour vos réservations
          </h3>
          <div class="text-gray-700 text-sm md:text-base leading-relaxed whitespace-pre-line font-sans">
            ${announcement.message}
          </div>
        </div>
      </div>
    `;

    // Insert inside the booking funnel container, right after the intro title section if it exists
    const titleBlock = bookingFunnel.querySelector('.text-center.mb-16') || bookingFunnel.querySelector('div');
    if (titleBlock) {
      titleBlock.parentNode.insertBefore(infoBox, titleBlock.nextSibling);
    } else {
      bookingFunnel.insertBefore(infoBox, bookingFunnel.firstChild);
    }
  }
})();
