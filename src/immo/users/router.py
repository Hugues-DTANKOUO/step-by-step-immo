"""Router pour les utilisateurs."""

from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from immo.config import settings
from immo.extensions import get_db
from immo.users.models import Role, User, user_role as UserRole
from immo.users.schemas import (
    Token,
    TokenPayload,
    UserChangePassword,
    UserCreate,
    UserInDB,
    UserUpdate,
    UserWithToken,
)


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Créer un token d'accès JWT."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + settings.access_token_expires

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Récupérer l'utilisateur connecté à partir du token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[int] = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        token_data = TokenPayload(sub=user_id, exp=payload.get("exp"))
    except JWTError:
        raise credentials_exception

    # Vérifier l'expiration du token
    if token_data.exp and datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
        raise credentials_exception

    result = await db.execute(select(User).options(joinedload(User.roles)).where(User.id == token_data.sub))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> Any:
    """Enregistrer un nouvel utilisateur."""
    # Vérifier si les conditions générales ont été acceptées
    if not user.terms_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Vous devez accepter les conditions générales d'utilisation"
        )

    # Vérifier si l'email ou le username existe déjà
    email_check = await db.execute(select(User).where(User.email == user.email))
    if email_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet email est déjà utilisé")

    username_check = await db.execute(select(User).where(User.username == user.username))
    if username_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce nom d'utilisateur est déjà utilisé")

    # Créer l'utilisateur
    db_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        about_me=user.about_me,
        terms_confirmation=user.terms_confirmation,
    )

    # Hacher le mot de passe
    db_user.set_password(user.password)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Attribuer le rôle 'User' (id=3) à l'utilisateur
    user_role_result = await db.execute(select(Role).where(Role.name == "User"))
    user_role = user_role_result.scalar_one_or_none()

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de l'attribution du rôle utilisateur"
        )

    db_user_role = UserRole(user_id=db_user.id, role_id=user_role.id)
    db.add(db_user_role)
    await db.commit()

    # Récupérer l'utilisateur avec ses rôles
    result = await db.execute(select(User).options(joinedload(User.roles)).where(User.id == db_user.id))
    created_user = result.scalar_one()

    return created_user


@router.post("/login", response_model=UserWithToken)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> Any:
    """Connecter un utilisateur."""
    user_result = await db.execute(select(User).options(joinedload(User.roles)).where(User.email == form_data.username))
    user = user_result.scalar_one_or_none()

    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Mettre à jour la date de dernière connexion
    user.update_last_seen()
    await db.commit()

    # Créer les tokens d'accès et de rafraîchissement
    access_token = await create_access_token(data={"sub": user.id}, expires_delta=settings.access_token_expires)

    refresh_token = await create_access_token(data={"sub": user.id}, expires_delta=settings.refresh_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "ttl_access_token": int(settings.access_token_expires.total_seconds()),
        "refresh_token": refresh_token,
        "ttl_refresh_token": int(settings.refresh_token_expires.total_seconds()),
        "user": user,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Any:
    """Rafraîchir le token d'accès."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[int] = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Vérifier si l'utilisateur existe
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Créer un nouveau token d'accès
        access_token = await create_access_token(data={"sub": user_id}, expires_delta=settings.access_token_expires)

        # Créer un nouveau token de rafraîchissement
        refresh_token = await create_access_token(data={"sub": user_id}, expires_delta=settings.refresh_token_expires)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "ttl_access_token": int(settings.access_token_expires.total_seconds()),
            "refresh_token": refresh_token,
            "ttl_refresh_token": int(settings.refresh_token_expires.total_seconds()),
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    """Récupérer les informations de l'utilisateur connecté."""
    return current_user


@router.put("/me", response_model=UserInDB)
async def update_user_me(
    user_update: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Mettre à jour les informations de l'utilisateur connecté."""
    # Vérifier si le nom d'utilisateur est déjà utilisé
    if user_update.username and user_update.username != current_user.username:
        username_check = await db.execute(select(User).where(User.username == user_update.username))
        if username_check.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce nom d'utilisateur est déjà utilisé")

    # Vérifier si l'email est déjà utilisé
    if user_update.email and user_update.email != current_user.email:
        email_check = await db.execute(select(User).where(User.email == user_update.email))
        if email_check.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet email est déjà utilisé")

    # Mettre à jour l'utilisateur
    if user_update.username:
        current_user.username = user_update.username
    if user_update.email:
        current_user.email = user_update.email
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    if user_update.about_me is not None:
        current_user.about_me = user_update.about_me

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Changer le mot de passe de l'utilisateur connecté."""
    # Vérifier l'ancien mot de passe
    if not current_user.verify_password(password_data.old_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ancien mot de passe incorrect")

    # Vérifier que les nouveaux mots de passe correspondent
    if password_data.password != password_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Les mots de passe ne correspondent pas")

    # Mettre à jour le mot de passe
    current_user.set_password(password_data.password)
    await db.commit()


@router.get("/{user_id}", response_model=UserInDB)
async def read_user(
    user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    """Récupérer les informations d'un utilisateur par son ID."""
    # Vérifier les permissions
    if user_id != current_user.id and not current_user.has_permission("ReadUser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'avez pas le droit de voir cet utilisateur"
        )

    # Récupérer l'utilisateur
    user_result = await db.execute(select(User).options(joinedload(User.roles)).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")

    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(current_user: User = Depends(get_current_user)) -> None:
    """Déconnecter l'utilisateur (côté client uniquement)."""
    # Rien à faire côté serveur (stateless)
    # La déconnexion se fait côté client en supprimant le token
    return None
