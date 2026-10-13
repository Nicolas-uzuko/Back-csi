from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers.auth import request_ip
from app.core.dependencies import get_current_user, require_permission
from app.core.permissions import Permission
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.repositories.utilisateur import UtilisateurRepository
from app.schemas.utilisateur import UtilisateurChangePassword, UtilisateurChangeRole, UtilisateurCreate, UtilisateurList, UtilisateurRead, UtilisateurUpdate
from app.services.audit import audit_service
from app.services.auth import password_hash_for_create
from app.services.crud import CrudService

router = APIRouter(prefix="/utilisateurs", tags=["utilisateurs"])


@router.get("", response_model=UtilisateurList)
async def list_users(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.UTILISATEURS_LECTURE))):
    items, total = await UtilisateurRepository(db).list(skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.post("", response_model=UtilisateurRead, status_code=201)
async def create_user(data: UtilisateurCreate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.UTILISATEURS_ECRITURE))):
    values = data.model_dump(exclude={"mot_de_passe"})
    values["email"] = str(values["email"]).lower()
    values["mot_de_passe_hash"] = password_hash_for_create(data.mot_de_passe)
    try:
        return await CrudService(db, UtilisateurRepository(db)).create(values, actor, table="utilisateurs", ip_address=request_ip(request))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email, nom utilisateur ou matricule déjà utilisé")


@router.get("/{user_id}", response_model=UtilisateurRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.UTILISATEURS_LECTURE))):
    user = await UtilisateurRepository(db).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


@router.patch("/{user_id}", response_model=UtilisateurRead)
async def update_user(user_id: int, data: UtilisateurUpdate, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.UTILISATEURS_ECRITURE))):
    values = data.model_dump(exclude_unset=True)
    if "email" in values:
        values["email"] = str(values["email"]).lower()
    try:
        item = await CrudService(db, UtilisateurRepository(db)).update(user_id, values, actor, table="utilisateurs", ip_address=request_ip(request))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email, nom utilisateur ou matricule déjà utilisé")
    if item is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return item


@router.patch("/{user_id}/role", response_model=UtilisateurRead)
async def change_role(user_id: int, data: UtilisateurChangeRole, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.ROLES_MODIFICATION))):
    item = await CrudService(db, UtilisateurRepository(db)).update(user_id, {"role": data.role}, actor, table="utilisateurs", ip_address=request_ip(request))
    if item is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    await audit_service.log(db, action="CHANGEMENT_ROLE", user_id=actor.id, identifier=actor.nom_utilisateur, table="utilisateurs", record_id=user_id, details={"nouveau_role": data.role.value}, ip_address=request_ip(request), success=True)
    return item


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.UTILISATEURS_ECRITURE))):
    if user_id == actor.id:
        raise HTTPException(status_code=400, detail="Un administrateur ne peut pas supprimer son propre compte")
    if not await CrudService(db, UtilisateurRepository(db)).delete(user_id, actor, table="utilisateurs", ip_address=request_ip(request)):
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")


@router.post("/me/password", status_code=204)
async def change_my_password(data: UtilisateurChangePassword, request: Request, db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(get_current_user)):
    if not verify_password(data.ancien_mot_de_passe, actor.mot_de_passe_hash):
        await audit_service.log(db, action="CHANGEMENT_MOT_DE_PASSE", user_id=actor.id, identifier=actor.nom_utilisateur, ip_address=request_ip(request), success=False)
        raise HTTPException(status_code=400, detail="Ancien mot de passe invalide")
    actor.mot_de_passe_hash = hash_password(data.nouveau_mot_de_passe)
    await audit_service.log(db, action="CHANGEMENT_MOT_DE_PASSE", user_id=actor.id, identifier=actor.nom_utilisateur, ip_address=request_ip(request), success=True)
