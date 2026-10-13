from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _category_depart(value: str) -> str:
    if value not in ("/2", "/4"):
        raise ValueError("La categorie doit etre /2 ou /4")
    return value


def _archive(value: str) -> str:
    if value not in ("A", "B"):
        raise ValueError("La categorie d archive doit etre A ou B")
    return value


class CourrierDepartCreate(BaseModel):
    categorie: str = Field(..., max_length=10)
    categorie_archive: str = Field(..., min_length=1, max_length=1)
    # En-têtes FM / TO / INFO
    fm: Optional[str] = Field(None, max_length=255)
    to: Optional[str] = Field(None, max_length=255)
    info: Optional[str] = None
    # En-tête du message radio (HD / priorité / indicatif HVRC)
    heure_depart: Optional[str] = Field(None, max_length=20, description="Heure de départ (champ HD)")
    priorite: Optional[str] = Field(None, max_length=5, description="Priorité : P (Priorité), U (Urgent), R (Routine)")
    indicatif: Optional[str] = Field(None, max_length=100, description="Indicatif radio HVRC de l'émetteur")
    # Identification et objet
    reference_message: Optional[str] = Field(None, max_length=100)
    objet: Optional[str] = Field(None, max_length=500)
    date_piece: Optional[date] = None
    ref: Optional[str] = Field(None, max_length=100)
    # Corps et expédition
    corps_message: Optional[str] = Field(None, description="Corps du message (texte entre les séparateurs X)")
    observation: Optional[str] = None
    signataire: Optional[str] = Field(None, max_length=255)
    date_envoi: Optional[date] = None

    _categorie = field_validator("categorie")(_category_depart)
    _archive = field_validator("categorie_archive")(_archive)


class CourrierDepartUpdate(BaseModel):
    categorie: Optional[str] = Field(None, max_length=10)
    categorie_archive: Optional[str] = Field(None, min_length=1, max_length=1)
    # En-têtes FM / TO / INFO
    fm: Optional[str] = Field(None, max_length=255)
    to: Optional[str] = Field(None, max_length=255)
    info: Optional[str] = None
    # En-tête du message radio (HD / priorité / indicatif HVRC)
    heure_depart: Optional[str] = Field(None, max_length=20)
    priorite: Optional[str] = Field(None, max_length=5)
    indicatif: Optional[str] = Field(None, max_length=100)
    # Identification et objet
    reference_message: Optional[str] = Field(None, max_length=100)
    objet: Optional[str] = Field(None, max_length=500)
    date_piece: Optional[date] = None
    ref: Optional[str] = Field(None, max_length=100)
    # Corps et expédition
    corps_message: Optional[str] = None
    observation: Optional[str] = None
    signataire: Optional[str] = Field(None, max_length=255)
    date_envoi: Optional[date] = None

    _categorie = field_validator("categorie")(_category_depart)
    _archive = field_validator("categorie_archive")(_archive)


class CourrierDepartRead(CourrierDepartCreate):
    id_courrier: int
    model_config = {"from_attributes": True}


class CourrierDepartList(BaseModel):
    items: list[CourrierDepartRead]
    total: int
    skip: int
    limit: int
