"""Router pour les utilitaires."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from immo.extensions import get_db
from immo.users.models import User
from immo.users.router import get_current_user
from immo.utils.models import City, Country, Currency, StatusProject
from immo.utils.schemas import (
    CityCreate,
    CityInDB,
    CityUpdate,
    CityWithCountry,
    CountryCreate,
    CountryInDB,
    CountryUpdate,
    CurrencyCreate,
    CurrencyInDB,
    CurrencyUpdate,
    StatusProjectCreate,
    StatusProjectInDB,
    StatusProjectUpdate,
    UtilsProperties,
)


router = APIRouter()


@router.get("/properties", response_model=UtilsProperties)
async def get_utils_properties(db: AsyncSession = Depends(get_db)):
    """Récupérer toutes les propriétés utilitaires (pays, devises, statuts de projet)."""
    # Récupérer les pays
    countries_result = await db.execute(select(Country))
    countries = countries_result.scalars().all()

    # Récupérer les devises
    currencies_result = await db.execute(select(Currency))
    currencies = currencies_result.scalars().all()

    # Récupérer les statuts de projet
    status_projects_result = await db.execute(select(StatusProject))
    status_projects = status_projects_result.scalars().all()

    return {"countries": countries, "currencies": currencies, "status_projects": status_projects}


# Endpoints pour les pays
@router.get("/countries", response_model=List[CountryInDB])
async def get_countries(db: AsyncSession = Depends(get_db)):
    """Récupérer tous les pays."""
    result = await db.execute(select(Country))
    countries = result.scalars().all()
    return countries


@router.post("/countries", response_model=CountryInDB, status_code=status.HTTP_201_CREATED)
async def create_country(
    country: CountryCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Créer un nouveau pays."""
    # Vérifier les permissions
    if not current_user.has_permission("CreateCountry"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de créer un pays")

    # Vérifier si le pays existe déjà
    result = await db.execute(select(Country).where(Country.name == country.name))
    existing_country = result.scalar_one_or_none()
    if existing_country:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce pays existe déjà")

    # Créer le pays
    db_country = Country(name=country.name, code=country.code, created_by=current_user.id)
    db.add(db_country)
    await db.commit()
    await db.refresh(db_country)

    return db_country


@router.get("/countries/{country_id}", response_model=CountryInDB)
async def get_country(country_id: int, db: AsyncSession = Depends(get_db)):
    """Récupérer un pays par son ID."""
    result = await db.execute(select(Country).where(Country.id == country_id))
    country = result.scalar_one_or_none()

    if country is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pays non trouvé")

    return country


@router.put("/countries/{country_id}", response_model=CountryInDB)
async def update_country(
    country_id: int,
    country_update: CountryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mettre à jour un pays."""
    # Vérifier les permissions
    if not current_user.has_permission("UpdateCountry"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de modifier un pays"
        )

    # Récupérer le pays
    result = await db.execute(select(Country).where(Country.id == country_id))
    db_country = result.scalar_one_or_none()

    if db_country is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pays non trouvé")

    # Mettre à jour le pays
    db_country.name = country_update.name
    db_country.code = country_update.code

    await db.commit()
    await db.refresh(db_country)

    return db_country


@router.delete("/countries/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_country(
    country_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Supprimer un pays."""
    # Vérifier les permissions
    if not current_user.has_permission("DeleteCountry"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de supprimer un pays"
        )

    # Récupérer le pays
    result = await db.execute(select(Country).where(Country.id == country_id))
    db_country = result.scalar_one_or_none()

    if db_country is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pays non trouvé")

    # Supprimer le pays
    await db.delete(db_country)
    await db.commit()

    return None


# Endpoints pour les villes
@router.get("/countries/{country_id}/cities", response_model=List[CityInDB])
async def get_cities_by_country(country_id: int, db: AsyncSession = Depends(get_db)):
    """Récupérer toutes les villes d'un pays."""
    result = await db.execute(select(City).where(City.country_id == country_id))
    cities = result.scalars().all()
    return cities


@router.post("/countries/{country_id}/cities", response_model=CityInDB, status_code=status.HTTP_201_CREATED)
async def create_city(
    country_id: int,
    city: CityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Créer une nouvelle ville pour un pays."""
    # Vérifier les permissions
    if not current_user.has_permission("CreateCity"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de créer une ville")

    # Vérifier si le pays existe
    country_result = await db.execute(select(Country).where(Country.id == country_id))
    country = country_result.scalar_one_or_none()
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pays non trouvé")

    # Vérifier si la ville existe déjà
    city_result = await db.execute(select(City).where(City.name == city.name, City.country_id == country_id))
    existing_city = city_result.scalar_one_or_none()
    if existing_city:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette ville existe déjà pour ce pays")

    # Créer la ville
    db_city = City(name=city.name, country_id=country_id, created_by=current_user.id)
    db.add(db_city)
    await db.commit()
    await db.refresh(db_city)

    return db_city


@router.get("/cities/{city_id}", response_model=CityWithCountry)
async def get_city(city_id: int, db: AsyncSession = Depends(get_db)):
    """Récupérer une ville par son ID avec les informations sur son pays."""
    # Récupérer la ville
    result = await db.execute(select(City).where(City.id == city_id))
    city = result.scalar_one_or_none()

    if city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ville non trouvée")

    # Récupérer le pays
    country_result = await db.execute(select(Country).where(Country.id == city.country_id))
    country = country_result.scalar_one_or_none()

    if country is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pays non trouvé pour cette ville")

    # Construire la réponse
    return {
        "id": city.id,
        "name": city.name,
        "country_id": city.country_id,
        "created_by": city.created_by,
        "country": country,
    }


@router.put("/cities/{city_id}", response_model=CityInDB)
async def update_city(
    city_id: int,
    city_update: CityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mettre à jour une ville."""
    # Vérifier les permissions
    if not current_user.has_permission("UpdateCity"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de modifier une ville"
        )

    # Récupérer la ville
    result = await db.execute(select(City).where(City.id == city_id))
    db_city = result.scalar_one_or_none()

    if db_city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ville non trouvée")

    # Mettre à jour la ville
    if city_update.name is not None:
        db_city.name = city_update.name
    if city_update.country_id is not None:
        # Vérifier si le nouveau pays existe
        country_result = await db.execute(select(Country).where(Country.id == city_update.country_id))
        country = country_result.scalar_one_or_none()
        if not country:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pays non trouvé")
        db_city.country_id = city_update.country_id

    await db.commit()
    await db.refresh(db_city)

    return db_city


@router.delete("/cities/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(city_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Supprimer une ville."""
    # Vérifier les permissions
    if not current_user.has_permission("DeleteCity"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de supprimer une ville"
        )

    # Récupérer la ville
    result = await db.execute(select(City).where(City.id == city_id))
    db_city = result.scalar_one_or_none()

    if db_city is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ville non trouvée")

    # Supprimer la ville
    await db.delete(db_city)
    await db.commit()

    return None


# Endpoints pour les devises
@router.get("/currencies", response_model=List[CurrencyInDB])
async def get_currencies(db: AsyncSession = Depends(get_db)):
    """Récupérer toutes les devises."""
    result = await db.execute(select(Currency))
    currencies = result.scalars().all()
    return currencies


@router.post("/currencies", response_model=CurrencyInDB, status_code=status.HTTP_201_CREATED)
async def create_currency(
    currency: CurrencyCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle devise."""
    # Vérifier les permissions
    if not current_user.has_permission("CreateCurrency"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de créer une devise"
        )

    # Vérifier si la devise existe déjà
    result = await db.execute(
        select(Currency).where((Currency.name == currency.name) | (Currency.code == currency.code))
    )
    existing_currency = result.scalar_one_or_none()
    if existing_currency:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette devise existe déjà")

    # Créer la devise
    db_currency = Currency(name=currency.name, code=currency.code, created_by=current_user.id)
    db.add(db_currency)
    await db.commit()
    await db.refresh(db_currency)

    return db_currency


@router.get("/currencies/{currency_id}", response_model=CurrencyInDB)
async def get_currency(currency_id: int, db: AsyncSession = Depends(get_db)):
    """Récupérer une devise par son ID."""
    result = await db.execute(select(Currency).where(Currency.id == currency_id))
    currency = result.scalar_one_or_none()

    if currency is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devise non trouvée")

    return currency


@router.put("/currencies/{currency_id}", response_model=CurrencyInDB)
async def update_currency(
    currency_id: int,
    currency_update: CurrencyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mettre à jour une devise."""
    # Vérifier les permissions
    if not current_user.has_permission("UpdateCurrency"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de modifier une devise"
        )

    # Récupérer la devise
    result = await db.execute(select(Currency).where(Currency.id == currency_id))
    db_currency = result.scalar_one_or_none()

    if db_currency is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devise non trouvée")

    # Mettre à jour la devise
    db_currency.name = currency_update.name
    db_currency.code = currency_update.code

    await db.commit()
    await db.refresh(db_currency)

    return db_currency


@router.delete("/currencies/{currency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_currency(
    currency_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Supprimer une devise."""
    # Vérifier les permissions
    if not current_user.has_permission("DeleteCurrency"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de supprimer une devise"
        )

    # Récupérer la devise
    result = await db.execute(select(Currency).where(Currency.id == currency_id))
    db_currency = result.scalar_one_or_none()

    if db_currency is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devise non trouvée")

    # Supprimer la devise
    await db.delete(db_currency)
    await db.commit()

    return None


# Endpoints pour les statuts de projet
@router.get("/status-projects", response_model=List[StatusProjectInDB])
async def get_status_projects(db: AsyncSession = Depends(get_db)):
    """Récupérer tous les statuts de projet."""
    result = await db.execute(select(StatusProject))
    status_projects = result.scalars().all()
    return status_projects


@router.post("/status-projects", response_model=StatusProjectInDB, status_code=status.HTTP_201_CREATED)
async def create_status_project(
    status_project: StatusProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Créer un nouveau statut de projet."""
    # Vérifier les permissions
    if not current_user.has_permission("CreateStatusProject"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de créer un statut de projet"
        )

    # Vérifier si le statut de projet existe déjà
    result = await db.execute(select(StatusProject).where(StatusProject.name == status_project.name))
    existing_status_project = result.scalar_one_or_none()
    if existing_status_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce statut de projet existe déjà")

    # Créer le statut de projet
    db_status_project = StatusProject(name=status_project.name, description=status_project.description)
    db.add(db_status_project)
    await db.commit()
    await db.refresh(db_status_project)

    return db_status_project


@router.get("/status-projects/{status_project_id}", response_model=StatusProjectInDB)
async def get_status_project(status_project_id: int, db: AsyncSession = Depends(get_db)):
    """Récupérer un statut de projet par son ID."""
    result = await db.execute(select(StatusProject).where(StatusProject.id == status_project_id))
    status_project = result.scalar_one_or_none()

    if status_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statut de projet non trouvé")

    return status_project


@router.put("/status-projects/{status_project_id}", response_model=StatusProjectInDB)
async def update_status_project(
    status_project_id: int,
    status_project_update: StatusProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mettre à jour un statut de projet."""
    # Vérifier les permissions
    if not current_user.has_permission("UpdateStatusProject"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de modifier un statut de projet"
        )

    # Pour les trois premiers statuts de projet (en dur), seul le super admin peut les modifier
    if status_project_id <= 3 and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de modifier ce statut de projet"
        )

    # Récupérer le statut de projet
    result = await db.execute(select(StatusProject).where(StatusProject.id == status_project_id))
    db_status_project = result.scalar_one_or_none()

    if db_status_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statut de projet non trouvé")

    # Mettre à jour le statut de projet
    db_status_project.name = status_project_update.name
    db_status_project.description = status_project_update.description

    await db.commit()
    await db.refresh(db_status_project)

    return db_status_project


@router.delete("/status-projects/{status_project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_status_project(
    status_project_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Supprimer un statut de projet."""
    # Vérifier les permissions
    if not current_user.has_permission("DeleteStatusProject"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de supprimer un statut de projet"
        )

    # Pour les trois premiers statuts de projet (en dur), on ne peut pas les supprimer
    if status_project_id <= 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous ne pouvez pas supprimer ce statut de projet"
        )

    # Récupérer le statut de projet
    result = await db.execute(select(StatusProject).where(StatusProject.id == status_project_id))
    db_status_project = result.scalar_one_or_none()

    if db_status_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statut de projet non trouvé")

    # Supprimer le statut de projet
    await db.delete(db_status_project)
    await db.commit()

    return None
