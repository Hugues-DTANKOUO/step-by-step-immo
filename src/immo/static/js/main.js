/**
 * main.js - Fonctionnalités JavaScript globales
 * Modernisation du frontend pour FastAPI avec Jinja2
 */

document.addEventListener('DOMContentLoaded', function() {
    // Gestion du menu mobile
    initMobileMenu();
    
    // Gestion des animations au scroll
    initScrollAnimations();
    
    // Initialisation des tooltips
    initTooltips();
    
    // Gestion des formulaires
    initForms();
  });
  
  /**
   * Initialise le menu mobile
   */
  function initMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuClose = document.querySelector('.mobile-menu-close');
    const body = document.body;
    
    if (mobileMenuToggle && mobileMenu) {
      // Ouvrir le menu mobile
      mobileMenuToggle.addEventListener('click', function() {
        mobileMenu.classList.add('active');
        body.style.overflow = 'hidden'; // Empêcher le défilement de la page
      });
      
      // Fermer le menu mobile
      if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', function() {
          mobileMenu.classList.remove('active');
          body.style.overflow = ''; // Réactiver le défilement de la page
        });
      }
      
      // Fermer le menu mobile en cliquant en dehors
      document.addEventListener('click', function(event) {
        if (mobileMenu.classList.contains('active') && 
            !mobileMenu.contains(event.target) && 
            !mobileMenuToggle.contains(event.target)) {
          mobileMenu.classList.remove('active');
          body.style.overflow = '';
        }
      });
    }
  }
  
  /**
   * Initialise les animations au scroll
   */
  function initScrollAnimations() {
    // Sélectionner tous les éléments à animer
    const animatedElements = document.querySelectorAll('.fade-in, .slide-in-left, .slide-in-right, .slide-in-up');
    
    if (animatedElements.length > 0) {
      // Fonction pour vérifier si un élément est visible dans la fenêtre
      const isElementInViewport = (el) => {
        const rect = el.getBoundingClientRect();
        return (
          rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.8 &&
          rect.bottom >= 0
        );
      };
      
      // Fonction pour animer les éléments visibles
      const handleScroll = () => {
        animatedElements.forEach(element => {
          if (isElementInViewport(element)) {
            element.style.opacity = '1';
            element.style.transform = 'translate(0)';
          }
        });
      };
      
      // Initialiser les éléments
      animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        if (element.classList.contains('slide-in-left')) {
          element.style.transform = 'translateX(-30px)';
        } else if (element.classList.contains('slide-in-right')) {
          element.style.transform = 'translateX(30px)';
        } else if (element.classList.contains('slide-in-up')) {
          element.style.transform = 'translateY(30px)';
        }
      });
      
      // Ajouter l'écouteur d'événement de défilement
      window.addEventListener('scroll', handleScroll);
      
      // Déclencher une fois au chargement
      handleScroll();
    }
  }
  
  /**
   * Initialise les tooltips
   */
  function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(tooltip => {
      tooltip.addEventListener('mouseenter', function() {
        const tooltipText = this.getAttribute('data-tooltip');
        
        // Créer l'élément tooltip
        const tooltipElement = document.createElement('div');
        tooltipElement.className = 'tooltip';
        tooltipElement.textContent = tooltipText;
        
        // Ajouter le tooltip au DOM
        document.body.appendChild(tooltipElement);
        
        // Positionner le tooltip
        const rect = this.getBoundingClientRect();
        tooltipElement.style.top = `${rect.top - tooltipElement.offsetHeight - 10}px`;
        tooltipElement.style.left = `${rect.left + (rect.width / 2) - (tooltipElement.offsetWidth / 2)}px`;
        
        // Afficher le tooltip
        setTimeout(() => {
          tooltipElement.style.opacity = '1';
        }, 10);
        
        // Stocker une référence au tooltip
        this.tooltipElement = tooltipElement;
      });
      
      tooltip.addEventListener('mouseleave', function() {
        if (this.tooltipElement) {
          this.tooltipElement.style.opacity = '0';
          
          // Supprimer le tooltip après l'animation
          setTimeout(() => {
            if (this.tooltipElement.parentNode) {
              this.tooltipElement.parentNode.removeChild(this.tooltipElement);
            }
          }, 300);
        }
      });
    });
  }
  
  /**
   * Initialise les formulaires
   */
  function initForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
      // Gestion de la soumission du formulaire
      form.addEventListener('submit', function(event) {
        // Vérifier si le formulaire est valide
        if (!validateForm(this)) {
          event.preventDefault();
        }
      });
      
      // Gestion des champs de mot de passe
      const passwordToggles = form.querySelectorAll('.password-toggle');
      passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
          const passwordInput = this.closest('.input-group').querySelector('input');
          const icon = this.querySelector('i');
          
          if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
          } else {
            passwordInput.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
          }
        });
      });
    });
  }
  
  /**
   * Valide un formulaire
   * @param {HTMLFormElement} form - Le formulaire à valider
   * @returns {boolean} - True si le formulaire est valide, false sinon
   */
  function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input, select, textarea');
    
    // Supprimer les messages d'erreur existants
    const errorMessages = form.querySelectorAll('.form-error');
    errorMessages.forEach(error => error.remove());
    
    // Vérifier chaque champ
    inputs.forEach(input => {
      // Réinitialiser les styles
      input.classList.remove('error');
      
      // Vérifier si le champ est requis et vide
      if (input.hasAttribute('required') && !input.value.trim()) {
        isValid = false;
        markFieldAsInvalid(input, 'Ce champ est requis');
      }
      
      // Vérifier les emails
      if (input.type === 'email' && input.value.trim() && !isValidEmail(input.value)) {
        isValid = false;
        markFieldAsInvalid(input, 'Veuillez entrer une adresse email valide');
      }
      
      // Vérifier les mots de passe
      if (input.type === 'password' && input.value.trim() && input.value.length < 8) {
        isValid = false;
        markFieldAsInvalid(input, 'Le mot de passe doit contenir au moins 8 caractères');
      }
    });
    
    return isValid;
  }
  
  /**
   * Marque un champ comme invalide et affiche un message d'erreur
   * @param {HTMLElement} field - Le champ à marquer
   * @param {string} message - Le message d'erreur à afficher
   */
  function markFieldAsInvalid(field, message) {
    field.classList.add('error');
    
    // Créer le message d'erreur
    const errorElement = document.createElement('div');
    errorElement.className = 'form-error';
    errorElement.textContent = message;
    
    // Ajouter le message après le champ ou son parent
    const parent = field.closest('.form-group') || field.parentNode;
    parent.appendChild(errorElement);
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
   * Fonction utilitaire pour débouncer les appels de fonction
   * @param {Function} func - La fonction à débouncer
   * @param {number} wait - Le délai d'attente en ms
   * @returns {Function} - La fonction debouncée
   */
  function debounce(func, wait) {
    let timeout;
    return function() {
      const context = this;
      const args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(context, args), wait);
    };
  }
  