import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.utilisateur import RoleUtilisateur, StatutUtilisateur


def _validate_password(value: str) -> str:
    if not re.search(r"[A-Z]", value) or not re.search(r"[0-9]", value):
        raise ValueError("Le mot de passe doit contenir une majuscule et un chiffre")
    return value


class UtilisateurCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, max_length=100)
    matricule: Optional[str] = Field(None, max_length=50)
    nom_utilisateur: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    telephone: Optional[str] = Field(None, max_length=10)
    mot_de_passe: str = Field(..., min_length=8, max_length=128)
    role: RoleUtilisateur = RoleUtilisateur.UTILISATEUR

    @field_validator("telephone")
    @classmethod
    def telephone_valide(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not re.fullmatch(r"[0-9]{10}", value):
            raise ValueError("Le telephone doit contenir exactement 10 chiffres")
        return value

    @field_validator("nom_utilisateur")
    @classmethod
    def identifiant_valide(cls, value: str) -> str:
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", value):
            raise ValueError("Le nom utilisateur contient des caracteres invalides")
        return value

    _password = field_validator("mot_de_passe")(_validate_password)


class UtilisateurUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, max_length=100)
    matricule: Optional[str] = Field(None, max_length=50)
    nom_utilisateur: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    telephone: Optional[str] = Field(None, max_length=10)
    statut: Optional[StatutUtilisateur] = None

    @field_validator("telephone")
    @classmethod
    def telephone_valide(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not re.fullmatch(r"[0-9]{10}", value):
            raise ValueError("Le telephone doit contenir exactement 10 chiffres")
        return value


class UtilisateurChangeRole(BaseModel):
    role: RoleUtilisateur


class UtilisateurChangePassword(BaseModel):
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str = Field(..., min_length=8, max_length=128)
    _password = field_validator("nouveau_mot_de_passe")(_validate_password)


class UtilisateurRead(BaseModel):
    id: int
    nom: str
    prenom: Optional[str] = None
    matricule: Optional[str] = None
    nom_utilisateur: str
    email: str
    telephone: Optional[str] = None
    role: RoleUtilisateur
    statut: StatutUtilisateur
    date_creation: datetime
    date_modification: datetime

    model_config = {"from_attributes": True}


class UtilisateurList(BaseModel):
    items: list[UtilisateurRead]
    total: int
    skip: int
    limit: int
