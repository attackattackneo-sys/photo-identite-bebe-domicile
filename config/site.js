// Configuration globale du site
const siteConfig = {
  announcement: {
    active: true, // true = visible, false = invisible
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
