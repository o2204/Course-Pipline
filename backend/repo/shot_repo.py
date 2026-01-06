from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models.shots import Shot


class ShotRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, shot_id: UUID) -> Shot | None:
        result = await self.db.execute(
            select(Shot).where(Shot.id == shot_id)
        )
        return result.scalar_one_or_none()

    async def get_by_video(
        self,
        video_id: UUID,
    ) -> list[Shot]:
        result = await self.db.execute(
            select(Shot)
            .where(Shot.video_id == video_id)
            .order_by(Shot.shot_number)
        )
        return result.scalars().all()

    async def create(self, data: dict) -> Shot:
        shot = Shot(**data)
        self.db.add(shot)
        await self.db.flush()
        await self.db.refresh(shot)
        return shot

    async def get_by_position(
        self,
        video_id: UUID,
        shot_number: int,
    ) -> Shot | None:
        result = await self.db.execute(
            select(Shot).where(
                Shot.video_id == video_id,
                Shot.shot_number == shot_number,
            )
        )
        return result.scalar_one_or_none()
