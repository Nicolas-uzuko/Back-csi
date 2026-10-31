from pathlib import Path
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.models.document import CategorieArchive, Document, ModeConservation, TypeConfidentialite
from app.models.utilisateur import Utilisateur
from app.repositories.document import DocumentRepository
from app.repositories.metier import (
    CourrierArriveeRepository, CourrierDepartRepository, ServiceCourantRepository, SituationPriseArmeRepository,
)
from app.schemas.courrier_arrivee import CourrierArriveeCreate, CourrierArriveeList, CourrierArriveeRead, CourrierArriveeUpdate
from app.schemas.courrier_depart import CourrierDepartCreate, CourrierDepartList, CourrierDepartRead, CourrierDepartUpdate
from app.schemas.document import DocumentRead
from app.schemas.service_courant import ServiceCourantCreate, ServiceCourantList, ServiceCourantRead, ServiceCourantUpdate
from app.schemas.situation_prise_arme import SituationPriseArmeCreate, SituationPriseArmeList, SituationPriseArmeRead, SituationPriseArmeUpdate
from app.services.audit import audit_service
from app.services.crud import CrudService
from app.services.storage import private_storage

router = APIRouter(tags=["registres"])


def ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


async def _get_or_404(service: CrudService, record_id: int):
    record = await service.get(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    return record


@router.get("/courriers-arrivee", response_model=CourrierArriveeList)
async def list_courriers_arrivee(
    skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), categorie: Optional[str] = Query(None, max_length=10),
    db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.COURRIERS_ARRIVEE_LECTURE)),
):
    items, total = await CrudService(db, CourrierArriveeRepository(db)).list(skip=skip, limit=limit, filters={"categorie": categorie})
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/courriers-arrivee", response_model=CourrierArriveeRead, status_code=201)
async def create_courrier_arrivee(data: CourrierArriveeCreate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.COURRIERS_ARRIVEE_ECRITURE))):
    return await CrudService(db, CourrierArriveeRepository(db)).create(data.model_dump(), actor, table="courriers_arrivee", ip_address=ip(request))


@router.get("/courriers-arrivee/{record_id}", response_model=CourrierArriveeRead)
async def get_courrier_arrivee(record_id: int, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.COURRIERS_ARRIVEE_LECTURE))):
    return await _get_or_404(CrudService(db, CourrierArriveeRepository(db)), record_id)


@router.patch("/courriers-arrivee/{record_id}", response_model=CourrierArriveeRead)
async def update_courrier_arrivee(record_id: int, data: CourrierArriveeUpdate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.COURRIERS_ARRIVEE_ECRITURE))):
    record = await CrudService(db, CourrierArriveeRepository(db)).update(record_id, data.model_dump(exclude_unset=True), actor, table="courriers_arrivee", ip_address=ip(request))
    if record is None:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    return record


@router.delete("/courriers-arrivee/{record_id}", status_code=204)
async def delete_courrier_arrivee(record_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.COURRIERS_ARRIVEE_ECRITURE))):
    if not await CrudService(db, CourrierArriveeRepository(db)).delete(record_id, actor, table="courriers_arrivee", ip_address=ip(request)):
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")


@router.get("/courriers-depart", response_model=CourrierDepartList)
async def list_courriers_depart(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), categorie: Optional[str] = Query(None, max_length=10), db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.COURRIERS_DEPART_LECTURE))):
    items, total = await CrudService(db, CourrierDepartRepository(db)).list(skip=skip, limit=limit, filters={"categorie": categorie})
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/courriers-depart", response_model=CourrierDepartRead, status_code=201)
async def create_courrier_depart(data: CourrierDepartCreate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.COURRIERS_DEPART_ECRITURE))):
    return await CrudService(db, CourrierDepartRepository(db)).create(data.model_dump(), actor, table="courriers_depart", ip_address=ip(request))


@router.get("/courriers-depart/{record_id}", response_model=CourrierDepartRead)
async def get_courrier_depart(record_id: int, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.COURRIERS_DEPART_LECTURE))):
    return await _get_or_404(CrudService(db, CourrierDepartRepository(db)), record_id)


@router.patch("/courriers-depart/{record_id}", response_model=CourrierDepartRead)
async def update_courrier_depart(record_id: int, data: CourrierDepartUpdate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.COURRIERS_DEPART_ECRITURE))):
    record = await CrudService(db, CourrierDepartRepository(db)).update(record_id, data.model_dump(exclude_unset=True), actor, table="courriers_depart", ip_address=ip(request))
    if record is None:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    return record


@router.delete("/courriers-depart/{record_id}", status_code=204)
async def delete_courrier_depart(record_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.COURRIERS_DEPART_ECRITURE))):
    if not await CrudService(db, CourrierDepartRepository(db)).delete(record_id, actor, table="courriers_depart", ip_address=ip(request)):
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")


@router.get("/services-courants", response_model=ServiceCourantList)
async def list_services(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.SERVICES_LECTURE))):
    items, total = await CrudService(db, ServiceCourantRepository(db)).list(skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/services-courants", response_model=ServiceCourantRead, status_code=201)
async def create_service(data: ServiceCourantCreate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.SERVICES_ECRITURE))):
    return await CrudService(db, ServiceCourantRepository(db)).create(data.model_dump(), actor, table="services_courants", ip_address=ip(request))


@router.get("/services-courants/{record_id}", response_model=ServiceCourantRead)
async def get_service(record_id: int, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.SERVICES_LECTURE))):
    return await _get_or_404(CrudService(db, ServiceCourantRepository(db)), record_id)


@router.patch("/services-courants/{record_id}", response_model=ServiceCourantRead)
async def update_service(record_id: int, data: ServiceCourantUpdate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.SERVICES_ECRITURE))):
    record = await CrudService(db, ServiceCourantRepository(db)).update(record_id, data.model_dump(exclude_unset=True), actor, table="services_courants", ip_address=ip(request))
    if record is None:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    return record



@router.delete("/services-courants/{record_id}", status_code=204)
async def delete_service(record_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.SERVICES_ECRITURE))):
    if not await CrudService(db, ServiceCourantRepository(db)).delete(record_id, actor, table="services_courants", ip_address=ip(request)):
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")


@router.post("/services-courants/{record_id}/upload", response_model=DocumentRead, status_code=201)
async def upload_fichier_ordre_mission(
    record_id: int,
    file: UploadFile = File(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    actor: Utilisateur = Depends(require_permission(Permission.SERVICES_ECRITURE)),
):
    """Attache un fichier (PDF, DOCX, image) à un ordre de mission."""
    # Vérifier que le service existe
    service = await CrudService(db, ServiceCourantRepository(db)).get(record_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Ordre de mission introuvable")

    # Supprimer l'ancien fichier lié si existant
    existing_docs, _ = await DocumentRepository(db).list(
        skip=0, limit=1,
        filters={"table_source": "services_courants", "id_source": record_id}
    )
    for old_doc in existing_docs:
        if old_doc.chemin_stockage:
            from pathlib import Path as _Path
            old_path = _Path(old_doc.chemin_stockage).resolve()
            if old_path.parent == private_storage.root and old_path.is_file():
                old_path.unlink(missing_ok=True)
        await DocumentRepository(db).delete(old_doc.id_document)

    # Sauvegarder le nouveau fichier
    try:
        file_values = await private_storage.save_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Créer le document lié à cet ordre de mission (catégorie A, type CAHIER_SERVICE devient ORDRE_GENDARMERIE_NATIONALE pour cat A)
    values = {
        **file_values,
        "table_source": "services_courants",
        "id_source": record_id,
        "categorie_archive": CategorieArchive.A,
        "type_document": "ORDRE_GENDARMERIE_NATIONALE",
        "confidentialite": TypeConfidentialite.NON_CONFIDENTIEL,
        "mode_conservation": ModeConservation.NUMERIQUE,
        "emplacement_physique": None,
        "importe_par_id": actor.id,
    }
    document = await DocumentRepository(db).add(values)
    await audit_service.log(
        db, action="CREATION", user_id=actor.id, identifier=actor.nom_utilisateur,
        table="documents", record_id=document.id_document,
        details={"mode": "NUMERIQUE", "type_document": "ORDRE_GENDARMERIE_NATIONALE", "ordre_mission_id": record_id},
        ip_address=ip(request) if request else None, success=True,
    )
    return document


@router.get("/services-courants/{record_id}/download")
async def download_fichier_ordre_mission(
    record_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    actor: Utilisateur = Depends(require_permission(Permission.SERVICES_LECTURE)),
):
    """Télécharger le fichier attaché à un ordre de mission."""
    docs, _ = await DocumentRepository(db).list(
        skip=0, limit=1,
        filters={"table_source": "services_courants", "id_source": record_id}
    )
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun fichier attaché à cet ordre de mission")
    document = docs[0]
    if not document.chemin_stockage:
        raise HTTPException(status_code=404, detail="Aucun fichier numérique associé")
    try:
        content = await private_storage.read_private(document.chemin_stockage)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="Fichier introuvable sur le serveur")
    await audit_service.log(
        db, action="TELECHARGEMENT", user_id=actor.id, identifier=actor.nom_utilisateur,
        table="documents", record_id=document.id_document,
        ip_address=ip(request), success=True,
    )
    filename = quote((document.nom_original or document.nom_interne or f"ordre_mission_{record_id}").replace(" ", "_"))
    return Response(
        content=content,
        media_type=document.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.get("/services-courants/{record_id}/fichier-info", response_model=DocumentRead)
async def get_fichier_info_ordre_mission(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    actor: Utilisateur = Depends(require_permission(Permission.SERVICES_LECTURE)),
):
    """Récupère les métadonnées du fichier attaché à un ordre de mission."""
    docs, _ = await DocumentRepository(db).list(
        skip=0, limit=1,
        filters={"table_source": "services_courants", "id_source": record_id}
    )
    if not docs:
        raise HTTPException(status_code=404, detail="Aucun fichier attaché")
    return docs[0]


@router.get("/situations-prise-arme", response_model=SituationPriseArmeList)
async def list_situations(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.SITUATIONS_LECTURE))):
    items, total = await CrudService(db, SituationPriseArmeRepository(db)).list(skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/situations-prise-arme", response_model=SituationPriseArmeRead, status_code=201)
async def create_situation(data: SituationPriseArmeCreate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.SITUATIONS_ECRITURE))):
    return await CrudService(db, SituationPriseArmeRepository(db)).create(data.model_dump(), actor, table="situations_prise_arme", ip_address=ip(request))


@router.get("/situations-prise-arme/{record_id}", response_model=SituationPriseArmeRead)
async def get_situation(record_id: int, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.SITUATIONS_LECTURE))):
    return await _get_or_404(CrudService(db, SituationPriseArmeRepository(db)), record_id)


@router.patch("/situations-prise-arme/{record_id}", response_model=SituationPriseArmeRead)
async def update_situation(record_id: int, data: SituationPriseArmeUpdate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.SITUATIONS_ECRITURE))):
    record = await CrudService(db, SituationPriseArmeRepository(db)).update(record_id, data.model_dump(exclude_unset=True), actor, table="situations_prise_arme", ip_address=ip(request))
    if record is None:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    return record


@router.delete("/situations-prise-arme/{record_id}", status_code=204)
async def delete_situation(record_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.SITUATIONS_ECRITURE))):
    if not await CrudService(db, SituationPriseArmeRepository(db)).delete(record_id, actor, table="situations_prise_arme", ip_address=ip(request)):
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
