"""Extensions pour l'application FastAPI."""

import logging

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from immo.config import settings


# Configuration du logging
logger = logging.getLogger(__name__)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Moteur de base de données et session asynchrone
engine: Optional[AsyncEngine] = None
async_session_maker = None


async def init_db() -> None:
    """Initialisation de la connexion à la base de données."""
    global engine, async_session_maker

    if engine is None:
        logger.info(f"Initialisation du moteur de base de données avec URL: {settings.DATABASE_URL}")
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True,
            poolclass=NullPool if settings.ENV == "testing" else None,
        )

        async_session_maker = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Fournit une session de base de données pour les opérations asynchrones."""
    if async_session_maker is None:
        await init_db()

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Dépendance pour la pagination
def pagination_params(skip: int = 0, limit: int = 100):
    """Paramètres de pagination pour les API."""
    return {"skip": skip, "limit": limit}
