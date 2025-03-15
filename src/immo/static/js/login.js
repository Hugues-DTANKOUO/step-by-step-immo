/**
 * login.js - Fonctionnalités JavaScript spécifiques à la page de connexion
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation de la gestion du mot de passe
    initPasswordToggle();
    
    // Initialisation du formulaire de connexion
    initLoginForm();
    
    // Initialisation des boutons de connexion sociale
    initSocialLogin();
  });
  
  /**
   * Initialise le bouton de visibilité du mot de passe
   */
  function initPasswordToggle() {
    const passwordToggle = document.querySelector('.password-toggle');
    
    if (!passwordToggle) return;
    
    passwordToggle.addEventListener('click', function() {
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
  }
  
  /**
   * Initialise le formulaire de connexion
   */
  function initLoginForm() {
    const form = document.querySelector('.auth-form');
    
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      
      // Récupérer les valeurs du formulaire
      const email = form.querySelector('#email').value.trim();
      const password = form.querySelector('#password').value.trim();
      const remember = form.querySelector('#remember')?.checked || false;
      
      // Valider les champs
      let isValid = true;
      
      if (!email) {
        showFieldError(form.querySelector('#email'), 'Veuillez entrer votre adresse email');
        isValid = false;
      } else if (!isValidEmail(email)) {
        showFieldError(form.querySelector('#email'), 'Veuillez entrer une adresse email valide');
        isValid = false;
      }
      
      if (!password) {
        showFieldError(form.querySelector('#password'), 'Veuillez entrer votre mot de passe');
        isValid = false;
      }
      
      if (!isValid) return;
      
      // Simuler l'envoi du formulaire
      const submitButton = form.querySelector('button[type="submit"]');
      const originalText = submitButton.textContent;
      submitButton.disabled = true;
      submitButton.textContent = 'Connexion en cours...';
      
      // Dans un environnement réel, nous enverrions ces données au serveur
      // Ici, nous simulons simplement une redirection après un délai
      setTimeout(() => {
        // Rediriger vers la page principale
        window.location.href = '/main';
      }, 1500);
    });
    
    // Supprimer les messages d'erreur lors de la saisie
    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => {
      input.addEventListener('input', function() {
        clearFieldError(this);
      });
    });
  }
  
  /**
   * Initialise les boutons de connexion sociale
   */
  function initSocialLogin() {
    const socialButtons = document.querySelectorAll('.btn-social');
    
    socialButtons.forEach(button => {
      button.addEventListener('click', function(event) {
        event.preventDefault();
        
        const provider = this.classList.contains('btn-google') ? 'Google' : 'Facebook';
        
        // Simuler le chargement
        this.disabled = true;
        const originalText = this.textContent;
        this.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Connexion en cours...`;
        
        // Dans un environnement réel, nous redirigerions vers l'API d'authentification
        // Ici, nous simulons simplement une redirection après un délai
        setTimeout(() => {
          // Rediriger vers la page principale
          window.location.href = '/main';
        }, 1500);
      });
    });
  }
  
  /**
   * Affiche un message d'erreur pour un champ
   * @param {HTMLElement} field - Le champ concerné
   * @param {string} message - Le message d'erreur
   */
  function showFieldError(field, message) {
    // Supprimer les erreurs existantes
    clearFieldError(field);
    
    // Ajouter la classe d'erreur
    field.classList.add('error');
    
    // Créer le message d'erreur
    const errorElement = document.createElement('div');
    errorElement.className = 'form-error';
    errorElement.textContent = message;
    
    // Ajouter le message après le groupe d'input
    const inputGroup = field.closest('.input-group') || field;
    const formGroup = inputGroup.closest('.form-group');
    formGroup.appendChild(errorElement);
  }
  
  /**
   * Supprime le message d'erreur d'un champ
   * @param {HTMLElement} field - Le champ concerné
   */
  function clearFieldError(field) {
    // Supprimer la classe d'erreur
    field.classList.remove('error');
    
    // Supprimer le message d'erreur
    const formGroup = field.closest('.form-group');
    const errorElement = formGroup.querySelector('.form-error');
    if (errorElement) {
      errorElement.remove();
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
  