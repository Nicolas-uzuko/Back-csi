from datetime import datetime
from typing import Optional, TYPE_CHECKING
import enum

from sqlalchemy import BigInteger, CheckConstraint, Enum as SAEnum, Identity, Index, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.historique_action import HistoriqueAction


class RoleUtilisateur(str, enum.Enum):
    ADMIN = "ADMIN"
    UTILISATEUR = "UTILISATEUR"


class StatutUtilisateur(str, enum.Enum):
    ACTIF = "ACTIF"
    DESACTIVE = "DESACTIVE"


class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    __table_args__ = (
        CheckConstraint(
            "telephone ~ '^[0-9]{10}$' OR telephone IS NULL",
            name="ck_utilisateurs_telephone_format",
        ),
        Index("ix_utilisateurs_email", "email"),
        Index("ix_utilisateurs_nom_utilisateur", "nom_utilisateur"),
        Index("ix_utilisateurs_matricule", "matricule"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    matricule: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    nom_utilisateur: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    telephone: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    mot_de_passe_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleUtilisateur] = mapped_column(
        SAEnum(RoleUtilisateur, name="role_utilisateur_enum", native_enum=True),
        nullable=False,
        default=RoleUtilisateur.UTILISATEUR,
        server_default="UTILISATEUR",
    )
    statut: Mapped[StatutUtilisateur] = mapped_column(
        SAEnum(StatutUtilisateur, name="statut_utilisateur_enum", native_enum=True),
        nullable=False,
        default=StatutUtilisateur.ACTIF,
        server_default="ACTIF",
    )
    date_creation: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    date_modification: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Only the SHA-256 hash is stored. The clear reset token is never persisted.
    reset_token_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    reset_token_expire: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    documents_importes: Mapped[list["Document"]] = relationship(
        "Document", back_populates="importe_par", foreign_keys="Document.importe_par_id"
    )
    historique_actions: Mapped[list["HistoriqueAction"]] = relationship(
        "HistoriqueAction", back_populates="utilisateur", foreign_keys="HistoriqueAction.utilisateur_id"
    )
