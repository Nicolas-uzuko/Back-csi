from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.repositories.metier import (
    CourrierArriveeRepository, CourrierDepartRepository, ServiceCourantRepository, SituationPriseArmeRepository,
)
from app.schemas.courrier_arrivee import CourrierArriveeCreate, CourrierArriveeList, CourrierArriveeRead, CourrierArriveeUpdate
from app.schemas.courrier_depart import CourrierDepartCreate, CourrierDepartList, CourrierDepartRead, CourrierDepartUpdate
from app.schemas.service_courant import ServiceCourantCreate, ServiceCourantList, ServiceCourantRead, ServiceCourantUpdate
from app.schemas.situation_prise_arme import SituationPriseArmeCreate, SituationPriseArmeList, SituationPriseArmeRead, SituationPriseArmeUpdate
from app.services.crud import CrudService

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
