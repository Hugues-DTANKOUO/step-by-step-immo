"""Modèles de données pour les services."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from immo.extensions import Base


class Service(Base):
    """Modèle de données pour les services."""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    title = Column(String(64), index=True)
    description = Column(String(1000))
    price = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    provider = relationship("User", back_populates="services")

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<Service {self.title}>"
