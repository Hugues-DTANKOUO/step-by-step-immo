"""Modèles de données pour les utilitaires."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from immo.extensions import Base


class Country(Base):
    """Modèle de données pour les pays."""

    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True)
    code = Column(String(2), index=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relations
    cities = relationship("City", back_populates="country", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<Country {self.name}>"


class City(Base):
    """Modèle de données pour les villes."""

    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True)
    country_id = Column(Integer, ForeignKey("countries.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relations
    country = relationship("Country", back_populates="cities")
    projects = relationship("Project", back_populates="city")

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<City {self.name}>"


class Currency(Base):
    """Modèle de données pour les devises."""

    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True)
    code = Column(String(5), index=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relations
    projects = relationship("Project", back_populates="currency")

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<Currency {self.name}>"


class StatusProject(Base):
    """Modèle de données pour les statuts des projets."""

    __tablename__ = "status_projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True)
    description = Column(String(200))

    # Relations
    projects = relationship("Project", back_populates="status_project")

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<StatusProject {self.name}>"
