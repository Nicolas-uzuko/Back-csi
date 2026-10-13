from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ServiceCourantCreate(BaseModel):
    grade_nom: Optional[str] = Field(None, max_length=255)
    type_arme: Optional[str] = Field(None, max_length=100)
    tenue: Optional[str] = Field(None, max_length=100)
    moyen: Optional[str] = Field(None, max_length=255)
    mission: Optional[str] = None
    date_depart: Optional[datetime] = None
    date_retour: Optional[datetime] = None
    numero_ordre: Optional[str] = Field(None, max_length=50)
    signataire: Optional[str] = Field(None, max_length=255)

    @model_validator(mode="after")
    def dates_coherentes(self):
        if self.date_depart and self.date_retour and self.date_retour < self.date_depart:
            raise ValueError("date_retour doit etre posterieure ou egale a date_depart")
        return self


class ServiceCourantUpdate(ServiceCourantCreate):
    pass


class ServiceCourantRead(ServiceCourantCreate):
    id_service: int
    model_config = {"from_attributes": True}


class ServiceCourantList(BaseModel):
    items: list[ServiceCourantRead]
    total: int
    skip: int
    limit: int
