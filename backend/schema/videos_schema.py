from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from backend.models.base import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"))
    video_number = Column(Integer, nullable=False)
    title = Column(Text)
    script_original = Column(Text)
    script_clean = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
