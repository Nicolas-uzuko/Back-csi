from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ProcesVerbalCreate(BaseModel):
    numero_pv: Optional[str] = Field(None, max_length=100)
    date_piece: Optional[date] = None
    noms_enqueteurs: Optional[str] = None
    analyse_sommaire: Optional[str] = None
    personne_en_cause: Optional[str] = Field(None, max_length=255)
    nature_affaire: Optional[str] = Field(None, max_length=255)
    observations: Optional[str] = None


class ProcesVerbalUpdate(ProcesVerbalCreate):
    pass


class ProcesVerbalRead(ProcesVerbalCreate):
    id_pv: int
    model_config = {"from_attributes": True}


class ProcesVerbalList(BaseModel):
    items: list[ProcesVerbalRead]
    total: int
    skip: int
    limit: int
