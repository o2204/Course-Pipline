from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from backend.models.base import Base

class Shot(Base):
    __tablename__ = "shots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"))
    shot_number = Column(Integer, nullable=False)
    scene_text = Column(Text, nullable=False)