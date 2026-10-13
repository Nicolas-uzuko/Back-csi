from typing import Optional

from sqlalchemy import BigInteger, Identity, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Plainte(Base):
    """Sensitive complaint register; endpoints require dedicated permissions."""

    __tablename__ = "plaintes"
    __table_args__ = (Index("ix_plaintes_numero_ordre", "numero_ordre"),)

    id_plainte: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    numero_ordre: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    nom_plaignant: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    nom_personne_en_cause: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    motif_plainte: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lieu_acte: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telephone_plaignant: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    observation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
