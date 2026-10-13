from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class AsyncRepository(Generic[ModelT]):
    """Small repository with allowlisted filters supplied by concrete classes."""

    model: type[ModelT]
    id_field: str

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, record_id: int) -> Optional[ModelT]:
        return await self.db.scalar(
            select(self.model).where(getattr(self.model, self.id_field) == record_id)
        )

    async def list(self, *, skip: int, limit: int, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[ModelT], int]:
        predicates = []
        for field, value in (filters or {}).items():
            if value is not None:
                predicates.append(getattr(self.model, field) == value)
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)
        if predicates:
            query = query.where(*predicates)
            count_query = count_query.where(*predicates)
        query = query.order_by(getattr(self.model, self.id_field).desc()).offset(skip).limit(limit)
        result = await self.db.scalars(query)
        total = int(await self.db.scalar(count_query) or 0)
        return list(result.all()), total

    async def add(self, values: dict[str, Any]) -> ModelT:
        instance = self.model(**values)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def update(self, record_id: int, values: dict[str, Any]) -> Optional[ModelT]:
        if not values:
            return await self.get(record_id)
        await self.db.execute(
            update(self.model)
            .where(getattr(self.model, self.id_field) == record_id)
            .values(**values)
        )
        await self.db.flush()
        return await self.get(record_id)

    async def delete(self, record_id: int) -> bool:
        result = await self.db.execute(
            delete(self.model).where(getattr(self.model, self.id_field) == record_id)
        )
        await self.db.flush()
        return bool(result.rowcount)
