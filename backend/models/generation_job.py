import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from backend.models.base import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ✅ ONE job → ONE frame
    frame_id = Column(
        UUID(as_uuid=True),
        ForeignKey("frames.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Context
    file_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    prompt_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Provider
    provider = Column(String, nullable=False)   # "higgsfield"
    request_id = Column(String, unique=True)

    # Lifecycle
    status = Column(String, nullable=False)     # queued | running | success | failed | cancelled
    error_message = Column(String)
    retry_count = Column(Integer, server_default="0", nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
