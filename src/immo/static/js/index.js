/**
 * index.js - Fonctionnalités spécifiques à la page d'accueil
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation du slider de témoignages
    initTestimonialsSlider();
    
    // Gestion du formulaire de newsletter
    initNewsletterForm();
    
    // Animation des cartes de fonctionnalités
    initFeatureCards();
  });
  
  /**
   * Initialise le slider de témoignages
   */
  function initTestimonialsSlider() {
    const slider = document.querySelector('.testimonials-slider');
    
    if (!slider) return;
    
    const cards = slider.querySelectorAll('.testimonial-card');
    let currentIndex = 0;
    
    // Créer les indicateurs si nécessaire
    const indicators = document.createElement('div');
    indicators.className = 'testimonial-indicators';
    
    cards.forEach((_, index) => {
      const dot = document.createElement('span');
      dot.className = 'indicator' + (index === 0 ? ' active' : '');
      dot.addEventListener('click', () => {
        goToSlide(index);
      });
      indicators.appendChild(dot);
    });
    
    // Ajouter les indicateurs après le slider
    slider.parentNode.insertBefore(indicators, slider.nextSibling);
    
    // Créer les boutons de navigation
    const prevButton = document.createElement('button');
    prevButton.className = 'testimonial-nav prev';
    prevButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
    prevButton.setAttribute('aria-label', 'Témoignage précédent');
    
    const nextButton = document.createElement('button');
    nextButton.className = 'testimonial-nav next';
    nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
    nextButton.setAttribute('aria-label', 'Témoignage suivant');
    
    // Ajouter les boutons de navigation
    const navContainer = document.createElement('div');
    navContainer.className = 'testimonial-nav-container';
    navContainer.appendChild(prevButton);
    navContainer.appendChild(nextButton);
    slider.parentNode.appendChild(navContainer);
    
    // Fonction pour aller à un slide spécifique
    function goToSlide(index) {
      // Mettre à jour l'index courant
      currentIndex = index;
      
      // Calculer le décalage
      const cardWidth = cards[0].offsetWidth;
      const gap = parseInt(window.getComputedStyle(slider).getPropertyValue('gap'));
      const offset = index * (cardWidth + gap);
      
      // Animer le défilement
      slider.scrollTo({
        left: offset,
        behavior: 'smooth'
      });
      
      // Mettre à jour les indicateurs
      const dots = indicators.querySelectorAll('.indicator');
      dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
      });
    }
    
    // Gestionnaires d'événements pour les boutons
    prevButton.addEventListener('click', () => {
      const newIndex = (currentIndex - 1 + cards.length) % cards.length;
      goToSlide(newIndex);
    });
    
    nextButton.addEventListener('click', () => {
      const newIndex = (currentIndex + 1) % cards.length;
      goToSlide(newIndex);
    });
    
    // Défilement automatique
    let autoplayInterval;
    
    function startAutoplay() {
      autoplayInterval = setInterval(() => {
        const newIndex = (currentIndex + 1) % cards.length;
        goToSlide(newIndex);
      }, 5000); // Changer de slide toutes les 5 secondes
    }
    
    function stopAutoplay() {
      clearInterval(autoplayInterval);
    }
    
    // Démarrer le défilement automatique
    startAutoplay();
    
    // Arrêter le défilement automatique lors de l'interaction
    slider.addEventListener('mouseenter', stopAutoplay);
    prevButton.addEventListener('mouseenter', stopAutoplay);
    nextButton.addEventListener('mouseenter', stopAutoplay);
    
    // Reprendre le défilement automatique
    slider.addEventListener('mouseleave', startAutoplay);
    prevButton.addEventListener('mouseleave', startAutoplay);
    nextButton.addEventListener('mouseleave', startAutoplay);
  }
  
  /**
   * Initialise le formulaire de newsletter
   */
  function initNewsletterForm() {
    const form = document.querySelector('.newsletter-form');
    
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      
      const emailInput = this.querySelector('input[type="email"]');
      const email = emailInput.value.trim();
      
      if (!email) {
        showFormMessage(form, 'Veuillez entrer votre adresse email.', 'error');
        return;
      }
      
      if (!isValidEmail(email)) {
        showFormMessage(form, 'Veuillez entrer une adresse email valide.', 'error');
        return;
      }
      
      // Simuler l'envoi du formulaire
      const submitButton = this.querySelector('button[type="submit"]');
      const originalText = submitButton.textContent;
      
      submitButton.disabled = true;
      submitButton.textContent = 'Envoi en cours...';
      
      // Simuler une requête AJAX
      setTimeout(() => {
        showFormMessage(form, 'Merci pour votre inscription à notre newsletter !', 'success');
        emailInput.value = '';
        submitButton.disabled = false;
        submitButton.textContent = originalText;
      }, 1000);
    });
  }
  
  /**
   * Affiche un message de formulaire
   * @param {HTMLElement} form - Le formulaire
   * @param {string} message - Le message à afficher
   * @param {string} type - Le type de message ('success' ou 'error')
   */
  function showFormMessage(form, message, type) {
    // Supprimer les messages existants
    const existingMessage = form.querySelector('.form-message');
    if (existingMessage) {
      existingMessage.remove();
    }
    
    // Créer le nouvel élément de message
    const messageElement = document.createElement('div');
    messageElement.className = `form-message ${type}`;
    messageElement.textContent = message;
    
    // Ajouter le message après le formulaire
    form.appendChild(messageElement);
    
    // Faire disparaître le message après un délai
    if (type === 'success') {
      setTimeout(() => {
        messageElement.style.opacity = '0';
        setTimeout(() => {
          messageElement.remove();
        }, 300);
      }, 3000);
    }
  }
  
  /**
   * Vérifie si une adresse email est valide
   * @param {string} email - L'adresse email à vérifier
   * @returns {boolean} - True si l'email est valide, false sinon
   */
  function isValidEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }
  
  /**
   * Initialise les animations des cartes de fonctionnalités
   */
  function initFeatureCards() {
    const cards = document.querySelectorAll('.feature-card');
    
    if (!cards.length) return;
    
    cards.forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-10px)';
        this.style.boxShadow = 'var(--box-shadow-lg)';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = 'var(--box-shadow-sm)';
      });
    });
  }
  