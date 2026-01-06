from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from backend.models.base import Base

class Frame(Base):
    __tablename__ = "frames"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"))
    shot_id = Column(UUID(as_uuid=True), ForeignKey("shots.id", ondelete="CASCADE"))
    frame_number = Column(Integer, nullable=False)
    frame_code = Column(Text, nullable=False, unique=True)
    frame_prompt = Column(Text, nullable=False)
    status = Column(Text, default="pending")  # pending | generating | completed | failed
    image_url = Column(Text)
