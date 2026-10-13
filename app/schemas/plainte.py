from typing import Optional

from pydantic import BaseModel, Field


class PlainteCreate(BaseModel):
    numero_ordre: Optional[str] = Field(None, max_length=50)
    nom_plaignant: Optional[str] = Field(None, max_length=255)
    nom_personne_en_cause: Optional[str] = Field(None, max_length=255)
    motif_plainte: Optional[str] = None
    lieu_acte: Optional[str] = Field(None, max_length=255)
    telephone_plaignant: Optional[str] = Field(None, max_length=30)
    observation: Optional[str] = None


class PlainteUpdate(PlainteCreate):
    pass


class PlainteRead(PlainteCreate):
    id_plainte: int
    model_config = {"from_attributes": True}


class PlainteList(BaseModel):
    items: list[PlainteRead]
    total: int
    skip: int
    limit: int
