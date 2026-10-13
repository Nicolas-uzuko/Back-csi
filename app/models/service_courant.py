from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, Identity, Index, String, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ServiceCourant(Base):
    __tablename__ = "services_courants"
    __table_args__ = (
        CheckConstraint(
            "date_retour IS NULL OR date_depart IS NULL OR date_retour >= date_depart",
            name="ck_services_courants_dates_coherentes",
        ),
        Index("ix_services_courants_date_depart", "date_depart"),
        Index("ix_services_courants_numero_ordre", "numero_ordre"),
    )

    id_service: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    grade_nom: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type_arme: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tenue: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    moyen: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mission: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_depart: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    date_retour: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    numero_ordre: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    signataire: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
