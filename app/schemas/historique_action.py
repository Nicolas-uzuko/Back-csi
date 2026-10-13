from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class HistoriqueActionRead(BaseModel):
    id_historique: int
    utilisateur_id: Optional[int] = None
    identifiant_utilisateur: Optional[str] = None
    action: str
    table_cible: Optional[str] = None
    id_enregistrement_cible: Optional[str] = None
    date_action: datetime
    details: Optional[dict[str, Any]] = None
    adresse_ip: Optional[str] = None
    succes: Optional[bool] = None

    model_config = {"from_attributes": True}


class HistoriqueActionList(BaseModel):
    items: list[HistoriqueActionRead]
    total: int
    skip: int
    limit: int
