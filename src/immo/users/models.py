"""Modèles de données pour les utilisateurs."""

from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from immo.extensions import Base


# Contexte pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Table de liaison entre utilisateurs et rôles
user_role = Table(
    "user_roles",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)

# Table de liaison entre rôles et permissions
role_permission = Table(
    "role_permissions",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id")),
    Column("permission_id", Integer, ForeignKey("permissions.id")),
)


class User(Base):
    """Modèle de données pour les utilisateurs."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, index=True)
    first_name = Column(String(64), nullable=True)
    last_name = Column(String(64), nullable=True)
    email = Column(String(120), unique=True, index=True)
    email_confirmed = Column(Boolean, default=False)
    password_hash = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    about_me = Column(String(255), nullable=True)
    terms_confirmation = Column(Boolean, default=False)

    # Relations
    projects = relationship("Project", back_populates="author", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="provider", cascade="all, delete-orphan")
    roles = relationship("Role", secondary=user_role, back_populates="users")

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Définir le mot de passe de l'utilisateur."""
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Vérifier le mot de passe de l'utilisateur."""
        return pwd_context.verify(password, self.password_hash)

    def update_last_seen(self) -> None:
        """Mettre à jour la date de dernière visite."""
        self.last_seen = datetime.utcnow()

    def has_role(self, role_name: str) -> bool:
        """Vérifier si l'utilisateur a un rôle spécifique."""
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        """Vérifier si l'utilisateur a une permission spécifique."""
        return any(any(permission.name == permission_name for permission in role.permissions) for role in self.roles)

    @property
    def is_admin(self) -> bool:
        """Vérifier si l'utilisateur est administrateur."""
        return self.has_role("Admin") or self.has_role("SuperAdmin")

    @property
    def is_super_admin(self) -> bool:
        """Vérifier si l'utilisateur est super administrateur."""
        return self.has_role("SuperAdmin")


class Role(Base):
    """Modèle de données pour les rôles."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)
    description = Column(String(200), nullable=True)

    # Relations
    users = relationship("User", secondary=user_role, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permission, back_populates="roles")

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<Role {self.name}>"


class Permission(Base):
    """Modèle de données pour les permissions."""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)
    description = Column(String(200), nullable=True)

    # Relations
    roles = relationship("Role", secondary=role_permission, back_populates="permissions")

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<Permission {self.name}>"
