from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers.auth import request_ip
from app.core.dependencies import require_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.repositories.metier import PlainteRepository, ProcesVerbalRepository
from app.schemas.plainte import PlainteCreate, PlainteList, PlainteRead, PlainteUpdate
from app.schemas.proces_verbal import ProcesVerbalCreate, ProcesVerbalList, ProcesVerbalRead, ProcesVerbalUpdate
from app.services.audit import audit_service
from app.services.crud import CrudService

router = APIRouter(tags=["donnees sensibles"])


async def _get(service: CrudService, record_id: int):
    item = await service.get(record_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    return item


@router.get("/plaintes", response_model=PlainteList)
async def list_plaintes(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), request: Request = None, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.PLAINTES_LECTURE))):
    service = CrudService(db, PlainteRepository(db))
    items, total = await service.list(skip=skip, limit=limit, filters={})
    await audit_service.log(db, action="CONSULTATION", user_id=actor.id, identifier=actor.nom_utilisateur, table="plaintes", details={"skip": skip, "limit": limit}, ip_address=request_ip(request) if request else None, success=True)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/plaintes", response_model=PlainteRead, status_code=201)
async def create_plainte(data: PlainteCreate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.PLAINTES_ECRITURE))):
    return await CrudService(db, PlainteRepository(db)).create(data.model_dump(), actor, table="plaintes", ip_address=request_ip(request))


@router.get("/plaintes/{record_id}", response_model=PlainteRead)
async def get_plainte(record_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.PLAINTES_LECTURE))):
    item = await _get(CrudService(db, PlainteRepository(db)), record_id)
    await audit_service.log(db, action="CONSULTATION", user_id=actor.id, identifier=actor.nom_utilisateur, table="plaintes", record_id=record_id, ip_address=request_ip(request), success=True)
    return item


@router.patch("/plaintes/{record_id}", response_model=PlainteRead)
async def update_plainte(record_id: int, data: PlainteUpdate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.PLAINTES_ECRITURE))):
    item = await CrudService(db, PlainteRepository(db)).update(record_id, data.model_dump(exclude_unset=True), actor, table="plaintes", ip_address=request_ip(request))
    if item is None:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    return item


@router.delete("/plaintes/{record_id}", status_code=204)
async def delete_plainte(record_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.PLAINTES_SUPPRESSION))):
    if not await CrudService(db, PlainteRepository(db)).delete(record_id, actor, table="plaintes", ip_address=request_ip(request)):
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")


@router.get("/proces-verbaux", response_model=ProcesVerbalList)
async def list_pv(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), request: Request = None, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.PV_LECTURE))):
    service = CrudService(db, ProcesVerbalRepository(db))
    items, total = await service.list(skip=skip, limit=limit)
    await audit_service.log(db, action="CONSULTATION", user_id=actor.id, identifier=actor.nom_utilisateur, table="proces_verbaux", details={"skip": skip, "limit": limit}, ip_address=request_ip(request) if request else None, success=True)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("/proces-verbaux", response_model=ProcesVerbalRead, status_code=201)
async def create_pv(data: ProcesVerbalCreate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.PV_ECRITURE))):
    return await CrudService(db, ProcesVerbalRepository(db)).create(data.model_dump(), actor, table="proces_verbaux", ip_address=request_ip(request))


@router.get("/proces-verbaux/{record_id}", response_model=ProcesVerbalRead)
async def get_pv(record_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.PV_LECTURE))):
    item = await _get(CrudService(db, ProcesVerbalRepository(db)), record_id)
    await audit_service.log(db, action="CONSULTATION", user_id=actor.id, identifier=actor.nom_utilisateur, table="proces_verbaux", record_id=record_id, ip_address=request_ip(request), success=True)
    return item


@router.patch("/proces-verbaux/{record_id}", response_model=ProcesVerbalRead)
async def update_pv(record_id: int, data: ProcesVerbalUpdate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.PV_ECRITURE))):
    item = await CrudService(db, ProcesVerbalRepository(db)).update(record_id, data.model_dump(exclude_unset=True), actor, table="proces_verbaux", ip_address=request_ip(request))
    if item is None:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    return item


@router.delete("/proces-verbaux/{record_id}", status_code=204)
async def delete_pv(record_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.PV_SUPPRESSION))):
    if not await CrudService(db, ProcesVerbalRepository(db)).delete(record_id, actor, table="proces_verbaux", ip_address=request_ip(request)):
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
