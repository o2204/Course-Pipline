import uuid
from sqlalchemy import Column, Text, Integer, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.models.base import Base


class Video(Base):
    """
    Videos table - stores final generated videos.
    
    Each video identified by (course_name, video_number).
    """
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Reference to files table via course_name
    course_name = Column(
        Text,
        ForeignKey("files.course_name", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Video sequence number (1, 2, 3, ...)
    video_number = Column(Integer, nullable=False)
    
    # URL to final generated video (from Higgsfield AI)
    video_url = Column(Text, nullable=True)
    
    # Motion prompt used for video generation (renamed from script_clean)
    motion_prompt = Column(Text, nullable=True)

    # First frame image URL (required for generation)
    url_1 = Column(Text, nullable=True)
    
    # Last frame image URL (optional, for interpolation)
    url_2 = Column(Text, nullable=True)

    # Higgsfield Request ID
    request_id = Column(Text, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Unique constraint: one video per video_number per course
    __table_args__ = (
        UniqueConstraint('course_name', 'video_number', name='uq_course_video'),
    )

    # Relationship back to Files
    file = relationship("Files", back_populates="videos")

    # Relationship to Shots
    shots = relationship(
        "Shot",
        back_populates="video",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
