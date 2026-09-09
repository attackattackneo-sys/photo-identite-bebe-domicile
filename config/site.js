// Configuration globale du site
const siteConfig = {
  announcement: {
    active: false, // true = visible, false = invisible
    message: "📸 Fermeture estivale pour congés!\nJe serai en vacances du 16 juillet au 6 août 2026.\nAucune séance photo ne sera programmée pendant cette période.\nJe serai ravi de vous retrouver à partir du lundi 10 août 2026 pour de nouvelles aventures photographiques!\nPour toute demande, vous pouvez me contacter par email, je vous répondrai à mon retour.",
    startDate: "2026-07-16",
    endDate: "2026-08-06",
    showOnAllPages: true,
    bannerText: "📸 Fermeture pour congés du 16 juillet au 6 août 2026 inclus.",
    bgColor: "bg-indigo-600", // Couleur de fond Tailwind
    textColor: "text-white"    // Couleur de texte Tailwind
  }
};

window.siteConfig = siteConfig;


// Global Mobile Menu Controller
window.toggleMobileMenu = function() {
    var menu = document.getElementById('mobile-menu');
    var nav = document.getElementById('main-nav') || document.querySelector('nav');
    var btn = document.getElementById('mobile-menu-btn');
    if (!menu) return;

    var isHidden = menu.classList.contains('hidden');
    if (isHidden) {
        menu.classList.remove('hidden');
        if (nav) {
            nav.classList.add('bg-white/95', 'backdrop-blur-md', 'shadow-lg');
            nav.classList.remove('bg-transparent', 'shadow-none');
            var navLinks = nav.querySelector('.nav-links-container');
            var logoText = nav.querySelector('.logo-text');
            var logoImg = nav.querySelector('.logo-img');
            if (navLinks) { navLinks.classList.add('text-gray-800'); navLinks.classList.remove('text-white/90'); }
            if (logoText) { logoText.classList.add('text-dark'); logoText.classList.remove('text-white'); }
            if (logoImg) { logoImg.classList.remove('brightness-0', 'invert'); }
        }
        if (btn) {
            btn.classList.add('text-gray-800');
            btn.classList.remove('text-white');
            btn.setAttribute('aria-expanded', 'true');
            btn.innerHTML = '<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>';
        }
    } else {
        menu.classList.add('hidden');
        if (btn) {
            btn.setAttribute('aria-expanded', 'false');
            btn.innerHTML = '<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>';
        }
        if (window.scrollY <= 20 && nav) {
            nav.classList.remove('bg-white/95', 'backdrop-blur-md', 'shadow-lg');
            nav.classList.add('bg-transparent', 'shadow-none');
            var navLinks = nav.querySelector('.nav-links-container');
            var logoText = nav.querySelector('.logo-text');
            var logoImg = nav.querySelector('.logo-img');
            if (navLinks) { navLinks.classList.remove('text-gray-800'); navLinks.classList.add('text-white/90'); }
            if (logoText) { logoText.classList.remove('text-dark'); logoText.classList.add('text-white'); }
            if (logoImg) { logoImg.classList.add('brightness-0', 'invert'); }
            if (btn) {
                btn.classList.remove('text-gray-800');
                btn.classList.add('text-white');
            }
        }
    }
};

window.closeMobileMenu = function() {
    var menu = document.getElementById('mobile-menu');
    if (menu && !menu.classList.contains('hidden')) {
        window.toggleMobileMenu();
    }
};

document.addEventListener('click', function(e) {
    var menu = document.getElementById('mobile-menu');
    var btn = document.getElementById('mobile-menu-btn');
    if (menu && !menu.classList.contains('hidden')) {
        if (!menu.contains(e.target) && (!btn || !btn.contains(e.target))) {
            window.closeMobileMenu();
        }
    }
});

// Keyboard accessibility: Escape key closes modal and mobile menu
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' || e.keyCode === 27) {
        if (typeof window.closeMobileMenu === 'function') {
            window.closeMobileMenu();
        }
        if (typeof window.closeBookingModal === 'function') {
            window.closeBookingModal();
        }
    }
});

