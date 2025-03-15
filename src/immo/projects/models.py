"""Modèles de données pour les projets."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from immo.extensions import Base


class Project(Base):
    """Modèle de données pour les projets."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String(64), index=True)
    description = Column(String(1000))
    budget = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    status_project_id = Column(Integer, ForeignKey("status_projects.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"))
    currency_id = Column(Integer, ForeignKey("currencies.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    begin_at = Column(DateTime)
    end_at = Column(DateTime)
    progress = Column(Integer, default=0)

    # Relations
    author = relationship("User", back_populates="projects")
    status_project = relationship("StatusProject", back_populates="projects")
    city = relationship("City", back_populates="projects")
    currency = relationship("Currency", back_populates="projects")
    steps = relationship("Step", back_populates="project", cascade="all, delete-orphan")

    # Contraintes
    __table_args__ = (UniqueConstraint("title", "user_id", name="_title_project_user_uc"),)

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<Project {self.title}>"

    @property
    def unallocated_budget(self) -> int:
        """Budget non alloué."""
        return int(self.budget - sum(step.budget for step in self.steps))


class Step(Base):
    """Modèle de données pour les étapes d'un projet."""

    __tablename__ = "steps"

    id = Column(Integer, primary_key=True)
    title = Column(String(64), index=True)
    description = Column(String(1000))
    number = Column(Integer, nullable=False)
    budget = Column(Integer, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    begin_at = Column(DateTime)
    end_at = Column(DateTime)
    progress = Column(Integer, default=0)

    # Relations
    project = relationship("Project", back_populates="steps")
    creator = relationship("User")

    # Contraintes
    __table_args__ = (UniqueConstraint("title", "project_id", name="_title_step_project_uc"),)

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<Step {self.title}>"
