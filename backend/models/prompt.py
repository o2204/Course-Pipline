# backend/models/prompt.py

import uuid
from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.models.base import Base


class Prompt(Base):
    """
    Prompts table - stores AI-generated storyboard as single JSONB object.
    
    CRITICAL: 
    - Entire storyboard structure stored in prompt_json (NO normalization)
    - Structure: {videos: [{shots: [{frames: [...]}]}]}
    - All JSON traversal MUST be done in Python (see utils/frame_extractor.py)
    - NO JSON querying in SQL
    """
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Reference to files table via course_name
    course_name = Column(
        Text,
        ForeignKey("files.course_name", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Full OpenAI-generated storyboard as JSONB
    prompt_json = Column(JSONB, nullable=False)

    model_name = Column(Text, nullable=True, default="gpt-4o-mini")

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationship back to Files
    file = relationship("Files", back_populates="prompts")

