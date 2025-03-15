/**
 * dashboard.js - Fonctionnalités spécifiques à la page principale (tableau de bord)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des cartes de projets
    initProjectCards();
    
    // Initialisation du carousel de conseils
    initTipsCarousel();
    
    // Gestion des statistiques
    initDashboardStats();
  });
  
  /**
   * Initialise les interactions avec les cartes de projets
   */
  function initProjectCards() {
    const projectCards = document.querySelectorAll('.project-card');
    
    if (!projectCards.length) return;
    
    projectCards.forEach(card => {
      // Animation au survol
      card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px)';
        this.style.boxShadow = 'var(--box-shadow-md)';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = 'var(--box-shadow-sm)';
      });
      
      // Redirection au clic sur la carte (sauf si clic sur un bouton)
      card.addEventListener('click', function(event) {
        // Ne pas rediriger si on clique sur un bouton ou un lien
        if (event.target.closest('a, button')) return;
        
        // Récupérer l'URL de détail du projet
        const detailLink = this.querySelector('a[href^="/projets/"]');
        if (detailLink) {
          window.location.href = detailLink.getAttribute('href');
        }
      });
    });
  }
  
  /**
   * Initialise le carousel de conseils
   */
  function initTipsCarousel() {
    const carousel = document.querySelector('.tips-carousel');
    if (!carousel) return;
    
    const tips = [
      {
        icon: 'fas fa-lightbulb',
        title: 'Optimisez votre budget',
        text: 'Prévoyez une marge de 10-15% pour les imprévus dans votre projet immobilier.'
      },
      {
        icon: 'fas fa-file-contract',
        title: 'Vérifiez les documents',
        text: 'Assurez-vous de bien lire tous les documents avant de signer, particulièrement les conditions.'
      },
      {
        icon: 'fas fa-calendar-check',
        title: 'Planifiez vos visites',
        text: 'Organisez plusieurs visites à différents moments de la journée pour mieux évaluer un bien.'
      }
    ];
    
    let currentTipIndex = 0;
    const tipCard = carousel.querySelector('.tip-card');
    const prevButton = document.querySelector('.carousel-control.prev');
    const nextButton = document.querySelector('.carousel-control.next');
    const indicators = document.querySelectorAll('.carousel-indicators .indicator');
    
    // Fonction pour afficher un conseil
    function showTip(index) {
      const tip = tips[index];
      
      // Animer la sortie
      tipCard.style.opacity = '0';
      tipCard.style.transform = 'translateX(-20px)';
      
      setTimeout(() => {
        // Mettre à jour le contenu
        tipCard.querySelector('.tip-icon i').className = tip.icon;
        tipCard.querySelector('.tip-title').textContent = tip.title;
        tipCard.querySelector('.tip-text').textContent = tip.text;
        
        // Animer l'entrée
        tipCard.style.transform = 'translateX(0)';
        tipCard.style.opacity = '1';
        
        // Mettre à jour les indicateurs
        indicators.forEach((indicator, i) => {
          indicator.classList.toggle('active', i === index);
        });
        
        // Mettre à jour l'index courant
        currentTipIndex = index;
      }, 300);
    }
    
    // Gestionnaires d'événements pour les boutons
    if (prevButton) {
      prevButton.addEventListener('click', () => {
        const newIndex = (currentTipIndex - 1 + tips.length) % tips.length;
        showTip(newIndex);
      });
    }
    
    if (nextButton) {
      nextButton.addEventListener('click', () => {
        const newIndex = (currentTipIndex + 1) % tips.length;
        showTip(newIndex);
      });
    }
    
    // Gestionnaires d'événements pour les indicateurs
    indicators.forEach((indicator, index) => {
      indicator.addEventListener('click', () => {
        showTip(index);
      });
    });
    
    // Rotation automatique des conseils
    let autoplayInterval;
    
    function startAutoplay() {
      autoplayInterval = setInterval(() => {
        const newIndex = (currentTipIndex + 1) % tips.length;
        showTip(newIndex);
      }, 8000); // Changer de conseil toutes les 8 secondes
    }
    
    function stopAutoplay() {
      clearInterval(autoplayInterval);
    }
    
    // Démarrer la rotation automatique
    startAutoplay();
    
    // Arrêter la rotation lors de l'interaction
    carousel.addEventListener('mouseenter', stopAutoplay);
    if (prevButton) prevButton.addEventListener('mouseenter', stopAutoplay);
    if (nextButton) nextButton.addEventListener('mouseenter', stopAutoplay);
    
    // Reprendre la rotation
    carousel.addEventListener('mouseleave', startAutoplay);
    if (prevButton) prevButton.addEventListener('mouseleave', startAutoplay);
    if (nextButton) nextButton.addEventListener('mouseleave', startAutoplay);
  }
  
  /**
   * Initialise les statistiques du tableau de bord
   */
  function initDashboardStats() {
    const statValues = document.querySelectorAll('.stat-value');
    
    if (!statValues.length) return;
    
    // Animation des chiffres
    statValues.forEach(stat => {
      const finalValue = stat.textContent;
      const isPercentage = finalValue.includes('%');
      let value = isPercentage ? parseInt(finalValue) : parseInt(finalValue);
      
      if (isNaN(value)) return;
      
      // Réinitialiser à zéro
      stat.textContent = isPercentage ? '0%' : '0';
      
      // Animer jusqu'à la valeur finale
      let startValue = 0;
      const duration = 1500;
      const increment = value / (duration / 16);
      
      const updateStat = () => {
        startValue += increment;
        if (startValue > value) {
          startValue = value;
        }
        
        stat.textContent = isPercentage ? Math.floor(startValue) + '%' : Math.floor(startValue);
        
        if (startValue < value) {
          requestAnimationFrame(updateStat);
        }
      };
      
      // Démarrer l'animation après un court délai
      setTimeout(updateStat, 300);
    });
  }
  