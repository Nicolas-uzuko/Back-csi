from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _category_arrivee(value: str) -> str:
    if value not in ("/3", "/3S"):
        raise ValueError("La categorie doit etre /3 ou /3S")
    return value


def _archive(value: str) -> str:
    if value not in ("A", "B"):
        raise ValueError("La categorie d archive doit etre A ou B")
    return value


class CourrierArriveeCreate(BaseModel):
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
    # Identification
    numero_ordre: Optional[str] = Field(None, max_length=50)
    numero_piece: Optional[str] = Field(None, max_length=100)
    date_piece: Optional[date] = None
    date_reception: Optional[date] = None
    origine_piece: Optional[str] = Field(None, max_length=255)
    # Corps et traitement
    corps_message: Optional[str] = Field(None, description="Corps du message (texte entre les séparateurs X)")
    analyse: Optional[str] = None
    observation: Optional[str] = None

    _categorie = field_validator("categorie")(_category_arrivee)
    _archive = field_validator("categorie_archive")(_archive)


class CourrierArriveeUpdate(BaseModel):
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
    # Identification
    numero_ordre: Optional[str] = Field(None, max_length=50)
    numero_piece: Optional[str] = Field(None, max_length=100)
    date_piece: Optional[date] = None
    date_reception: Optional[date] = None
    origine_piece: Optional[str] = Field(None, max_length=255)
    # Corps et traitement
    corps_message: Optional[str] = None
    analyse: Optional[str] = None
    observation: Optional[str] = None

    _categorie = field_validator("categorie")(_category_arrivee)
    _archive = field_validator("categorie_archive")(_archive)


class CourrierArriveeRead(CourrierArriveeCreate):
    id_courrier: int
    model_config = {"from_attributes": True}


class CourrierArriveeList(BaseModel):
    items: list[CourrierArriveeRead]
    total: int
    skip: int
    limit: int
