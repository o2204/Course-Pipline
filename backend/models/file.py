import uuid
from sqlalchemy import Column, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.models.base import Base


class Files(Base):
    """
    Files table - stores uploaded course files.
    
    Business identifier: course_name (immutable, unique)
    """
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # CRITICAL: course_name is the business identifier (NOT filename)
    course_name = Column(Text, nullable=False, unique=True)
    
    full_text = Column(Text, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships (using course_name, not FK)
    # Note: SQLAlchemy relationships still work with the course_name reference
    prompts = relationship(
        "Prompt",
        back_populates="file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    
    images = relationship(
        "Image",
        back_populates="file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    
    videos = relationship(
        "Video",
        back_populates="file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

