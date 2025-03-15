"""Configuration de l'application."""

from datetime import timedelta
from typing import Any, Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application."""

    # Environnement
    ENV: str = "development"
    DEBUG: bool = True

    # Base de données
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/step_by_step_immo"

    # Sécurité
    SECRET_KEY: str = "step_by_step"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 heure
    REFRESH_TOKEN_EXPIRE_DAYS: int = 3  # 3 jours

    # Super Admin
    SUPER_ADMIN_USERNAME: str = "super_admin"
    SUPER_ADMIN_EMAIL: str = "15p035@polytechnique.cm"
    SUPER_ADMIN_PASSWORD: str = "HuguesAdmin@2021"
    SUPER_ADMIN_FIRST_NAME: str = "Hugues"
    SUPER_ADMIN_LAST_NAME: str = "Dtankouo"
    SUPER_ADMIN_ABOUT_ME: str = "Je suis un super admin"

    # Classe pour configurer les sources externes (fichiers .env)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def access_token_expires(self) -> timedelta:
        """Durée de vie du token d'accès."""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def refresh_token_expires(self) -> timedelta:
        """Durée de vie du token de rafraîchissement."""
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    @property
    def super_admin(self) -> Dict[str, Any]:
        """Configuration du super administrateur."""
        return {
            "username": self.SUPER_ADMIN_USERNAME,
            "email": self.SUPER_ADMIN_EMAIL,
            "email_confirmed": True,
            "password": self.SUPER_ADMIN_PASSWORD,
            "first_name": self.SUPER_ADMIN_FIRST_NAME,
            "last_name": self.SUPER_ADMIN_LAST_NAME,
            "about_me": self.SUPER_ADMIN_ABOUT_ME,
            "terms_confirmation": True,
        }


# Instance unique de la configuration
settings = Settings()
