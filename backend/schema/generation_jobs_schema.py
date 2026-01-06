from sqlalchemy import Column, Text, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from backend.models.base import Base

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(Text, nullable=False)  # image | video
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    provider = Column(Text)
    request_id = Column(Text)
    status = Column(Text, default="pending")
    error = Column(Text)
    retries = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
