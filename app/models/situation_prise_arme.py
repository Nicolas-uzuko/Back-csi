from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, Identity, Index, Integer, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SituationPriseArme(Base):
    """No equality relationship is assumed between the register counters."""

    __tablename__ = "situations_prise_arme"
    __table_args__ = (
        CheckConstraint("effectif_realise IS NULL OR effectif_realise >= 0", name="ck_situations_effectif_realise_positif"),
        CheckConstraint("absent IS NULL OR absent >= 0", name="ck_situations_absent_positif"),
        CheckConstraint("present IS NULL OR present >= 0", name="ck_situations_present_positif"),
        CheckConstraint("indisponible IS NULL OR indisponible >= 0", name="ck_situations_indisponible_positif"),
        CheckConstraint("sur_le_rang IS NULL OR sur_le_rang >= 0", name="ck_situations_sur_le_rang_positif"),
        Index("ix_situations_prise_arme_date_situation", "date_situation"),
    )

    id_situation: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    effectif_realise: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    absent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    present: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    indisponible: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sur_le_rang: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    motif_absent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    motif_indisponible: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_situation: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
