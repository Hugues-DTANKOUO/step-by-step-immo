"""Schémas Pydantic pour les abonnements."""

from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# Schémas pour les abonnements d'utilisateurs non enregistrés
class NonUserSubscriptionBase(BaseModel):
    """Schéma de base pour une souscription d'utilisateur non enregistré."""

    email: EmailStr = Field(..., min_length=3, max_length=100)
    names: str = Field(..., min_length=3, max_length=100)
    project_title: str = Field(..., min_length=3, max_length=64)
    project_location: str = Field(..., min_length=3, max_length=64)
    project_budget: str = Field(..., min_length=3, max_length=64)
    project_dateline: date
    project_description: str = Field(..., min_length=3, max_length=1000)
    project_terms_confirmation: bool


class NonUserSubscriptionCreate(NonUserSubscriptionBase):
    """Schéma pour la création d'une souscription d'utilisateur non enregistré."""

    @field_validator("project_dateline")
    def validate_dateline(cls, v):
        """Validation de la date limite."""
        if v < date.today():
            raise ValueError("La date limite doit être dans le futur")
        return v


class NonUserSubscriptionInDB(NonUserSubscriptionBase):
    """Schéma pour la représentation d'une souscription d'utilisateur non enregistré en base de données."""

    id: int
    validated: bool = False
    created_at: datetime

    class Config:
        orm_mode = True


# Schémas pour les abonnements validés d'utilisateurs non enregistrés
class ValidatedNonUserSubscriptionBase(BaseModel):
    """Schéma de base pour une souscription validée d'utilisateur non enregistré."""

    email: EmailStr = Field(..., min_length=3, max_length=100)
    names: str = Field(..., min_length=3, max_length=100)
    project_title: str = Field(..., min_length=3, max_length=64)
    project_location: str = Field(..., min_length=3, max_length=64)
    project_budget: int
    project_budget_currency_id: int
    project_dateline: date
    project_description: str = Field(..., min_length=3, max_length=1000)
    project_terms_confirmation: bool
    valid_until: date
    manager_id: int
    subscription_id: int


class ValidatedNonUserSubscriptionCreate(ValidatedNonUserSubscriptionBase):
    """Schéma pour la création d'une souscription validée d'utilisateur non enregistré."""

    @field_validator("valid_until")
    def validate_valid_until(cls, v):
        """Validation de la date de validité."""
        if v < date.today():
            raise ValueError("La date de validité doit être dans le futur")
        return v


class ValidatedNonUserSubscriptionInDB(ValidatedNonUserSubscriptionBase):
    """Schéma pour la représentation d'une souscription validée d'utilisateur non enregistré en base de données."""

    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Schémas pour les abonnements gratuits
class FreeSubscriptionBase(BaseModel):
    """Schéma de base pour une souscription gratuite."""

    email: EmailStr = Field(..., min_length=3, max_length=100)


class FreeSubscriptionCreate(FreeSubscriptionBase):
    """Schéma pour la création d'une souscription gratuite."""

    pass


class FreeSubscriptionInDB(FreeSubscriptionBase):
    """Schéma pour la représentation d'une souscription gratuite en base de données."""

    id: int
    created_at: datetime

    class Config:
        orm_mode = True
