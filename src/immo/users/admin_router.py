"""Router pour les fonctionnalités d'administration."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from immo.extensions import get_db
from immo.users.models import Permission, Role, User, role_permission, user_role
from immo.users.router import get_current_user
from immo.users.schemas import (
    PermissionCreate,
    PermissionInDB,
    PermissionUpdate,
    RoleCreate,
    RoleInDB,
    RoleUpdate,
    UserCreate,
    UserInDB,
)


router = APIRouter()


@router.post("/create-admin", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_admin(
    user: UserCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Créer un nouvel administrateur."""
    # Vérifier si l'utilisateur a le droit de créer un administrateur
    if not current_user.has_permission("CreateAdmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Vérifier si l'email ou le username existe déjà
    email_check = await db.execute(select(User).where(User.email == user.email))
    if email_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Adresse email déjà utilisée")

    username_check = await db.execute(select(User).where(User.username == user.username))
    if username_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nom d'utilisateur déjà utilisé")

    # Créer l'utilisateur
    db_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        about_me=user.about_me,
        email_confirmed=True,
        terms_confirmation=user.terms_confirmation,
    )

    # Définir le mot de passe
    db_user.set_password(user.password)

    # Sauvegarder l'utilisateur
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Récupérer le rôle Admin (id=2)
    admin_role_result = await db.execute(select(Role).where(Role.id == 2))
    admin_role = admin_role_result.scalar_one_or_none()

    if not admin_role:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Rôle Admin non trouvé")

    # Assigner le rôle Admin à l'utilisateur
    stmt = user_role.insert().values(user_id=db_user.id, role_id=admin_role.id)
    await db.execute(stmt)
    await db.commit()

    # Récupérer l'utilisateur avec ses rôles
    user_result = await db.execute(select(User).options(joinedload(User.roles)).where(User.id == db_user.id))
    created_user = user_result.scalar_one()

    return created_user


@router.get("/roles", response_model=List[RoleInDB])
async def get_roles(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Any:
    """Récupérer tous les rôles."""
    # Vérifier si l'utilisateur a le droit de voir les rôles
    if not current_user.has_permission("ListRole"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Récupérer tous les rôles
    roles_result = await db.execute(select(Role))
    roles = roles_result.scalars().all()

    return roles


@router.post("/roles", response_model=RoleInDB, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Créer un nouveau rôle."""
    # Vérifier si l'utilisateur a le droit de créer un rôle
    if not current_user.has_permission("CreateRole"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Vérifier si le rôle existe déjà
    role_check = await db.execute(select(Role).where(Role.name == role.name))
    if role_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce rôle existe déjà")

    # Créer le rôle
    db_role = Role(name=role.name, description=role.description)

    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)

    return db_role


@router.get("/roles/{role_id}", response_model=RoleInDB)
async def get_role(
    role_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer un rôle par son ID."""
    # Vérifier si l'utilisateur a le droit de voir ce rôle
    if not current_user.has_permission("ReadRole"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Récupérer le rôle
    role_result = await db.execute(select(Role).where(Role.id == role_id))
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle non trouvé")

    return role


@router.put("/roles/{role_id}", response_model=RoleInDB)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Mettre à jour un rôle."""
    # Vérifier si l'utilisateur a le droit de modifier ce rôle
    if not current_user.has_permission("UpdateRole"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Seul le super administrateur peut modifier les rôles ADMIN et SUPERADMIN
    if role_id in [1, 2] and not current_user.is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à modifier ce rôle")

    # Récupérer le rôle
    role_result = await db.execute(select(Role).where(Role.id == role_id))
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle non trouvé")

    # Vérifier si le nouveau nom n'est pas déjà utilisé par un autre rôle
    if role_update.name != role.name:
        role_check = await db.execute(select(Role).where(Role.name == role_update.name, Role.id != role_id))
        if role_check.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce nom de rôle est déjà utilisé")

    # Mettre à jour le rôle
    role.name = role_update.name
    role.description = role_update.description

    await db.commit()
    await db.refresh(role)

    return role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """Supprimer un rôle."""
    # Vérifier si l'utilisateur a le droit de supprimer ce rôle
    if not current_user.has_permission("DeleteRole"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Seul le super administrateur peut supprimer les quatre premiers rôles
    if role_id in range(1, 5) and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à supprimer ce rôle"
        )

    # Récupérer le rôle
    role_result = await db.execute(select(Role).where(Role.id == role_id))
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle non trouvé")

    # Supprimer le rôle
    await db.delete(role)
    await db.commit()


@router.get("/permissions", response_model=List[PermissionInDB])
async def get_permissions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Any:
    """Récupérer toutes les permissions."""
    # Vérifier si l'utilisateur a le droit de voir les permissions
    if not current_user.has_permission("ListPermission"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Récupérer toutes les permissions
    permissions_result = await db.execute(select(Permission))
    permissions = permissions_result.scalars().all()

    return permissions


@router.post("/permissions", response_model=PermissionInDB, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Créer une nouvelle permission."""
    # Vérifier si l'utilisateur a le droit de créer une permission
    if not current_user.has_permission("CreatePermission"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Vérifier si la permission existe déjà
    permission_check = await db.execute(select(Permission).where(Permission.name == permission.name))
    if permission_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette permission existe déjà")

    # Créer la permission
    db_permission = Permission(name=permission.name, description=permission.description)

    db.add(db_permission)
    await db.commit()
    await db.refresh(db_permission)

    return db_permission


@router.get("/permissions/{permission_id}", response_model=PermissionInDB)
async def get_permission(
    permission_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer une permission par son ID."""
    # Vérifier si l'utilisateur a le droit de voir cette permission
    if not current_user.has_permission("ReadPermission"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Récupérer la permission
    permission_result = await db.execute(select(Permission).where(Permission.id == permission_id))
    permission = permission_result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission non trouvée")

    return permission


@router.put("/permissions/{permission_id}", response_model=PermissionInDB)
async def update_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Mettre à jour une permission."""
    # Vérifier si l'utilisateur a le droit de modifier cette permission
    if not current_user.has_permission("UpdatePermission"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Seul le super administrateur peut modifier les 88 premières permissions
    if permission_id in range(1, 89) and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à modifier cette permission"
        )

    # Récupérer la permission
    permission_result = await db.execute(select(Permission).where(Permission.id == permission_id))
    permission = permission_result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission non trouvée")

    # Vérifier si le nouveau nom n'est pas déjà utilisé par une autre permission
    if permission_update.name != permission.name:
        permission_check = await db.execute(
            select(Permission).where(Permission.name == permission_update.name, Permission.id != permission_id)
        )
        if permission_check.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce nom de permission est déjà utilisé")

    # Mettre à jour la permission
    permission.name = permission_update.name
    permission.description = permission_update.description

    await db.commit()
    await db.refresh(permission)

    return permission


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """Supprimer une permission."""
    # Vérifier si l'utilisateur a le droit de supprimer cette permission
    if not current_user.has_permission("DeletePermission"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Seul le super administrateur peut supprimer les 88 premières permissions
    if permission_id in range(1, 89) and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à supprimer cette permission"
        )

    # Récupérer la permission
    permission_result = await db.execute(select(Permission).where(Permission.id == permission_id))
    permission = permission_result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission non trouvée")

    # Supprimer la permission
    await db.delete(permission)
    await db.commit()


@router.get("/roles/{role_id}/permissions", response_model=List[PermissionInDB])
async def get_role_permissions(
    role_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer toutes les permissions d'un rôle."""
    # Vérifier si l'utilisateur a le droit de voir les permissions d'un rôle
    if not current_user.has_permission("ListRolePermission"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Vérifier si le rôle existe
    role_result = await db.execute(select(Role).where(Role.id == role_id))
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle non trouvé")

    # Récupérer les permissions du rôle
    permissions_result = await db.execute(
        select(Permission)
        .join(role_permission, role_permission.c.permission_id == Permission.id)
        .where(role_permission.c.role_id == role_id)
    )
    permissions = permissions_result.scalars().all()

    return permissions


@router.post("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_permission_to_role(
    role_id: int, permission_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """Ajouter une permission à un rôle."""
    # Vérifier si l'utilisateur a le droit d'ajouter une permission à un rôle
    if not current_user.has_permission("CreateRolePermission"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Seul le super administrateur peut ajouter des permissions aux rôles ADMIN et SUPERADMIN
    if role_id in [1, 2] and not current_user.is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à modifier ce rôle")

    # Vérifier si le rôle existe
    role_result = await db.execute(select(Role).where(Role.id == role_id))
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle non trouvé")

    # Vérifier si la permission existe
    permission_result = await db.execute(select(Permission).where(Permission.id == permission_id))
    permission = permission_result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission non trouvée")

    # Vérifier si la permission est déjà attribuée au rôle
    role_permission_check = await db.execute(
        select(role_permission).where(
            role_permission.c.role_id == role_id, role_permission.c.permission_id == permission_id
        )
    )
    if role_permission_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cette permission est déjà attribuée à ce rôle"
        )

    # Ajouter la permission au rôle
    stmt = role_permission.insert().values(role_id=role_id, permission_id=permission_id)
    await db.execute(stmt)
    await db.commit()


@router.delete("/roles/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permission_from_role(
    role_id: int, permission_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """Supprimer une permission d'un rôle."""
    # Vérifier si l'utilisateur a le droit de supprimer une permission d'un rôle
    if not current_user.has_permission("DeleteRolePermission"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Seul le super administrateur peut supprimer des permissions des trois premiers rôles
    if role_id in range(1, 4) and not current_user.is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à modifier ce rôle")

    # Vérifier si le rôle existe
    role_result = await db.execute(select(Role).where(Role.id == role_id))
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle non trouvé")

    # Vérifier si la permission existe
    permission_result = await db.execute(select(Permission).where(Permission.id == permission_id))
    permission = permission_result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission non trouvée")

    # Vérifier si la permission est attribuée au rôle
    role_permission_check = await db.execute(
        select(role_permission).where(
            role_permission.c.role_id == role_id, role_permission.c.permission_id == permission_id
        )
    )
    if not role_permission_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cette permission n'est pas attribuée à ce rôle"
        )

    # Supprimer la permission du rôle
    stmt = delete(role_permission).where(
        role_permission.c.role_id == role_id, role_permission.c.permission_id == permission_id
    )
    await db.execute(stmt)
    await db.commit()


@router.get("/users/{user_id}/roles", response_model=List[RoleInDB])
async def get_user_roles(
    user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer tous les rôles d'un utilisateur."""
    # Vérifier si l'utilisateur a le droit de voir les rôles d'un utilisateur
    if not current_user.has_permission("ListUserRole") and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Vérifier si l'utilisateur existe
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")

    # Récupérer les rôles de l'utilisateur
    roles_result = await db.execute(
        select(Role).join(user_role, user_role.c.role_id == Role.id).where(user_role.c.user_id == user_id)
    )
    roles = roles_result.scalars().all()

    return roles


@router.post("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_role_to_user(
    user_id: int, role_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """Ajouter un rôle à un utilisateur."""
    # Vérifier si l'utilisateur a le droit d'ajouter un rôle à un utilisateur
    if not current_user.has_permission("CreateUserRole"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Seul le super administrateur peut ajouter les rôles ADMIN et SUPERADMIN
    if role_id in [1, 2] and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à attribuer ce rôle"
        )

    # Vérifier si l'utilisateur existe
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")

    # Vérifier si le rôle existe
    role_result = await db.execute(select(Role).where(Role.id == role_id))
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle non trouvé")

    # Vérifier si le rôle est déjà attribué à l'utilisateur
    user_role_check = await db.execute(
        select(user_role).where(user_role.c.user_id == user_id, user_role.c.role_id == role_id)
    )
    if user_role_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Ce rôle est déjà attribué à cet utilisateur"
        )

    # Ajouter le rôle à l'utilisateur
    stmt = user_role.insert().values(user_id=user_id, role_id=role_id)
    await db.execute(stmt)
    await db.commit()


@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_user(
    user_id: int, role_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    """Supprimer un rôle d'un utilisateur."""
    # Vérifier si l'utilisateur a le droit de supprimer un rôle d'un utilisateur
    if not current_user.has_permission("DeleteUserRole"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à effectuer cette action"
        )

    # Seul le super administrateur peut supprimer les rôles ADMIN et SUPERADMIN
    if role_id in [1, 2] and not current_user.is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas autorisé à retirer ce rôle")

    # Vérifier si l'utilisateur existe
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")

    # Vérifier si le rôle existe
    role_result = await db.execute(select(Role).where(Role.id == role_id))
    role = role_result.scalar_one_or_none()

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle non trouvé")

    # Vérifier si le rôle est attribué à l'utilisateur
    user_role_check = await db.execute(
        select(user_role).where(user_role.c.user_id == user_id, user_role.c.role_id == role_id)
    )
    if not user_role_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Ce rôle n'est pas attribué à cet utilisateur"
        )

    # Supprimer le rôle de l'utilisateur
    stmt = delete(user_role).where(user_role.c.user_id == user_id, user_role.c.role_id == role_id)
    await db.execute(stmt)
    await db.commit()
