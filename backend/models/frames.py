import uuid
from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.models.base import Base


class Frame(Base):
    __tablename__ = "frames"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False,
    )

    shot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shots.id", ondelete="CASCADE"),
        nullable=False,
    )

    frame_number = Column(Integer, nullable=False)

    status = Column(Text, nullable=False, default="pending")

    image_url = Column(Text, nullable=True)
    bucket_path = Column(Text, nullable=True)
    frame_code = Column(Text, nullable=True)
    frame_prompt = Column(Text, nullable=True)

    generation_started_at = Column(TIMESTAMP(timezone=True), nullable=True)
    generation_completed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    shot = relationship("Shot", back_populates="frames")
