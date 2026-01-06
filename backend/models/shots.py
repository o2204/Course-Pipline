import uuid
from sqlalchemy import Column, Text, TIMESTAMP, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.models.base import Base


class Shot(Base):
    __tablename__ = "shots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    shot_number = Column(Integer, nullable=False)
    scene_en = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    video = relationship("Video", back_populates="shots")
    frames = relationship("Frame", back_populates="shot", cascade="all, delete-orphan")
