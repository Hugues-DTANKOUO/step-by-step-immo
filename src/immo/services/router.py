"""Router pour les services."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from immo.extensions import get_db
from immo.services.models import Service
from immo.services.schemas import ServiceCreate, ServiceInDB, ServiceUpdate
from immo.users.models import User
from immo.users.router import get_current_user


router = APIRouter()


@router.get("/", response_model=List[ServiceInDB])
async def get_services(
    skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer tous les services de l'utilisateur courant."""
    query = select(Service).where(Service.user_id == current_user.id).offset(skip).limit(limit)

    result = await db.execute(query)
    services = result.scalars().all()

    return services


@router.post("/", response_model=ServiceInDB, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Créer un nouveau service."""
    # Vérifier si l'utilisateur a le droit de créer un service
    if not current_user.has_permission("CreateService"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de créer un service"
        )

    # Vérifier si l'utilisateur a déjà atteint la limite de 5 services
    services_count = await db.execute(select(Service).where(Service.user_id == current_user.id))
    services = services_count.scalars().all()

    if len(services) >= 5 and not current_user.has_permission("CreateMoreThanFiveServices"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous avez déjà atteint le nombre maximum de services"
        )

    # Vérifier si un service avec le même titre existe déjà pour cet utilisateur
    existing_service = await db.execute(
        select(Service).where(Service.title == service.title, Service.user_id == current_user.id)
    )
    if existing_service.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vous avez déjà un service avec ce titre")

    # Créer le service
    db_service = Service(
        title=service.title, description=service.description, price=service.price, user_id=current_user.id
    )

    # Ajouter le service à la base de données
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)

    return db_service


@router.get("/{service_id}", response_model=ServiceInDB)
async def get_service(
    service_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer un service par son ID."""
    # Récupérer le service
    service_result = await db.execute(select(Service).where(Service.id == service_id))
    service = service_result.scalar_one_or_none()

    # Vérifier si le service existe
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service non trouvé")

    # Vérifier si l'utilisateur a le droit de voir ce service
    if service.user_id != current_user.id and not current_user.has_permission("ReadService"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de voir ce service")

    return service


@router.put("/{service_id}", response_model=ServiceInDB)
async def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Mettre à jour un service."""
    # Récupérer le service
    service_result = await db.execute(select(Service).where(Service.id == service_id))
    service = service_result.scalar_one_or_none()

    # Vérifier si le service existe
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service non trouvé")

    # Vérifier si l'utilisateur a le droit de modifier ce service
    if service.user_id != current_user.id and not current_user.has_permission("UpdateService"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de modifier ce service"
        )

    # Vérifier si un autre service avec le même titre existe déjà pour cet utilisateur
    if service_update.title and service_update.title != service.title:
        existing_service = await db.execute(
            select(Service).where(
                Service.title == service_update.title, Service.user_id == current_user.id, Service.id != service_id
            )
        )
        if existing_service.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Vous avez déjà un service avec ce titre"
            )

    # Mettre à jour le service
    if service_update.title is not None:
        service.title = service_update.title
    if service_update.description is not None:
        service.description = service_update.description
    if service_update.price is not None:
        service.price = service_update.price

    await db.commit()
    await db.refresh(service)

    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """Supprimer un service."""
    # Récupérer le service
    service_result = await db.execute(select(Service).where(Service.id == service_id))
    service = service_result.scalar_one_or_none()

    # Vérifier si le service existe
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service non trouvé")

    # Vérifier si l'utilisateur a le droit de supprimer ce service
    if service.user_id != current_user.id and not current_user.has_permission("DeleteService"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de supprimer ce service"
        )

    # Supprimer le service
    await db.delete(service)
    await db.commit()
