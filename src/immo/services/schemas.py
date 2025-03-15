"""Schémas Pydantic pour les services."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    """Schéma de base pour un service."""

    title: str = Field(..., min_length=3, max_length=64)
    description: str = Field(..., min_length=3, max_length=1000)
    price: int = Field(..., ge=0)


class ServiceCreate(ServiceBase):
    """Schéma pour la création d'un service."""

    pass


class ServiceUpdate(ServiceBase):
    """Schéma pour la mise à jour d'un service."""

    title: Optional[str] = Field(None, min_length=3, max_length=64)
    description: Optional[str] = Field(None, min_length=3, max_length=1000)
    price: Optional[int] = Field(None, ge=0)


class ServiceInDB(ServiceBase):
    """Schéma pour la représentation d'un service en base de données."""

    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
