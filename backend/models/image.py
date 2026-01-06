# backend/models/image.py

import uuid
from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.models.base import Base


class Image(Base):
    """
    Images table - stores generated images for each frame.
    
    Lookup key: frame_code (format: "V1_S2_F3")
    - V = Video number
    - S = Shot number
    - F = Frame number
    """
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Reference to files table via course_name
    course_name = Column(
        Text,
        ForeignKey("files.course_name", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Frame identifier (e.g., "V1_S2_F3")
    frame_code = Column(Text, nullable=False, index=True)

    # URL to generated image (from Higgsfield AI)
    image_url = Column(Text, nullable=False)

    # Higgsfield Request ID
    request_id = Column(Text, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Unique constraint: one image per frame per course
    __table_args__ = (
        UniqueConstraint('course_name', 'frame_code', name='uq_course_frame'),
    )
    
    # Relationship back to Files
    file = relationship("Files", back_populates="images")
