from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.courrier_arrivee import CourrierArrivee
from app.models.courrier_depart import CourrierDepart
from app.models.document import (
    CategorieArchive,
    Document,
    ModeConservation,
    TypeConfidentialite,
)
from app.models.plainte import Plainte
from app.models.proces_verbal import ProcesVerbal
from app.models.service_courant import ServiceCourant
from app.models.situation_prise_arme import SituationPriseArme
from app.models.utilisateur import Utilisateur
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentUploadMetadata
from app.services.audit import audit_service
from app.services.storage import private_storage


SOURCE_MODELS = {
    "courriers_arrivee": (CourrierArrivee, "id_courrier"),
    "courriers_depart": (CourrierDepart, "id_courrier"),
    "plaintes": (Plainte, "id_plainte"),
    "proces_verbaux": (ProcesVerbal, "id_pv"),
    "services_courants": (ServiceCourant, "id_service"),
    "situations_prise_arme": (SituationPriseArme, "id_situation"),
}

TYPE_CATEGORY = {
    "CORRESPONDANCE_ARRIVEE_3": CategorieArchive.A,
    "CAHIER_ENREGISTREMENT_3": CategorieArchive.A,
    "COPIE_CORRESPONDANCE_2": CategorieArchive.A,
    "AVIS_MUTATION": CategorieArchive.A,
    "ORDRE_GENDARMERIE_NATIONALE": CategorieArchive.A,
    "REGISTRE_PERMISSIONNAIRES": CategorieArchive.A,
    "CORRESPONDANCE_ARRIVEE_3S": CategorieArchive.B,
    "CAHIER_ENREGISTREMENT_3S": CategorieArchive.B,
    "COPIE_CORRESPONDANCE_4": CategorieArchive.B,
    "ARCHIVE_PROCES_VERBAL": CategorieArchive.B,
    "REGISTRE_PROCES_VERBAUX": CategorieArchive.B,
    "CAHIER_SERVICE": CategorieArchive.B,
    "BULLETIN_SERVICE": CategorieArchive.B,
}


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = DocumentRepository(db)

    async def _validate_source(self, table_source: Optional[str], id_source: Optional[int]) -> None:
        if (table_source is None) != (id_source is None):
            raise ValueError("table_source et id_source doivent etre fournis ensemble")
        if table_source is None:
            return
        source = SOURCE_MODELS.get(table_source)
        if source is None:
            raise ValueError("Table source non autorisee")
        model, id_field = source
        exists = await self.db.scalar(select(model).where(getattr(model, id_field) == id_source))
        if exists is None:
            raise ValueError("Enregistrement source introuvable")

    @staticmethod
    def _validate_classification(type_document: str, category: CategorieArchive, confidentiality: TypeConfidentialite) -> None:
        expected_category = TYPE_CATEGORY.get(type_document)
        if expected_category is None or expected_category != category:
            raise ValueError("Type de document incompatible avec la categorie d archive")
        expected_confidentiality = (
            TypeConfidentialite.NON_CONFIDENTIEL if category == CategorieArchive.A else TypeConfidentialite.CONFIDENTIEL
        )
        if confidentiality != expected_confidentiality:
            raise ValueError("Confidentialite incompatible avec la categorie d archive")

    async def create_physical(self, data: DocumentCreate, actor: Utilisateur, ip_address: Optional[str]) -> Document:
        self._validate_classification(data.type_document, data.categorie_archive, data.confidentialite)
        await self._validate_source(data.table_source, data.id_source)
        values = data.model_dump()
        document = await self.repository.add(values)
        await audit_service.log(
            self.db, action="CREATION", user_id=actor.id, identifier=actor.nom_utilisateur,
            table="documents", record_id=document.id_document,
            details={"mode": data.mode_conservation.value, "type_document": data.type_document},
            ip_address=ip_address, success=True,
        )
        return document

    async def upload(self, data: DocumentUploadMetadata, upload: UploadFile, actor: Utilisateur, ip_address: Optional[str]) -> Document:
        self._validate_classification(data.type_document, data.categorie_archive, data.confidentialite)
        await self._validate_source(data.table_source, data.id_source)
        file_values = await private_storage.save_upload(upload)
        values = {**data.model_dump(), **file_values}
        try:
            document = await self.repository.add(values)
            await audit_service.log(
                self.db, action="CREATION", user_id=actor.id, identifier=actor.nom_utilisateur,
                table="documents", record_id=document.id_document,
                details={"mode": data.mode_conservation.value, "type_document": data.type_document, "fichier": True},
                ip_address=ip_address, success=True,
            )
            return document
        except Exception:
            path = Path(str(file_values["chemin_stockage"]))
            if path.is_file():
                path.unlink()
            raise

    async def update(self, document_id: int, data: DocumentUpdate, actor: Utilisateur, ip_address: Optional[str]) -> Optional[Document]:
        current = await self.repository.get(document_id)
        if current is None:
            return None
        values = data.model_dump(exclude_unset=True)
        category = values.get("categorie_archive", current.categorie_archive)
        confidentiality = values.get("confidentialite", current.confidentialite)
        type_document = values.get("type_document", current.type_document)
        self._validate_classification(type_document, category, confidentiality)
        document = await self.repository.update(document_id, values)
        await audit_service.log(
            self.db, action="MODIFICATION", user_id=actor.id, identifier=actor.nom_utilisateur,
            table="documents", record_id=document_id, details={"champs": list(values)},
            ip_address=ip_address, success=True,
        )
        return document

    async def delete(self, document_id: int, actor: Utilisateur, ip_address: Optional[str]) -> bool:
        current = await self.repository.get(document_id)
        if current is None:
            return False
        deleted = await self.repository.delete(document_id)
        if deleted:
            if current.chemin_stockage:
                path = Path(current.chemin_stockage).resolve()
                if path.parent == private_storage.root and path.is_file():
                    path.unlink()
            await audit_service.log(
                self.db, action="SUPPRESSION", user_id=actor.id, identifier=actor.nom_utilisateur,
                table="documents", record_id=document_id, ip_address=ip_address, success=True,
            )
        return deleted
