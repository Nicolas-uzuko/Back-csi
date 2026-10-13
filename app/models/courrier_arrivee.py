from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, CHAR, CheckConstraint, Date, Identity, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CourrierArrivee(Base):
    """Registre des courriers reçus (Messages Radio entrants, catégorie /3 ou /3S).

    Champs alignés sur le format Message Radio GN :
    - heure_depart : champ HD du message
    - priorite     : indicateur de priorité (-P-, -U-, -R-)
    - indicatif    : HVRC — indicatif radio de l'émetteur
    - corps_message: texte du message (entre les séparateurs X)

    The meaning of FM, TO and INFO is intentionally not inferred and must be
    validated by CSI Sakaraha managers.
    """

    __tablename__ = "courriers_arrivee"
    __table_args__ = (
        CheckConstraint("categorie IN ('/3', '/3S')", name="ck_courriers_arrivee_categorie"),
        CheckConstraint("categorie_archive IN ('A', 'B')", name="ck_courriers_arrivee_categorie_archive"),
        Index("ix_courriers_arrivee_date_reception", "date_reception"),
        Index("ix_courriers_arrivee_categorie", "categorie"),
        Index("ix_courriers_arrivee_numero_ordre", "numero_ordre"),
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
    # Identification de la pièce
    numero_ordre: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    numero_piece: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date_piece: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    date_reception: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    origine_piece: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # Corps et traitement
    corps_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    analyse: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
