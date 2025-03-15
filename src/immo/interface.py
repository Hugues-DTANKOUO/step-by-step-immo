"""Application FastAPI principale pour Step by Step Immo."""

import logging

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from immo.config import settings
from immo.extensions import get_db, init_db
from immo.projects.router import router as projects_router
from immo.seed import seed_database
from immo.services.router import router as services_router
from immo.subscriptions.router import router as subscriptions_router
from immo.users.admin_router import router as admin_router
from immo.users.router import router as users_router
from immo.utils.router import router as utils_router


# Répertoire de l'application
APP_NAME = "Step by Step Immo"
APP_DIR = Path(__file__).parent

# Configuration de la journalisation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application."""
    # Code à exécuter au démarrage
    logger.info("Initialisation de la base de données")
    await init_db()

    # Initialisation des données de base (seed) uniquement en développement ou en test
    if settings.ENV in ["development", "testing"]:
        try:
            logger.info("Initialisation des données de base...")
            await seed_database()
            logger.info("Données de base initialisées avec succès!")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des données de base: {e}")

    # Rend le contrôle à FastAPI
    yield

    # Code à exécuter à l'arrêt
    logger.info("Fermeture de l'application")


# Initialisation de l'application avec le gestionnaire de cycle de vie
app = FastAPI(
    title=APP_NAME,
    description="Plateforme de gestion de projets immobiliers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Montage des fichiers statiques
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

# Templates Jinja2 pour le rendu HTML
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

# Inclusion des routeurs
app.include_router(utils_router, prefix="/api/utils", tags=["Utilités"])
app.include_router(users_router, prefix="/api/users", tags=["Utilisateurs"])
app.include_router(admin_router, prefix="/api/admin", tags=["Administration"])
app.include_router(projects_router, prefix="/api/projects", tags=["Projets"])
app.include_router(services_router, prefix="/api/services", tags=["Services"])
app.include_router(subscriptions_router, prefix="/api/subscriptions", tags=["Abonnements"])


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    """Page d'accueil de l'application."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": APP_NAME,
            "year": 2025,  # Année courante
            "user": True,  # À remplacer par l'utilisateur connecté si nécessaire
            "registration_option": "registration",  # Option par défaut pour les formulaires
        },
    )


# Route pour la page de connexion
@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route pour la page d'inscription
@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Route pour souscrire à un abonnement
@app.get("/subscribe")
async def subscribe(request: Request):
    return templates.TemplateResponse("subscribe.html", {"request": request})

# Route pour gérer les abonnements
@app.get("/my-subscription", response_class=HTMLResponse)
async def manage_subscription(request: Request):
    """Page for managing the current user's subscription."""
    # Mock data for user
    user = {
        "id": 1,
        "username": "demo_user",
        "email": "demo@example.com",
        "first_name": "Demo",
        "last_name": "User"
    }
    
    # Mock data for user's subscription
    subscription = {
        "plan_name": "Standard",
        "status": "active",
        "status_label": "Active",
        "price": "9.99",
        "currency": "$",
        "interval": "month",
        "billing_cycle": "monthly",
        "next_billing_date": "2025-04-15",
        "start_date": "2025-03-15",
        "payment_method": "Visa ending in 1234",
        "auto_renew": True
    }
    
    # Mock data for invoices
    invoices = [
        {
            "id": 1,
            "date": "2025-03-15",
            "description": "Standard Plan - Monthly",
            "amount": "9.99",
            "currency": "$",
            "status": "paid",
            "status_label": "Paid",
            "pdf_url": "#"
        },
        {
            "id": 2,
            "date": "2025-02-15",
            "description": "Standard Plan - Monthly",
            "amount": "9.99",
            "currency": "$",
            "status": "paid",
            "status_label": "Paid",
            "pdf_url": "#"
        }
    ]
    
    # Mock data for payment methods
    payment_methods = [
        {
            "id": 1,
            "type": "credit_card",
            "brand": "Visa",
            "last4": "1234",
            "exp_month": "12",
            "exp_year": "2026",
            "is_default": True
        },
        {
            "id": 2,
            "type": "paypal",
            "email": "demo@example.com",
            "is_default": False
        }
    ]

    return templates.TemplateResponse(
        "manage_subscription.html",
        {
            "request": request,
            "user": user,
            "subscription": subscription,
            "invoices": invoices,
            "payment_methods": payment_methods,
            "next_billing_date": "2025-04-15",
            "app_name": APP_NAME,
            "year": 2025,
        },
    )

# Route pour la page de profil utilisateur
@app.get("/profile", response_class=HTMLResponse)
async def user_profile(request: Request):
    """Page de profil utilisateur."""
    # Exemple de données à passer au template

    subscription = {
        "plan_name": "Standard",
        "status": "active",
        "status_label": "Active",
        "price": "9.99",
        "currency": "$",
        "interval": "month",
        "billing_cycle": "monthly",
        "next_billing_date": "15/04/2025",
        "start_date": "15/03/2025",
        "payment_method": "Visa ending in 1234",
        "auto_renew": True
    }

    notification_settings = {
        "email_notifications": True,
        "push_notifications": True,
        "sms_notifications": False,
        "email_project_updates": True,
        "email_newsletter": False
    }

    privaty_settings = {
        "profile_visibility": 'public',
        "allow_contact": True,
        "allow_messages": True
    }

    user_data = {
        "id": 1,
        "username": "dtankouo",
        "email": "hugues@stepbystepimmo.com",
        "first_name": "Hugues",
        "last_name": "Dtankouo",
        "phone": "0123456789",
        "address": "123, Rue de la Demo",
        "city": "Montreal",
        "country": "Canada",
        "postal_code": "75000",
        "created_at": "15/03/2025",
        "last_login": "15/03/2025",
        "last_activity": "15/03/2025 12:30",
        "subscription": subscription,
        "notification_settings": notification_settings,
        "privacy_settings": privaty_settings,
    }  
    return templates.TemplateResponse(
        "user_account.html",
        {
            "request": request,
            "user": user_data,
            "app_name": APP_NAME,
            "year": 2025,
        },
    )

# Route pour créer un projet
@app.get("/create-project", response_class=HTMLResponse)
async def create_project(request: Request):
    """Page pour créer un nouveau projet."""
    # Exemple de données à passer au template
    user_data = {
        "id": 1,
        "username": "dtankouo",
        "email": "hugues@stepbystepimmo.com",
        "first_name": "Hugues",
        "last_name": "Dtankouo",
        "phone": "0123456789",
        "address": "123, Rue de la Demo",
        "city": "Montreal",
        "country": "Canada",
        "postal_code": "75000",
        "created_at": "15/03/2025",
        "last_login": "15/03/2025",
        "last_activity": "15/03/2025 12:30",
    }

    cities = [
        {
            "id": 1,
            "name": "Douala",
            "country": {
                "id": 1,
                "name": "Cameroun",
                "code": "CM",
            }
        },
        {
            "id": 2,
            "name": "Yaoundé",
            "country": {
                "id": 1,
                "name": "Cameroun",
                "code": "CM",
            }
        },
        {
            "id": 3,
            "name": "Paris",
            "country": {
                "id": 2,
                "name": "France",
                "code": "FR",
            }
        },
        {
            "id": 4,
            "name": "Montreal",
            "country": {
                "id": 3,
                "name": "Canada",
                "code": "CA",
            }
        },
        {
            "id": 5,
            "name": "Abidjan",
            "country": {
                "id": 4,
                "name": "Côte d'Ivoire",
                "code": "CI",
            }
        },
        {
            "id": 6,
            "name": "Cotonou",
            "country": {
                "id": 5,
                "name": "Bénin",
                "code": "BJ",
            }
        },
        {
            "id": 7,
            "name": "Kinshasa",
            "country": {
                "id": 6,
                "name": "RDC",
                "code": "CD",
            }
        }
    ]

    currencies = [
        {
        "id": 1,
        "name": "Dollar américain",
        "symbol": "$",
        "code": "USD",
        },
        {
        "id": 2,
        "name": "Euro",
        "symbol": "€",
        "code": "EUR",
        },
        {
        "id": 3,
        "name": "Franc CFA",
        "symbol": "Fcfa",
        "code": "XAF",
        },
        {
        "id": 4,
        "name": "Dollar canadien",
        "symbol": "$",
        "code": "CAD",
        },
    ]

    return templates.TemplateResponse(
        "create_project.html",
        {
            "request": request,
            "cities": cities,
            "currencies": currencies,
            "user": user_data,
            "app_name": APP_NAME,
            "year": 2025,
        },
    )

# Route pour créer une étape de projet
@app.get("/add-step", response_class=HTMLResponse)
async def create_step(request: Request):
    """Page pour créer une nouvelle étape de projet."""
    # Exemple de données à passer au template
    user_data = {
        "id": 1,
        "username": "dtankouo",
        "email": "hugues@stepbystepimmo.com",
        "first_name": "Hugues",
        "last_name": "Dtankouo",
        "phone": "0123456789",
        "address": "123, Rue de la Demo",
        "city": "Montreal",
        "country": "Canada",
        "postal_code": "75000",
        "created_at": "15/03/2025",
        "last_login": "15/03/2025",
        "last_activity": "15/03/2025 12:30",
    }

    project = {
        "id": 1,
        "title": "Achat d'un terrain titré à Douala",
        "description": "Achat d'un terrain titré de 500 m² à Douala pour la construction d'une maison",
        "budget": 100000,
        "begin_at": "15/03/2025",
        "end_at": "15/06/2025",
        "progress": 65,
        "unallocated_budget": 30000,
        "city": "Douala",
        "currency": {
            "id": 3,
            "name": "Franc CFA",
            "symbol": "Fcfa",
            "code": "XAF",
        },
        "status": "active",
        "created_at": "15/03/2025",
        "completed_steps": 3,
        "total_steps": 5
    }

    return templates.TemplateResponse(
        "add_step.html",
        {
            "request": request,
            "user": user_data,
            "project": project,
            "app_name": APP_NAME,
            "year": 2025,
        },
    )

# Route pour le tableau de bord
@app.get("/dashboard")
async def dashboard(request: Request):
    # Exemple de données à passer au template
    user_data = {
        "first_name": "Hugues",
        "projects": [
            {
                "id": 1,
                "name": "Projet Exemple",
                "status": "active",
                "progress": 65,
                "location": "Paris",
                "created_at": "15/03/2025",
                "completed_steps": 3,
                "total_steps": 5
            },
            {
                "id": 2,
                "name": "Achat d'un terrain",
                "status": "active",
                "progress": 25,
                "location": "Douala",
                "created_at": "15/03/2025",
                "completed_steps": 1,
                "total_steps": 4
            },
            {
                "id": 3,
                "name": "Construction d'une maison à Yaoundé",
                "status": "pending",
                "progress": 5,
                "location": "Montreal",
                "created_at": "15/03/2025",
                "completed_steps": 2,
                "total_steps": 6
            }
        ],
        "completed_steps": 3,
        "services": ["service1", "service2"],
        "days_active": 15
    }

    next_steps = [
        {
            "id": 1,
            "title": "Rencontre avec l'architecte",
            "project_name": "Projet Exemple",
            "due_date": "15/04/2025",
        },
        {
            "id": 2,
            "title": "Visite du terrain",
            "project_name": "Achat d'un terrain",
            "due_date": "20/04/2025",
        }
    ]

    recommended_services = [
        {
            "id": 1,
            "icon": "fas fa-laptop-code",
            "name": "Hugues Dtankouo",
            "category": "Gestionnaire de projet",
        },
        {
            "id": 2,
            "icon": "fas fa-drafting-compass",
            "name": "Alban Koffi",
            "category": "Architecte",
        },
        {
            "id": 3,
            "icon": "fas fa-home",
            "name": "Marie Dupont",
            "category": "Agent immobilier",
        }
    ]
    
    return templates.TemplateResponse("main.html", {
        "request": request,
        "user": user_data,
        "projects": user_data["projects"],
        "completed_steps": user_data["completed_steps"],
        "services": user_data["services"],
        "days_active": user_data["days_active"],
        "next_steps": next_steps,
        "recommended_services": recommended_services,
    })


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Vérification de l'état de l'application.
    Vérifie l'état de la connexion à la base de données et d'autres dépendances critiques.
    """
    health_status = {
        "status": "healthy",
        "app_info": {"name": APP_NAME, "version": "1.0.0", "environment": settings.ENV},
        "dependencies": {"database": "healthy"},
    }

    # Vérifier la connexion à la base de données
    try:
        # Exécuter une requête simple pour vérifier la connexion
        result = await db.execute("SELECT 1")
        await result.scalar_one()
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["dependencies"]["database"] = f"unhealthy: {str(e)}"

    # Code de statut HTTP basé sur l'état de santé
    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status
