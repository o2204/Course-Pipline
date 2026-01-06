from typing import TypeVar, Generic, Type, Optional, List, cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models.base import Base


T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: UUID) -> Optional[T]:
        result = await self.db.execute(
            select(self.model).filter(self.model.id == id)
        )
        return result.scalars().first()

    async def get_all(
        self,
        page: int = 1,
        limit: int = 10
    ) -> List[T]:
        stmt = select(self.model)

        if page > 1:
            stmt = stmt.offset((page - 1) * limit)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.db.execute(stmt)
        return cast(List[T], result.scalars().all())

    async def create(self, obj_in: dict) -> T:
        obj = self.model(**obj_in)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: UUID, obj_in: dict) -> Optional[T]:
        obj = await self.get(id)
        if not obj:
            return None

        for key, value in obj_in.items():
            setattr(obj, key, value)

        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: UUID) -> bool:
        obj = await self.get(id)
        if not obj:
            return False

        await self.db.delete(obj)
        await self.db.flush()
        return True
