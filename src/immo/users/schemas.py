"""Schémas Pydantic pour la validation des données utilisateur."""

import re

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# Schémas pour les rôles
class RoleBase(BaseModel):
    """Schéma de base pour un rôle."""

    name: str = Field(..., min_length=3, max_length=64)
    description: Optional[str] = Field(None, max_length=200)


class RoleCreate(RoleBase):
    """Schéma pour la création d'un rôle."""

    pass


class RoleUpdate(RoleBase):
    """Schéma pour la mise à jour d'un rôle."""

    pass


class RoleInDB(RoleBase):
    """Schéma pour la représentation d'un rôle en base de données."""

    id: int

    class Config:
        orm_mode = True


# Schémas pour les permissions
class PermissionBase(BaseModel):
    """Schéma de base pour une permission."""

    name: str = Field(..., min_length=3, max_length=64)
    description: Optional[str] = Field(None, max_length=200)


class PermissionCreate(PermissionBase):
    """Schéma pour la création d'une permission."""

    pass


class PermissionUpdate(PermissionBase):
    """Schéma pour la mise à jour d'une permission."""

    pass


class PermissionInDB(PermissionBase):
    """Schéma pour la représentation d'une permission en base de données."""

    id: int

    class Config:
        orm_mode = True


# Schémas pour les utilisateurs
class UserBase(BaseModel):
    """Schéma de base pour un utilisateur."""

    username: str = Field(..., min_length=3, max_length=15)
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)
    about_me: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur."""

    password: str = Field(..., min_length=6, max_length=36)
    confirm_password: str = Field(..., min_length=6, max_length=36)
    terms_confirmation: bool = Field(..., description="Acceptation des conditions d'utilisation")

    @field_validator("password")
    def password_valid(cls, v):
        """Validation du mot de passe."""
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@€$éàèç])[a-zA-Z\d@€$éàèç]{6,}$"
        if not re.match(pattern, v):
            raise ValueError(
                "Le mot de passe doit contenir au moins une minuscule, une majuscule, un chiffre et un caractère spécial"
            )
        return v

    @field_validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        """Validation que les mots de passe correspondent."""
        if "password" in values and v != values["password"]:
            raise ValueError("Les mots de passe ne correspondent pas")
        return v


class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'un utilisateur."""

    username: Optional[str] = Field(None, min_length=3, max_length=15)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)
    about_me: Optional[str] = Field(None, max_length=255)


class UserLogin(BaseModel):
    """Schéma pour la connexion d'un utilisateur."""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=36)
    remember_me: bool = False


class UserChangePassword(BaseModel):
    """Schéma pour le changement de mot de passe d'un utilisateur."""

    old_password: str
    password: str = Field(..., min_length=6, max_length=36)
    confirm_password: str = Field(..., min_length=6, max_length=36)

    @field_validator("password")
    def password_valid(cls, v):
        """Validation du mot de passe."""
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@€$éàèç])[a-zA-Z\d@€$éàèç]{6,}$"
        if not re.match(pattern, v):
            raise ValueError(
                "Le mot de passe doit contenir au moins une minuscule, une majuscule, un chiffre et un caractère spécial"
            )
        return v

    @field_validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        """Validation que les mots de passe correspondent."""
        if "password" in values and v != values["password"]:
            raise ValueError("Les mots de passe ne correspondent pas")
        return v


class Token(BaseModel):
    """Schéma pour un token d'accès."""

    access_token: str
    token_type: str = "bearer"
    ttl_access_token: int
    refresh_token: str
    ttl_refresh_token: int


class TokenPayload(BaseModel):
    """Schéma pour le contenu d'un token JWT."""

    sub: Optional[int] = None
    exp: Optional[int] = None


class UserInDB(UserBase):
    """Schéma pour la représentation d'un utilisateur en base de données."""

    id: int
    email_confirmed: bool
    created_at: datetime
    last_seen: datetime
    roles: List[RoleInDB] = []

    class Config:
        orm_mode = True


class UserWithToken(Token):
    """Schéma pour la représentation d'un utilisateur avec son token."""

    user: UserInDB
