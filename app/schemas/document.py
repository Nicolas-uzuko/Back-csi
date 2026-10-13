from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.document import (
    CategorieArchive,
    ModeConservation,
    TypeConfidentialite,
    TYPES_DOCUMENTS_AUTORISES,
    TYPES_DOCUMENTS_CATEGORIE_A,
    TYPES_DOCUMENTS_CATEGORIE_B,
)


def _validate_classification(category: CategorieArchive, type_document: str, confidentiality: TypeConfidentialite) -> None:
    expected_types = TYPES_DOCUMENTS_CATEGORIE_A if category == CategorieArchive.A else TYPES_DOCUMENTS_CATEGORIE_B
    if type_document not in expected_types:
        raise ValueError("Type de document incompatible avec la categorie d archive")
    expected_confidentiality = TypeConfidentialite.NON_CONFIDENTIEL if category == CategorieArchive.A else TypeConfidentialite.CONFIDENTIEL
    if confidentiality != expected_confidentiality:
        raise ValueError("Confidentialite incompatible avec la categorie d archive")


class DocumentCreate(BaseModel):
    table_source: Optional[str] = Field(None, max_length=100)
    id_source: Optional[int] = Field(None, gt=0)
    categorie_archive: CategorieArchive
    type_document: str = Field(..., max_length=100)
    confidentialite: TypeConfidentialite
    mode_conservation: ModeConservation = ModeConservation.PHYSIQUE
    emplacement_physique: Optional[str] = Field(None, max_length=500)

    @field_validator("type_document")
    @classmethod
    def type_autorise(cls, value: str) -> str:
        if value not in TYPES_DOCUMENTS_AUTORISES:
            raise ValueError("Type de document non autorise")
        return value

    @model_validator(mode="after")
    def source_coherente(self):
        if (self.table_source is None) != (self.id_source is None):
            raise ValueError("table_source et id_source doivent etre fournis ensemble")
        if self.mode_conservation != ModeConservation.PHYSIQUE:
            raise ValueError("Un fichier numerique doit etre importe par l endpoint upload")
        if not self.emplacement_physique:
            raise ValueError("emplacement_physique est obligatoire pour PHYSIQUE")
        _validate_classification(self.categorie_archive, self.type_document, self.confidentialite)
        return self


class DocumentUploadMetadata(BaseModel):
    table_source: Optional[str] = Field(None, max_length=100)
    id_source: Optional[int] = Field(None, gt=0)
    categorie_archive: CategorieArchive
    type_document: str = Field(..., max_length=100)
    confidentialite: TypeConfidentialite
    mode_conservation: ModeConservation
    emplacement_physique: Optional[str] = Field(None, max_length=500)

    @field_validator("type_document")
    @classmethod
    def type_autorise(cls, value: str) -> str:
        if value not in TYPES_DOCUMENTS_AUTORISES:
            raise ValueError("Type de document non autorise")
        return value

    @model_validator(mode="after")
    def upload_coherent(self):
        if (self.table_source is None) != (self.id_source is None):
            raise ValueError("table_source et id_source doivent etre fournis ensemble")
        if self.mode_conservation == ModeConservation.PHYSIQUE:
            raise ValueError("PHYSIQUE ne necessite pas de fichier upload")
        if self.mode_conservation == ModeConservation.MIXTE and not self.emplacement_physique:
            raise ValueError("emplacement_physique est obligatoire pour MIXTE")
        _validate_classification(self.categorie_archive, self.type_document, self.confidentialite)
        return self


class DocumentUpdate(BaseModel):
    categorie_archive: Optional[CategorieArchive] = None
    type_document: Optional[str] = Field(None, max_length=100)
    confidentialite: Optional[TypeConfidentialite] = None
    emplacement_physique: Optional[str] = Field(None, max_length=500)

    @field_validator("type_document")
    @classmethod
    def type_autorise(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in TYPES_DOCUMENTS_AUTORISES:
            raise ValueError("Type de document non autorise")
        return value


class DocumentRead(BaseModel):
    id_document: int
    table_source: Optional[str] = None
    id_source: Optional[int] = None
    categorie_archive: CategorieArchive
    type_document: str
    confidentialite: TypeConfidentialite
    mode_conservation: ModeConservation
    emplacement_physique: Optional[str] = None
    nom_original: Optional[str] = None
    extension: Optional[str] = None
    mime_type: Optional[str] = None
    taille_octets: Optional[int] = None
    sha256: Optional[str] = None
    date_import: datetime
    importe_par_id: Optional[int] = None

    model_config = {"from_attributes": True}


class DocumentList(BaseModel):
    items: list[DocumentRead]
    total: int
    skip: int
    limit: int
