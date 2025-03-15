"""Schémas Pydantic pour les utilitaires."""

from typing import List, Optional

from pydantic import BaseModel, Field


# Schémas pour les pays
class CountryBase(BaseModel):
    """Schéma de base pour un pays."""

    name: str = Field(..., min_length=3, max_length=64)
    code: str = Field(..., min_length=2, max_length=2)


class CountryCreate(CountryBase):
    """Schéma pour la création d'un pays."""

    pass


class CountryUpdate(CountryBase):
    """Schéma pour la mise à jour d'un pays."""

    pass


class CountryInDB(CountryBase):
    """Schéma pour la représentation d'un pays en base de données."""

    id: int
    created_by: int

    class Config:
        orm_mode = True


# Schémas pour les villes
class CityBase(BaseModel):
    """Schéma de base pour une ville."""

    name: str = Field(..., min_length=3, max_length=64)
    country_id: int


class CityCreate(CityBase):
    """Schéma pour la création d'une ville."""

    pass


class CityUpdate(BaseModel):
    """Schéma pour la mise à jour d'une ville."""

    name: Optional[str] = Field(None, min_length=3, max_length=64)
    country_id: Optional[int] = None


class CityInDB(CityBase):
    """Schéma pour la représentation d'une ville en base de données."""

    id: int
    created_by: int

    class Config:
        orm_mode = True


class CityWithCountry(CityInDB):
    """Schéma pour la représentation d'une ville avec son pays."""

    country: CountryInDB


# Schémas pour les devises
class CurrencyBase(BaseModel):
    """Schéma de base pour une devise."""

    name: str = Field(..., min_length=3, max_length=64)
    code: str = Field(..., min_length=3, max_length=5)


class CurrencyCreate(CurrencyBase):
    """Schéma pour la création d'une devise."""

    pass


class CurrencyUpdate(CurrencyBase):
    """Schéma pour la mise à jour d'une devise."""

    name: Optional[str] = Field(None, min_length=3, max_length=64)
    code: Optional[str] = Field(None, min_length=3, max_length=5)


class CurrencyInDB(CurrencyBase):
    """Schéma pour la représentation d'une devise en base de données."""

    id: int
    created_by: int

    class Config:
        orm_mode = True


# Schémas pour les statuts de projet
class StatusProjectBase(BaseModel):
    """Schéma de base pour un statut de projet."""

    name: str = Field(..., min_length=3, max_length=64)
    description: Optional[str] = Field(None, max_length=200)


class StatusProjectCreate(StatusProjectBase):
    """Schéma pour la création d'un statut de projet."""

    pass


class StatusProjectUpdate(StatusProjectBase):
    """Schéma pour la mise à jour d'un statut de projet."""

    pass


class StatusProjectInDB(StatusProjectBase):
    """Schéma pour la représentation d'un statut de projet en base de données."""

    id: int

    class Config:
        orm_mode = True


# Schéma pour les propriétés utilitaires
class UtilsProperties(BaseModel):
    """Schéma pour les propriétés utilitaires."""

    countries: List[CountryInDB]
    currencies: List[CurrencyInDB]
    status_projects: List[StatusProjectInDB]
