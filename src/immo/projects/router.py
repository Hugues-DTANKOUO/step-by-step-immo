"""Router pour les projets."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from immo.extensions import get_db
from immo.projects.models import Project, Step
from immo.projects.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectWithDetails,
    StepCreate,
    StepInDB,
    StepUpdate,
)
from immo.users.models import User
from immo.users.router import get_current_user
from immo.utils.models import City, Currency, StatusProject


router = APIRouter()


@router.get("/", response_model=List[ProjectWithDetails])
async def get_projects(
    skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer tous les projets de l'utilisateur courant."""
    # Construire la requête
    query = (
        select(Project)
        .options(
            joinedload(Project.status_project),
            joinedload(Project.city),
            joinedload(Project.currency),
            joinedload(Project.steps),
        )
        .where(Project.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )

    # Exécuter la requête
    result = await db.execute(query)
    projects = result.unique().scalars().all()

    return projects


@router.post("/", response_model=ProjectWithDetails, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Créer un nouveau projet."""
    # Vérifier si l'utilisateur a le droit de créer un projet
    if not current_user.has_permission("CreateProject"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de créer un projet")

    # Vérifier si l'utilisateur a déjà atteint la limite de 5 projets
    projects_count = await db.execute(select(Project).where(Project.user_id == current_user.id))
    projects = projects_count.scalars().all()

    if len(projects) >= 5 and not current_user.has_permission("CreateMoreThanFiveProjects"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous avez déjà atteint le nombre maximum de projets"
        )

    # Vérifier si le statut de projet existe
    status_project_result = await db.execute(select(StatusProject).where(StatusProject.id == project.status_project_id))
    status_project = status_project_result.scalar_one_or_none()

    if not status_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le statut de projet spécifié n'existe pas")

    # Vérifier si la ville existe (si spécifiée)
    if project.city_id:
        city_result = await db.execute(select(City).where(City.id == project.city_id))
        city = city_result.scalar_one_or_none()

        if not city:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La ville spécifiée n'existe pas")

    # Vérifier si la devise existe (si spécifiée)
    if project.currency_id:
        currency_result = await db.execute(select(Currency).where(Currency.id == project.currency_id))
        currency = currency_result.scalar_one_or_none()

        if not currency:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La devise spécifiée n'existe pas")

    # Vérifier si un projet avec le même titre existe déjà pour cet utilisateur
    existing_project = await db.execute(
        select(Project).where(Project.title == project.title, Project.user_id == current_user.id)
    )
    if existing_project.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vous avez déjà un projet avec ce titre")

    # Créer le projet
    db_project = Project(
        title=project.title,
        description=project.description,
        budget=project.budget,
        user_id=current_user.id,
        status_project_id=project.status_project_id,
        city_id=project.city_id,
        currency_id=project.currency_id,
        begin_at=project.begin_at,
        end_at=project.end_at,
    )

    # Ajouter le projet à la base de données
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)

    # Récupérer le projet avec tous ses détails
    project_result = await db.execute(
        select(Project)
        .options(
            joinedload(Project.status_project),
            joinedload(Project.city),
            joinedload(Project.currency),
            joinedload(Project.steps),
        )
        .where(Project.id == db_project.id)
    )

    return project_result.scalar_one()


@router.get("/{project_id}", response_model=ProjectWithDetails)
async def get_project(
    project_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer un projet par son ID."""
    # Récupérer le projet avec ses détails
    project_result = await db.execute(
        select(Project)
        .options(
            joinedload(Project.status_project),
            joinedload(Project.city),
            joinedload(Project.currency),
            joinedload(Project.steps),
        )
        .where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()

    # Vérifier si le projet existe
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet non trouvé")

    # Vérifier si l'utilisateur a le droit de voir ce projet
    if project.user_id != current_user.id and not current_user.has_permission("ReadProject"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de voir ce projet")

    return project


@router.put("/{project_id}", response_model=ProjectWithDetails)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Mettre à jour un projet."""
    # Récupérer le projet
    project_result = await db.execute(
        select(Project).options(joinedload(Project.steps)).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()

    # Vérifier si le projet existe
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet non trouvé")

    # Vérifier si l'utilisateur a le droit de modifier ce projet
    if project.user_id != current_user.id and not current_user.has_permission("UpdateProject"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de modifier ce projet"
        )

    # Vérifier que l'ID du projet dans le body correspond à l'ID dans l'URL
    if project_update.id != project_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="L'identifiant du projet ne correspond pas")

    # Vérifier si un autre projet avec le même titre existe déjà pour cet utilisateur
    if project_update.title != project.title:
        existing_project = await db.execute(
            select(Project).where(
                Project.title == project_update.title, Project.user_id == current_user.id, Project.id != project_id
            )
        )
        if existing_project.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Vous avez déjà un projet avec ce titre"
            )

    # Vérifier que le nouveau budget est supérieur ou égal au budget déjà alloué
    allocated_budget = sum(step.budget for step in project.steps)
    if project_update.budget < allocated_budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau budget doit être supérieur ou égal au budget déjà alloué",
        )

    # Mettre à jour le projet
    project.title = project_update.title
    project.description = project_update.description
    project.budget = project_update.budget
    project.status_project_id = project_update.status_project_id
    project.city_id = project_update.city_id
    project.currency_id = project_update.currency_id
    project.begin_at = project_update.begin_at
    project.end_at = project_update.end_at

    await db.commit()
    await db.refresh(project)

    # Récupérer le projet mis à jour avec tous ses détails
    updated_project_result = await db.execute(
        select(Project)
        .options(
            joinedload(Project.status_project),
            joinedload(Project.city),
            joinedload(Project.currency),
            joinedload(Project.steps),
        )
        .where(Project.id == project_id)
    )

    return updated_project_result.scalar_one()


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """Supprimer un projet."""
    # Récupérer le projet
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()

    # Vérifier si le projet existe
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet non trouvé")

    # Vérifier si l'utilisateur a le droit de supprimer ce projet
    if project.user_id != current_user.id and not current_user.has_permission("DeleteProject"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de supprimer ce projet"
        )

    # Supprimer le projet
    await db.delete(project)
    await db.commit()


@router.get("/{project_id}/steps", response_model=List[StepInDB])
async def get_project_steps(
    project_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer toutes les étapes d'un projet."""
    # Récupérer le projet
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()

    # Vérifier si le projet existe
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet non trouvé")

    # Vérifier si l'utilisateur a le droit de voir les étapes de ce projet
    if project.user_id != current_user.id and not current_user.has_permission("ListStep"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de voir les étapes de ce projet"
        )

    # Récupérer les étapes du projet
    steps_result = await db.execute(select(Step).where(Step.project_id == project_id))
    steps = steps_result.scalars().all()

    return steps


@router.post("/{project_id}/steps", response_model=StepInDB, status_code=status.HTTP_201_CREATED)
async def create_project_step(
    project_id: int,
    step: StepCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Créer une nouvelle étape pour un projet."""
    # Récupérer le projet
    project_result = await db.execute(
        select(Project).options(joinedload(Project.steps)).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()

    # Vérifier si le projet existe
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet non trouvé")

    # Vérifier si le projet est terminé
    if project.status_project_id == 3:  # ID du statut "Terminé"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le projet est terminé")

    # Vérifier si l'utilisateur a le droit de créer une étape pour ce projet
    if project.user_id != current_user.id and not current_user.has_permission("CreateOtherStep"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de créer une étape pour ce projet"
        )

    # Vérifier si une étape avec le même titre existe déjà pour ce projet
    existing_step = await db.execute(select(Step).where(Step.title == step.title, Step.project_id == project_id))
    if existing_step.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce projet a déjà une étape avec ce titre")

    # Vérifier si le numéro d'étape est valide
    if step.number > len(project.steps) + 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le numéro de l'étape est supérieur au nombre d'étapes du projet",
        )

    # Vérifier si le budget n'est pas supérieur au budget non alloué du projet
    if step.budget > project.unallocated_budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le budget de l'étape est supérieur au budget non alloué du projet",
        )

    # Mettre à jour les numéros d'étapes existantes si nécessaire
    for existing_step in project.steps:
        if existing_step.number >= step.number:
            existing_step.number += 1

    # Créer l'étape
    db_step = Step(
        title=step.title,
        description=step.description,
        number=step.number,
        budget=step.budget,
        project_id=project_id,
        creator_id=current_user.id,
        begin_at=step.begin_at,
        end_at=step.end_at,
    )

    # Ajouter l'étape à la base de données
    db.add(db_step)
    await db.commit()

    # Mettre à jour les étapes existantes
    for existing_step in project.steps:
        if existing_step.id != db_step.id and existing_step.number >= step.number:
            await db.execute(update(Step).where(Step.id == existing_step.id).values(number=existing_step.number))

    await db.commit()
    await db.refresh(db_step)

    return db_step


@router.get("/{project_id}/steps/{step_id}", response_model=StepInDB)
async def get_project_step(
    project_id: int, step_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer une étape d'un projet."""
    # Récupérer l'étape
    step_result = await db.execute(select(Step).options(joinedload(Step.project)).where(Step.id == step_id))
    step = step_result.scalar_one_or_none()

    # Vérifier si l'étape existe
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Étape non trouvée")

    # Vérifier si l'étape appartient au projet spécifié
    if step.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cette étape n'appartient pas au projet spécifié"
        )

    # Vérifier si l'utilisateur a le droit de voir cette étape
    if step.project.user_id != current_user.id and not current_user.has_permission("ReadStep"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de voir cette étape"
        )

    return step


@router.put("/{project_id}/steps/{step_id}", response_model=StepInDB)
async def update_project_step(
    project_id: int,
    step_id: int,
    step_update: StepUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Mettre à jour une étape d'un projet."""
    # Récupérer l'étape
    step_result = await db.execute(select(Step).options(joinedload(Step.project)).where(Step.id == step_id))
    step = step_result.scalar_one_or_none()

    # Vérifier si l'étape existe
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Étape non trouvée")

    # Vérifier si l'étape appartient au projet spécifié
    if step.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cette étape n'appartient pas au projet spécifié"
        )

    # Vérifier si l'utilisateur a le droit de modifier cette étape
    if step.project.user_id != current_user.id and not current_user.has_permission("UpdateStep"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de modifier cette étape"
        )

    # Vérifier que l'ID de l'étape dans le body correspond à l'ID dans l'URL
    if step_update.id != step_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="L'identifiant de l'étape ne correspond pas"
        )

    # Récupérer le projet
    project_result = await db.execute(
        select(Project).options(joinedload(Project.steps)).where(Project.id == project_id)
    )
    project = project_result.scalar_one()

    # Vérifier si une autre étape du projet a le même titre
    if step_update.title != step.title:
        existing_step = await db.execute(
            select(Step).where(Step.title == step_update.title, Step.project_id == project_id, Step.id != step_id)
        )
        if existing_step.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Ce projet a déjà une autre étape avec ce titre"
            )

    # Vérifier si le nouveau budget n'est pas supérieur au budget non alloué du projet + budget actuel de l'étape
    if step_update.budget > project.unallocated_budget + step.budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau budget doit être inférieur ou égal au budget non alloué du projet + budget actuel de l'étape",
        )

    # Vérifier si le nouveau numéro est valide
    if step_update.number > len(project.steps):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau numéro doit être inférieur ou égal au nombre d'étapes du projet",
        )

    # Gérer le changement de numéro d'étape
    old_number = step.number
    new_number = step_update.number

    if old_number != new_number:
        # Mettre à jour les numéros des autres étapes
        for other_step in project.steps:
            if other_step.id != step_id:
                if old_number < new_number and other_step.number > old_number and other_step.number <= new_number:
                    other_step.number -= 1
                elif old_number > new_number and other_step.number >= new_number and other_step.number < old_number:
                    other_step.number += 1

    # Mettre à jour l'étape
    step.title = step_update.title
    step.description = step_update.description
    step.number = new_number
    step.budget = step_update.budget
    step.begin_at = step_update.begin_at
    step.end_at = step_update.end_at

    await db.commit()

    # Mettre à jour les numéros des autres étapes en base de données
    for other_step in project.steps:
        if other_step.id != step_id:
            await db.execute(update(Step).where(Step.id == other_step.id).values(number=other_step.number))

    await db.commit()
    await db.refresh(step)

    return step


@router.delete("/{project_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_step(
    project_id: int, step_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """Supprimer une étape d'un projet."""
    # Récupérer l'étape
    step_result = await db.execute(select(Step).options(joinedload(Step.project)).where(Step.id == step_id))
    step = step_result.scalar_one_or_none()

    # Vérifier si l'étape existe
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Étape non trouvée")

    # Vérifier si l'étape appartient au projet spécifié
    if step.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cette étape n'appartient pas au projet spécifié"
        )

    # Vérifier si l'utilisateur a le droit de supprimer cette étape
    if step.project.user_id != current_user.id and not current_user.has_permission("DeleteStep"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de supprimer cette étape"
        )

    # Vérifier si le projet est terminé
    if step.project.status_project_id == 3:  # ID du statut "Terminé"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le projet est terminé")

    # Récupérer le numéro de l'étape avant de la supprimer
    step_number = step.number

    # Supprimer l'étape
    await db.delete(step)
    await db.commit()

    # Mettre à jour les numéros des étapes suivantes
    steps_to_update = await db.execute(select(Step).where(Step.project_id == project_id, Step.number > step_number))

    for s in steps_to_update.scalars().all():
        s.number -= 1

    await db.commit()
