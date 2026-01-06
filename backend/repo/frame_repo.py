# backend/repo/frame_repo.py

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.frames import Frame
from backend.models.shots import Shot
from backend.models.videos import Video


class FrameRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------
    # Get by ID
    # -------------------------------------------------
    async def get_by_id(self, frame_id: UUID) -> Frame | None:
        result = await self.db.execute(
            select(Frame).where(Frame.id == frame_id)
        )
        return result.scalar_one_or_none()

    async def get_or_raise(self, frame_id: UUID) -> Frame:
        frame = await self.get_by_id(frame_id)
        if not frame:
            raise ValueError("Frame not found")
        return frame

    # -------------------------------------------------
    # Get frame by position (file + video + shot + frame)
    # -------------------------------------------------
    async def get_by_position(
        self,
        file_id: UUID,
        video_number: int,
        shot_number: int,
        frame_number: int,
    ) -> Frame | None:
        result = await self.db.execute(
            select(Frame)
            .join(Shot, Frame.shot_id == Shot.id)
            .join(Video, Shot.video_id == Video.id)
            .where(
                Frame.file_id == file_id,
                Video.video_number == video_number,
                Shot.shot_number == shot_number,
                Frame.frame_number == frame_number,
            )
        )
        return result.scalar_one_or_none()

    # -------------------------------------------------
    # Update frame prompt + code
    # -------------------------------------------------
    async def update_prompt(
        self,
        frame: Frame,
        frame_code: str,
        frame_prompt: str,
    ) -> Frame:
        frame.frame_code = frame_code
        frame.frame_prompt = frame_prompt

        await self.db.flush()
        await self.db.refresh(frame)
        return frame

    # -------------------------------------------------
    # Create frame
    # -------------------------------------------------
    async def create(self, data: dict) -> Frame:
        frame = Frame(**data)
        self.db.add(frame)
        await self.db.flush()
        await self.db.refresh(frame)
        return frame

    # -------------------------------------------------
    # Get frame by code
    # -------------------------------------------------
    async def get_by_code(self, frame_code: str) -> Frame | None:
        stmt = select(Frame).where(Frame.frame_code == frame_code)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_file_id(self, file_id):
        stmt = (
            select(Frame)
            .join(Frame.shot)
            .join(Shot.video)
            .where(Video.file_id == file_id)
            .order_by(Frame.frame_code)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update_prompt(
        self,
        *,
        frame: Frame,
        frame_code: str,
        frame_prompt: str,
    ) -> Frame:
        frame.frame_code = frame_code
        frame.frame_prompt = frame_prompt

        await self.db.flush()
        await self.db.refresh(frame)
        return frame

