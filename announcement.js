(function() {
  document.addEventListener('DOMContentLoaded', () => {
    // 1. Check configuration
    const siteConfig = window.siteConfig;
    if (!siteConfig || !siteConfig.announcement) return;

    const announcement = siteConfig.announcement;
    if (!announcement.active) return;

    // Determine paths for links (root vs subdirectory)
    const isFileProtocol = window.location.protocol === 'file:';
    let infoPageUrl = '/informations.html';
    if (isFileProtocol) {
      const isSubdir = window.location.pathname.includes('/villes/');
      const rootPrefix = isSubdir ? '../' : './';
      infoPageUrl = rootPrefix + 'informations.html';
    }

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

    // 5. Anti-spam Honeypot Protection
    initFormSpamProtection();
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

  function initFormSpamProtection() {
    const pageLoadTime = Date.now();
    const forms = document.querySelectorAll('form[data-action]');

    function isGibberish(value) {
      if (typeof value !== 'string') return false;
      const words = value.match(/[a-zA-Z]+/g);
      if (!words) return false;
      for (const word of words) {
        if (word.length > 12) {
          const hasUpper = /[A-Z]/.test(word);
          const hasLower = /[a-z]/.test(word);
          // Mixture of uppercase and lowercase, and not just title case
          if (hasUpper && hasLower && !/^[A-Z][a-z]+$/.test(word)) {
            return true;
          }
        }
      }
      return false;
    }

    function decodeAction(token) {
      if (!token) return '#';
      try {
        // Obfuscation: reversed string encoded in Base64
        const decoded = atob(token);
        const reversed = decoded.split('').reverse().join('');
        return reversed;
      } catch (err) {
        console.error('Error decoding action:', err);
        return '#';
      }
    }

    forms.forEach(form => {
      // Clear action initially to ensure it is not in the DOM
      form.setAttribute('action', '#');

      // Handle submit event
      form.addEventListener('submit', (e) => {
        // Reset custom validations before checks
        const zipcodeField = form.querySelector('input[name="lead_form[address][zipcode]"]');
        const phoneField = form.querySelector('input[name="lead_form[phone]"]');
        if (zipcodeField) zipcodeField.setCustomValidity('');
        if (phoneField) phoneField.setCustomValidity('');

        // 1. Honeypot check
        const gotcha = form.querySelector('input[name="_gotcha"]');
        if (gotcha && gotcha.value.trim() !== '') {
          console.warn('Spam submission blocked (honeypot).');
          e.preventDefault();
          return false;
        }

        // 2. Time check: block if submitted in less than 4 seconds
        const timeElapsed = (Date.now() - pageLoadTime) / 1000;
        if (timeElapsed < 4) {
          console.warn('Spam submission blocked (too fast).');
          e.preventDefault();
          return false;
        }

        // 3. Zipcode validation (5 digits)
        if (zipcodeField) {
          if (!/^[0-9]{5}$/.test(zipcodeField.value.trim())) {
            zipcodeField.setCustomValidity('Le code postal doit comporter exactement 5 chiffres.');
            zipcodeField.reportValidity();
            e.preventDefault();
            return false;
          }
        }

        // 4. Phone validation (French format)
        if (phoneField) {
          const phoneRegex = /^(?:0|\+33|0033)\s*[1-9](?:[ .-]?\d{2}){4}$/;
          if (!phoneRegex.test(phoneField.value.trim())) {
            phoneField.setCustomValidity('Veuillez saisir un numéro de téléphone valide (format français).');
            phoneField.reportValidity();
            e.preventDefault();
            return false;
          }
        }

        // 5. Gibberish detection
        let hasGibberish = false;
        const textInputs = form.querySelectorAll('input[type="text"], input[type="email"], textarea');
        textInputs.forEach(input => {
          if (input.name === '_gotcha') return;
          if (isGibberish(input.value)) {
            hasGibberish = true;
          }
        });

        if (hasGibberish) {
          console.warn('Spam submission blocked (gibberish detected).');
          e.preventDefault();
          return false;
        }

        // 6. Restore real action URL just at the moment of submission
        const token = form.getAttribute('data-action');
        form.setAttribute('action', decodeAction(token));
      });
    });

    // Handle HTMLFormElement.prototype.submit overrides to prevent direct bypass
    if (!window._honeypotInitialized) {
      window._honeypotInitialized = true;
      const originalSubmit = HTMLFormElement.prototype.submit;
      HTMLFormElement.prototype.submit = function() {
        // Reset validity
        const zipcodeField = this.querySelector('input[name="lead_form[address][zipcode]"]');
        const phoneField = this.querySelector('input[name="lead_form[phone]"]');
        if (zipcodeField) zipcodeField.setCustomValidity('');
        if (phoneField) phoneField.setCustomValidity('');

        // Honeypot check
        const gotcha = this.querySelector('input[name="_gotcha"]');
        if (gotcha && gotcha.value.trim() !== '') {
          console.warn('Spam submission blocked (proto, honeypot).');
          return;
        }

        // Time check
        const timeElapsed = (Date.now() - pageLoadTime) / 1000;
        if (timeElapsed < 4) {
          console.warn('Spam submission blocked (proto, too fast).');
          return;
        }

        // Zipcode validation
        if (zipcodeField) {
          if (!/^[0-9]{5}$/.test(zipcodeField.value.trim())) {
            zipcodeField.setCustomValidity('Le code postal doit comporter exactement 5 chiffres.');
            zipcodeField.reportValidity();
            return;
          }
        }

        // Phone validation
        if (phoneField) {
          const phoneRegex = /^(?:0|\+33|0033)\s*[1-9](?:[ .-]?\d{2}){4}$/;
          if (!phoneRegex.test(phoneField.value.trim())) {
            phoneField.setCustomValidity('Veuillez saisir un numéro de téléphone valide (format français).');
            phoneField.reportValidity();
            return;
          }
        }

        // Gibberish detection
        let hasGibberish = false;
        const textInputs = this.querySelectorAll('input[type="text"], input[type="email"], textarea');
        textInputs.forEach(input => {
          if (input.name === '_gotcha') return;
          if (isGibberish(input.value)) {
            hasGibberish = true;
          }
        });

        if (hasGibberish) {
          console.warn('Spam submission blocked (proto, gibberish).');
          return;
        }

        // Decode token and set action
        const actionToken = this.getAttribute('data-action');
        if (actionToken) {
          this.setAttribute('action', decodeAction(actionToken));
        }
        originalSubmit.apply(this);
      };
    }
  }
})();
