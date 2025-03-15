"""Schémas Pydantic pour les projets."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from immo.utils.schemas import CityInDB, CurrencyInDB, StatusProjectInDB


# Schémas pour les étapes
class StepBase(BaseModel):
    """Schéma de base pour une étape."""

    title: str = Field(..., min_length=3, max_length=64)
    description: str = Field(..., min_length=3, max_length=1000)
    number: int
    budget: int = Field(..., ge=0)
    begin_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class StepCreate(StepBase):
    """Schéma pour la création d'une étape."""

    pass


class StepUpdate(StepBase):
    """Schéma pour la mise à jour d'une étape."""

    id: int


class StepInDB(StepBase):
    """Schéma pour la représentation d'une étape en base de données."""

    id: int
    project_id: int
    creator_id: int
    created_at: datetime
    progress: int = 0

    class Config:
        orm_mode = True


# Schémas pour les projets
class ProjectBase(BaseModel):
    """Schéma de base pour un projet."""

    title: str = Field(..., min_length=3, max_length=64)
    description: str = Field(..., min_length=3, max_length=1000)
    budget: int = Field(..., ge=0)
    begin_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class ProjectCreate(ProjectBase):
    """Schéma pour la création d'un projet."""

    status_project_id: int
    city_id: Optional[int] = None
    currency_id: Optional[int] = None

    @field_validator("end_at")
    def validate_dates(cls, v, values):
        """Validation des dates."""
        if "begin_at" in values and values["begin_at"] is not None and v is not None:
            if values["begin_at"] > v:
                raise ValueError("La date de début doit être antérieure à la date de fin")
        return v


class ProjectUpdate(ProjectCreate):
    """Schéma pour la mise à jour d'un projet."""

    id: int


class ProjectInDB(ProjectBase):
    """Schéma pour la représentation d'un projet en base de données."""

    id: int
    user_id: int
    status_project_id: int
    city_id: Optional[int] = None
    currency_id: Optional[int] = None
    created_at: datetime
    progress: int = 0
    unallocated_budget: int = 0

    class Config:
        orm_mode = True


class ProjectWithDetails(ProjectInDB):
    """Schéma pour la représentation d'un projet avec ses détails."""

    status_project: StatusProjectInDB
    city: Optional[CityInDB] = None
    currency: Optional[CurrencyInDB] = None
    steps: List[StepInDB] = []
