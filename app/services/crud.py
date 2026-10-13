from typing import Any, Dict, Generic, Optional, TypeVar

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.utilisateur import Utilisateur
from app.repositories.base import AsyncRepository
from app.services.audit import audit_service

ModelT = TypeVar("ModelT")


class CrudService(Generic[ModelT]):
    def __init__(self, db: AsyncSession, repository: AsyncRepository):
        self.db = db
        self.repository = repository

    async def list(self, *, skip: int, limit: int, filters: Optional[Dict[str, Any]] = None):
        return await self.repository.list(skip=skip, limit=limit, filters=filters)

    async def get(self, record_id: int) -> Optional[ModelT]:
        return await self.repository.get(record_id)

    async def create(self, values: dict[str, Any], actor: Utilisateur, *, table: str, ip_address: Optional[str] = None):
        instance = await self.repository.add(values)
        await audit_service.log(
            self.db,
            action="CREATION",
            user_id=actor.id,
            identifier=actor.nom_utilisateur,
            table=table,
            record_id=getattr(instance, self.repository.id_field),
            details={"champs": list(values.keys())},
            ip_address=ip_address,
            success=True,
        )
        return instance

    async def update(self, record_id: int, values: dict[str, Any], actor: Utilisateur, *, table: str, ip_address: Optional[str] = None):
        instance = await self.repository.update(record_id, values)
        if instance is not None:
            await audit_service.log(
                self.db,
                action="MODIFICATION",
                user_id=actor.id,
                identifier=actor.nom_utilisateur,
                table=table,
                record_id=record_id,
                details={"champs": list(values.keys())},
                ip_address=ip_address,
                success=True,
            )
        return instance

    async def delete(self, record_id: int, actor: Utilisateur, *, table: str, ip_address: Optional[str] = None) -> bool:
        deleted = await self.repository.delete(record_id)
        if deleted:
            await audit_service.log(
                self.db,
                action="SUPPRESSION",
                user_id=actor.id,
                identifier=actor.nom_utilisateur,
                table=table,
                record_id=record_id,
                ip_address=ip_address,
                success=True,
            )
        return deleted
