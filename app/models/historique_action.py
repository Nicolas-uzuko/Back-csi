from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Identity, Index, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.utilisateur import Utilisateur


class HistoriqueAction(Base):
    """Append-only audit record. Sensitive values are redacted by the audit service."""

    __tablename__ = "historique_actions"
    __table_args__ = (
        Index("ix_historique_actions_date_action", "date_action"),
        Index("ix_historique_actions_utilisateur_id", "utilisateur_id"),
        Index("ix_historique_actions_table_cible", "table_cible"),
        Index("ix_historique_actions_action", "action"),
        Index("ix_historique_actions_succes", "succes"),
    )

    id_historique: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    utilisateur_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("utilisateurs.id", ondelete="SET NULL"), nullable=True)
    identifiant_utilisateur: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    table_cible: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    id_enregistrement_cible: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date_action: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    adresse_ip: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    succes: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    utilisateur: Mapped[Optional["Utilisateur"]] = relationship("Utilisateur", back_populates="historique_actions", foreign_keys=[utilisateur_id])
