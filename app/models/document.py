from datetime import datetime
from typing import Optional, TYPE_CHECKING
import enum

from sqlalchemy import BigInteger, CheckConstraint, Enum as SAEnum, ForeignKey, Identity, Index, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.utilisateur import Utilisateur


class CategorieArchive(str, enum.Enum):
    A = "A"
    B = "B"


class TypeConfidentialite(str, enum.Enum):
    NON_CONFIDENTIEL = "NON_CONFIDENTIEL"
    CONFIDENTIEL = "CONFIDENTIEL"


class ModeConservation(str, enum.Enum):
    PHYSIQUE = "PHYSIQUE"
    NUMERIQUE = "NUMERIQUE"
    MIXTE = "MIXTE"


TYPES_DOCUMENTS_AUTORISES = (
    "CORRESPONDANCE_ARRIVEE_3", "CAHIER_ENREGISTREMENT_3", "COPIE_CORRESPONDANCE_2",
    "AVIS_MUTATION", "ORDRE_GENDARMERIE_NATIONALE", "REGISTRE_PERMISSIONNAIRES",
    "CORRESPONDANCE_ARRIVEE_3S", "CAHIER_ENREGISTREMENT_3S", "COPIE_CORRESPONDANCE_4",
    "ARCHIVE_PROCES_VERBAL", "REGISTRE_PROCES_VERBAUX", "CAHIER_SERVICE", "BULLETIN_SERVICE",
)
TYPES_DOCUMENTS_CATEGORIE_A = frozenset(TYPES_DOCUMENTS_AUTORISES[:6])
TYPES_DOCUMENTS_CATEGORIE_B = frozenset(TYPES_DOCUMENTS_AUTORISES[6:])


class Document(Base):
    """Common archive metadata and an index of files stored outside public web roots.

    The source pair is deliberately polymorphic because no business FK between
    every possible document and register was validated. The importer FK is real.
    """

    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "(table_source IS NULL AND id_source IS NULL) OR "
            "(table_source IN ('courriers_arrivee', 'courriers_depart', 'plaintes', 'proces_verbaux', 'services_courants', 'situations_prise_arme') AND id_source IS NOT NULL)",
            name="ck_documents_source_coherente",
        ),
        CheckConstraint(
            "type_document IN ('CORRESPONDANCE_ARRIVEE_3', 'CAHIER_ENREGISTREMENT_3', 'COPIE_CORRESPONDANCE_2', 'AVIS_MUTATION', 'ORDRE_GENDARMERIE_NATIONALE', 'REGISTRE_PERMISSIONNAIRES', 'CORRESPONDANCE_ARRIVEE_3S', 'CAHIER_ENREGISTREMENT_3S', 'COPIE_CORRESPONDANCE_4', 'ARCHIVE_PROCES_VERBAL', 'REGISTRE_PROCES_VERBAUX', 'CAHIER_SERVICE', 'BULLETIN_SERVICE')",
            name="ck_documents_type_document_autorise",
        ),
        CheckConstraint(
            "(categorie_archive = 'A' AND confidentialite = 'NON_CONFIDENTIEL' AND type_document IN ('CORRESPONDANCE_ARRIVEE_3', 'CAHIER_ENREGISTREMENT_3', 'COPIE_CORRESPONDANCE_2', 'AVIS_MUTATION', 'ORDRE_GENDARMERIE_NATIONALE', 'REGISTRE_PERMISSIONNAIRES')) OR "
            "(categorie_archive = 'B' AND confidentialite = 'CONFIDENTIEL' AND type_document IN ('CORRESPONDANCE_ARRIVEE_3S', 'CAHIER_ENREGISTREMENT_3S', 'COPIE_CORRESPONDANCE_4', 'ARCHIVE_PROCES_VERBAL', 'REGISTRE_PROCES_VERBAUX', 'CAHIER_SERVICE', 'BULLETIN_SERVICE'))",
            name="ck_documents_classification_coherente",
        ),
        CheckConstraint(
            "(mode_conservation = 'PHYSIQUE' AND emplacement_physique IS NOT NULL) OR "
            "(mode_conservation IN ('NUMERIQUE', 'MIXTE') AND nom_interne IS NOT NULL AND chemin_stockage IS NOT NULL)",
            name="ck_documents_conservation_coherente",
        ),
        CheckConstraint("taille_octets IS NULL OR taille_octets >= 0", name="ck_documents_taille_positive"),
        CheckConstraint("sha256 IS NULL OR sha256 ~ '^[0-9a-fA-F]{64}$'", name="ck_documents_sha256_format"),
        Index("ix_documents_table_source_id_source", "table_source", "id_source"),
        Index("ix_documents_confidentialite", "confidentialite"),
        Index("ix_documents_categorie_archive", "categorie_archive"),
        Index("ix_documents_date_import", "date_import"),
        Index("ix_documents_importe_par_id", "importe_par_id"),
    )

    id_document: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    table_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    id_source: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    categorie_archive: Mapped[CategorieArchive] = mapped_column(SAEnum(CategorieArchive, name="categorie_archive_enum"), nullable=False)
    type_document: Mapped[str] = mapped_column(String(100), nullable=False)
    confidentialite: Mapped[TypeConfidentialite] = mapped_column(SAEnum(TypeConfidentialite, name="type_confidentialite_enum"), nullable=False)
    mode_conservation: Mapped[ModeConservation] = mapped_column(SAEnum(ModeConservation, name="mode_conservation_enum"), nullable=False)
    emplacement_physique: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    nom_original: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    nom_interne: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    extension: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    chemin_stockage: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    taille_octets: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    date_import: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    importe_par_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("utilisateurs.id", ondelete="SET NULL"), nullable=True)
    importe_par: Mapped[Optional["Utilisateur"]] = relationship("Utilisateur", back_populates="documents_importes", foreign_keys=[importe_par_id])
