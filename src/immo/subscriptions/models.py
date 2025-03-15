"""Modèles de données pour les abonnements."""

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from immo.extensions import Base


class NonUserSubscription(Base):
    """Modèle pour les souscriptions des utilisateurs non enregistrés."""

    __tablename__ = "non_user_subscriptions"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), index=True)
    names = Column(String(100))
    project_title = Column(String(64), index=True)
    project_location = Column(String(64))
    project_budget = Column(String(64))
    project_dateline = Column(Date, nullable=False)
    project_description = Column(String(1000))
    project_terms_confirmation = Column(Boolean, nullable=False)
    validated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    validated_subscription = relationship(
        "ValidatedNonUserSubscription", uselist=False, back_populates="subscription", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<NonUserSubscription {self.email}: {self.project_title}>"


class ValidatedNonUserSubscription(Base):
    """Modèle pour les souscriptions validées des utilisateurs non enregistrés."""

    __tablename__ = "validated_subscriptions"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), index=True)
    names = Column(String(100))
    project_title = Column(String(64), index=True)
    project_location = Column(String(64))
    project_budget = Column(Integer)
    project_budget_currency_id = Column(Integer, ForeignKey("currencies.id"))
    project_dateline = Column(Date, nullable=False)
    project_description = Column(String(1000))
    project_terms_confirmation = Column(Boolean, nullable=False)
    valid_until = Column(Date, nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("non_user_subscriptions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    subscription = relationship("NonUserSubscription", back_populates="validated_subscription")
    manager = relationship("User")
    currency = relationship("Currency")

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<ValidatedSubscription {self.email}: {self.project_title}, managed by {self.manager_id}>"


class FreeSubscription(Base):
    """Modèle pour les souscriptions gratuites."""

    __tablename__ = "free_subscriptions"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """Représentation de l'objet."""
        return f"<FreeSubscription {self.email}>"
