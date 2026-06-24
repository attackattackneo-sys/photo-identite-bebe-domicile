// Configuration globale du site
// Ce fichier centralise toutes les configurations modifiables sans toucher au code

const siteConfig = {
  // Configuration du bandeau d'annonce
  announcement: {
    active: true, // true = visible, false = invisible
    message: "📸 Fermeture estivale pour congés!\nJe serai en vacances du 16 juillet au 6 août 2026.\nAucune séance photo ne sera programmée pendant cette période.\nJe serai ravi de vous retrouver à partir du lundi 10 août 2026 pour de nouvelles aventures photographiques!\nPour toute demande, vous pouvez me contacter par email, je vous répondrai à mon retour.",
    startDate: "2026-07-16",
    endDate: "2026-08-06",
    showOnAllPages: true,
    // Couleurs du bandeau (doivent contraster avec le site)
    backgroundColor: "#e60000", // Rouge vif pour bien contraster avec l'orange du site
    textColor: "#ffffff", // Texte blanc
    icon: "📸", // Icône à gauche
    closeButtonColor: "#ffffff" // Couleur du bouton de fermeture
  },
  
  // URL de la page d'informations
  infoPageUrl: "informations.html",
  
  // Texte du lien "En savoir plus"
  infoLinkText: "En savoir plus"
};

// Rendre disponible dans le scope global pour le navigateur
window.siteConfig = siteConfig;

// Export pour utilisation dans les scripts Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = siteConfig;
}
