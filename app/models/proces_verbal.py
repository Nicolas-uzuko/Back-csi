from datetime import date
from typing import Optional

from sqlalchemy import BigInteger, Date, Identity, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProcesVerbal(Base):
    """Sensitive procès-verbal register protected by dedicated permissions."""

    __tablename__ = "proces_verbaux"
    __table_args__ = (
        Index("ix_proces_verbaux_numero_pv", "numero_pv"),
        Index("ix_proces_verbaux_date_piece", "date_piece"),
    )

    id_pv: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    numero_pv: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date_piece: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    noms_enqueteurs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    analyse_sommaire: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    personne_en_cause: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    nature_affaire: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    observations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
