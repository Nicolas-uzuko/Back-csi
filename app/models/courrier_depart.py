from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, CHAR, CheckConstraint, Date, Identity, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CourrierDepart(Base):
    """Registre des courriers envoyés (Messages Radio sortants, catégorie /2 ou /4).

    Champs alignés sur le format Message Radio GN :
    - heure_depart : champ HD du message
    - priorite     : indicateur de priorité (-P-, -U-, -R-)
    - indicatif    : HVRC — indicatif radio de l'émetteur
    - corps_message: texte du message (entre les séparateurs X)

    ``ref`` remains separate from the technical primary key and its meaning is
    intentionally left for validation by CSI Sakaraha managers.
    """

    __tablename__ = "courriers_depart"
    __table_args__ = (
        CheckConstraint("categorie IN ('/2', '/4')", name="ck_courriers_depart_categorie"),
        CheckConstraint("categorie_archive IN ('A', 'B')", name="ck_courriers_depart_categorie_archive"),
        Index("ix_courriers_depart_date_envoi", "date_envoi"),
        Index("ix_courriers_depart_categorie", "categorie"),
        Index("ix_courriers_depart_reference_message", "reference_message"),
    )

    id_courrier: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    categorie: Mapped[str] = mapped_column(String(10), nullable=False)
    categorie_archive: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    # En-têtes FM / TO / INFO du message radio
    fm: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Champs d'en-tête du message radio (ligne HD / NR / priorité)
    heure_depart: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    priorite: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    indicatif: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Identification et objet
    reference_message: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    objet: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    date_piece: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Corps et expédition
    corps_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signataire: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_envoi: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
