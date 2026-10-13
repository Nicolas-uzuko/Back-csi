from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.models.utilisateur import Utilisateur
from app.repositories.audit import AuditRepository
from app.schemas.historique_action import HistoriqueActionList

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=HistoriqueActionList)
async def list_audit(
    skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None, max_length=50), table_cible: Optional[str] = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db), actor: Utilisateur = Depends(require_permission(Permission.AUDIT_LECTURE)),
):
    items, total = await AuditRepository(db).list(skip=skip, limit=limit, filters={"action": action, "table_cible": table_cible})
    return {"items": items, "total": total, "skip": skip, "limit": limit}
