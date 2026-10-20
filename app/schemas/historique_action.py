from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, field_validator


class HistoriqueActionRead(BaseModel):
    id_historique: int
    utilisateur_id: Optional[int] = None
    identifiant_utilisateur: Optional[str] = None
    action: str
    table_cible: Optional[str] = None
    id_enregistrement_cible: Optional[str] = None
    date_action: datetime
    details: Optional[Any] = None
    adresse_ip: Optional[str] = None
    succes: Optional[bool] = None

    model_config = {"from_attributes": True}

    @field_validator("adresse_ip", mode="before")
    @classmethod
    def coerce_ip_to_str(cls, v: Any) -> Optional[str]:
        """SQLAlchemy retourne un objet IPv4Address/IPv6Address depuis INET (PostgreSQL).
        On le convertit en str pour satisfaire le schema Pydantic."""
        return str(v) if v is not None else None


class HistoriqueActionList(BaseModel):
    items: list[HistoriqueActionRead]
    total: int
    skip: int
    limit: int
