"""Router pour les abonnements."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from immo.extensions import get_db
from immo.subscriptions.models import FreeSubscription, NonUserSubscription, ValidatedNonUserSubscription
from immo.subscriptions.schemas import (
    FreeSubscriptionCreate,
    FreeSubscriptionInDB,
    NonUserSubscriptionCreate,
    NonUserSubscriptionInDB,
    ValidatedNonUserSubscriptionCreate,
    ValidatedNonUserSubscriptionInDB,
)
from immo.users.models import User
from immo.users.router import get_current_user


router = APIRouter()


@router.post("/non_user", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_non_user_subscription(
    subscription: NonUserSubscriptionCreate, db: AsyncSession = Depends(get_db)
) -> Any:
    """Créer un nouvel abonnement pour un utilisateur non enregistré."""
    # Créer l'abonnement
    db_subscription = NonUserSubscription(
        email=subscription.email,
        names=subscription.names,
        project_title=subscription.project_title,
        project_location=subscription.project_location,
        project_budget=subscription.project_budget,
        project_dateline=subscription.project_dateline,
        project_description=subscription.project_description,
        project_terms_confirmation=subscription.project_terms_confirmation,
    )

    db.add(db_subscription)
    await db.commit()
    await db.refresh(db_subscription)

    return {"message": "Abonnement créé"}


@router.get("/non_user", response_model=list[NonUserSubscriptionInDB])
async def get_non_user_subscriptions(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer tous les abonnements des utilisateurs non enregistrés."""
    # Vérifier si l'utilisateur est administrateur
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à accéder à cette ressource"
        )

    # Récupérer tous les abonnements
    subscriptions_result = await db.execute(select(NonUserSubscription))
    subscriptions = subscriptions_result.scalars().all()

    return subscriptions


@router.post(
    "/validated_non_user", response_model=ValidatedNonUserSubscriptionInDB, status_code=status.HTTP_201_CREATED
)
async def create_validated_non_user_subscription(
    subscription: ValidatedNonUserSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Valider un abonnement d'utilisateur non enregistré."""
    # Vérifier si l'utilisateur est administrateur
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à accéder à cette ressource"
        )

    # Vérifier si l'abonnement existe
    non_user_subscription_result = await db.execute(
        select(NonUserSubscription).where(NonUserSubscription.id == subscription.subscription_id)
    )
    non_user_subscription = non_user_subscription_result.scalar_one_or_none()

    if not non_user_subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abonnement non trouvé")

    # Vérifier si l'abonnement a déjà été validé
    if non_user_subscription.validated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet abonnement a déjà été validé")

    # Créer l'abonnement validé
    db_subscription = ValidatedNonUserSubscription(
        email=subscription.email,
        names=subscription.names,
        project_title=subscription.project_title,
        project_location=subscription.project_location,
        project_budget=subscription.project_budget,
        project_budget_currency_id=subscription.project_budget_currency_id,
        project_dateline=subscription.project_dateline,
        project_description=subscription.project_description,
        project_terms_confirmation=subscription.project_terms_confirmation,
        valid_until=subscription.valid_until,
        manager_id=subscription.manager_id,
        subscription_id=subscription.subscription_id,
    )

    db.add(db_subscription)
    await db.commit()
    await db.refresh(db_subscription)

    # Valider l'abonnement original si la date de validité est dans le futur
    if db_subscription.valid_until >= datetime.utcnow().date():
        non_user_subscription.validated = True
        await db.commit()

    return db_subscription


@router.get("/validated_non_user", response_model=list[ValidatedNonUserSubscriptionInDB])
async def get_validated_non_user_subscriptions(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer tous les abonnements validés des utilisateurs non enregistrés."""
    # Vérifier si l'utilisateur est administrateur
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à accéder à cette ressource"
        )

    # Récupérer tous les abonnements validés
    subscriptions_result = await db.execute(select(ValidatedNonUserSubscription))
    subscriptions = subscriptions_result.scalars().all()

    return subscriptions


@router.get("/validated_non_user/{subscription_id}", response_model=ValidatedNonUserSubscriptionInDB)
async def get_validated_non_user_subscription(
    subscription_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer un abonnement validé d'utilisateur non enregistré par son ID."""
    # Vérifier si l'utilisateur est administrateur
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à accéder à cette ressource"
        )

    # Récupérer l'abonnement validé
    subscription_result = await db.execute(
        select(ValidatedNonUserSubscription).where(ValidatedNonUserSubscription.id == subscription_id)
    )
    subscription = subscription_result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abonnement validé non trouvé")

    return subscription


@router.put("/validated_non_user/{subscription_id}", response_model=ValidatedNonUserSubscriptionInDB)
async def update_validated_non_user_subscription(
    subscription_id: int,
    subscription_update: ValidatedNonUserSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Mettre à jour un abonnement validé d'utilisateur non enregistré."""
    # Vérifier si l'utilisateur est administrateur
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à accéder à cette ressource"
        )

    # Récupérer l'abonnement validé
    subscription_result = await db.execute(
        select(ValidatedNonUserSubscription).where(ValidatedNonUserSubscription.id == subscription_id)
    )
    subscription = subscription_result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abonnement validé non trouvé")

    # Vérifier qu'il s'agit bien du même abonnement original
    if subscription.subscription_id != subscription_update.subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Vous ne pouvez pas modifier l'identifiant de l'abonnement"
        )

    # Mettre à jour l'abonnement validé
    subscription.email = subscription_update.email
    subscription.names = subscription_update.names
    subscription.project_title = subscription_update.project_title
    subscription.project_location = subscription_update.project_location
    subscription.project_budget = subscription_update.project_budget
    subscription.project_budget_currency_id = subscription_update.project_budget_currency_id
    subscription.project_dateline = subscription_update.project_dateline
    subscription.project_description = subscription_update.project_description
    subscription.project_terms_confirmation = subscription_update.project_terms_confirmation
    subscription.valid_until = subscription_update.valid_until
    subscription.manager_id = subscription_update.manager_id

    await db.commit()
    await db.refresh(subscription)

    # Mettre à jour le statut de validation de l'abonnement original
    non_user_subscription_result = await db.execute(
        select(NonUserSubscription).where(NonUserSubscription.id == subscription.subscription_id)
    )
    non_user_subscription = non_user_subscription_result.scalar_one_or_none()

    if non_user_subscription:
        non_user_subscription.validated = subscription.valid_until >= datetime.utcnow().date()
        await db.commit()

    return subscription


@router.delete("/validated_non_user/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_validated_non_user_subscription(
    subscription_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """Supprimer un abonnement validé d'utilisateur non enregistré."""
    # Vérifier si l'utilisateur est administrateur
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à accéder à cette ressource"
        )

    # Récupérer l'abonnement validé
    subscription_result = await db.execute(
        select(ValidatedNonUserSubscription).where(ValidatedNonUserSubscription.id == subscription_id)
    )
    subscription = subscription_result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abonnement validé non trouvé")

    # Récupérer l'identifiant de l'abonnement original avant suppression
    original_subscription_id = subscription.subscription_id

    # Supprimer l'abonnement validé
    await db.delete(subscription)
    await db.commit()

    # Mettre à jour le statut de validation de l'abonnement original
    non_user_subscription_result = await db.execute(
        select(NonUserSubscription).where(NonUserSubscription.id == original_subscription_id)
    )
    non_user_subscription = non_user_subscription_result.scalar_one_or_none()

    if non_user_subscription:
        non_user_subscription.validated = False
        await db.commit()


@router.post("/free", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_free_subscription(subscription: FreeSubscriptionCreate, db: AsyncSession = Depends(get_db)) -> Any:
    """Créer un nouvel abonnement gratuit."""
    # Vérifier si l'email est déjà utilisé
    existing_subscription_result = await db.execute(
        select(FreeSubscription).where(FreeSubscription.email == subscription.email)
    )
    if existing_subscription_result.scalar_one_or_none():
        return {"message": "Cet email est déjà abonné à notre newsletter"}

    # Créer l'abonnement gratuit
    db_subscription = FreeSubscription(email=subscription.email)

    db.add(db_subscription)
    await db.commit()

    return {"message": "Abonnement créé"}


@router.get("/free", response_model=list[FreeSubscriptionInDB])
async def get_free_subscriptions(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer tous les abonnements gratuits."""
    # Vérifier si l'utilisateur est administrateur
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à accéder à cette ressource"
        )

    # Récupérer tous les abonnements gratuits
    subscriptions_result = await db.execute(select(FreeSubscription))
    subscriptions = subscriptions_result.scalars().all()

    return subscriptions
