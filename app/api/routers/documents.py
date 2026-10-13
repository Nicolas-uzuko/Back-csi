from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers.auth import request_ip
from app.core.dependencies import get_current_user, require_permission
from app.core.permissions import Permission, has_permission
from app.db.session import get_db
from app.models.document import CategorieArchive, Document, TypeConfidentialite
from app.models.utilisateur import Utilisateur
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentList, DocumentRead, DocumentUpdate, DocumentUploadMetadata
from app.services.audit import audit_service
from app.services.documents import DocumentService
from app.services.storage import private_storage

router = APIRouter(prefix="/documents", tags=["archivage"])


def _ensure_document_permission(actor: Utilisateur, document: Document, *, write: bool = False) -> None:
    if write:
        if not has_permission(actor, Permission.DOCUMENTS_ECRITURE):
            raise HTTPException(status_code=403, detail="Permission insuffisante")
        return
    permission = Permission.DOCUMENTS_A_LECTURE if document.categorie_archive == CategorieArchive.A else Permission.DOCUMENTS_B_LECTURE
    if not has_permission(actor, permission) or (document.confidentialite == TypeConfidentialite.CONFIDENTIEL and actor.role.value != "ADMIN"):
        raise HTTPException(status_code=403, detail="Permission documentaire insuffisante")


@router.get("", response_model=DocumentList)
async def list_documents(
    skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), categorie_archive: Optional[CategorieArchive] = None,
    table_source: Optional[str] = Query(None, max_length=100), db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.DOCUMENTS_A_LECTURE)),
):
    if categorie_archive == CategorieArchive.B and not has_permission(actor, Permission.DOCUMENTS_B_LECTURE):
        raise HTTPException(status_code=403, detail="Permission documentaire insuffisante")
    if categorie_archive is None and not has_permission(actor, Permission.DOCUMENTS_B_LECTURE):
        categorie_archive = CategorieArchive.A
    if table_source and table_source not in {"courriers_arrivee", "courriers_depart", "plaintes", "proces_verbaux", "services_courants", "situations_prise_arme"}:
        raise HTTPException(status_code=422, detail="Table source non autorisee")
    items, total = await DocumentRepository(db).list(skip=skip, limit=limit, filters={"categorie_archive": categorie_archive, "table_source": table_source})
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("", response_model=DocumentRead, status_code=201)
async def create_physical_document(data: DocumentCreate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.DOCUMENTS_ECRITURE))):
    try:
        return await DocumentService(db).create_physical(data, actor, request_ip(request))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/upload", response_model=DocumentRead, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    categorie_archive: CategorieArchive = Form(...),
    type_document: str = Form(...),
    confidentialite: str = Form(...),
    mode_conservation: str = Form(...),
    table_source: Optional[str] = Form(None),
    id_source: Optional[int] = Form(None),
    emplacement_physique: Optional[str] = Form(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    actor: Utilisateur = Depends(require_permission(Permission.DOCUMENTS_ECRITURE)),
):
    try:
        metadata = DocumentUploadMetadata.model_validate({
            "categorie_archive": categorie_archive,
            "type_document": type_document,
            "confidentialite": confidentialite,
            "mode_conservation": mode_conservation,
            "table_source": table_source,
            "id_source": id_source,
            "emplacement_physique": emplacement_physique,
        })
        return await DocumentService(db).upload(metadata, file, actor, request_ip(request) if request else None)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(document_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.DOCUMENTS_A_LECTURE))):
    document = await DocumentRepository(db).get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document introuvable")
    _ensure_document_permission(actor, document)
    await audit_service.log(db, action="CONSULTATION", user_id=actor.id, identifier=actor.nom_utilisateur, table="documents", record_id=document_id, ip_address=request_ip(request), success=True)
    return document


@router.patch("/{document_id}", response_model=DocumentRead)
async def update_document(document_id: int, data: DocumentUpdate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.DOCUMENTS_ECRITURE))):
    try:
        document = await DocumentService(db).update(document_id, data, actor, request_ip(request))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if document is None:
        raise HTTPException(status_code=404, detail="Document introuvable")
    return document


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.DOCUMENTS_SUPPRESSION))):
    if not await DocumentService(db).delete(document_id, actor, request_ip(request)):
        raise HTTPException(status_code=404, detail="Document introuvable")


@router.get("/{document_id}/download")
async def download_document(document_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.DOCUMENTS_A_LECTURE))):
    document = await DocumentRepository(db).get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document introuvable")
    _ensure_document_permission(actor, document)
    if not document.chemin_stockage or document.mode_conservation.value == "PHYSIQUE":
        raise HTTPException(status_code=404, detail="Aucun fichier numérique associé")
    try:
        content = await private_storage.read_private(document.chemin_stockage)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    await audit_service.log(db, action="TELECHARGEMENT", user_id=actor.id, identifier=actor.nom_utilisateur, table="documents", record_id=document_id, ip_address=request_ip(request), success=True)
    filename = quote(Path(document.nom_original or document.nom_interne or "document").name)
    return Response(content=content, media_type=document.mime_type or "application/octet-stream", headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"})
