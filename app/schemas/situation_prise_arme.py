from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SituationPriseArmeCreate(BaseModel):
    effectif_realise: Optional[int] = Field(None, ge=0)
    absent: Optional[int] = Field(None, ge=0)
    present: Optional[int] = Field(None, ge=0)
    indisponible: Optional[int] = Field(None, ge=0)
    sur_le_rang: Optional[int] = Field(None, ge=0)
    motif_absent: Optional[str] = None
    motif_indisponible: Optional[str] = None
    date_situation: Optional[datetime] = None


class SituationPriseArmeUpdate(SituationPriseArmeCreate):
    pass


class SituationPriseArmeRead(SituationPriseArmeCreate):
    id_situation: int
    model_config = {"from_attributes": True}


class SituationPriseArmeList(BaseModel):
    items: list[SituationPriseArmeRead]
    total: int
    skip: int
    limit: int
