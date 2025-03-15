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
            }
        ],
        "completed_steps": 3,
        "services": ["service1", "service2"],
        "days_active": 15
    }
    
    return templates.TemplateResponse("main.html", {
        "request": request,
        "user": user_data,
        "projects": user_data["projects"],
        "completed_steps": user_data["completed_steps"],
        "services": user_data["services"],
        "days_active": user_data["days_active"]
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
