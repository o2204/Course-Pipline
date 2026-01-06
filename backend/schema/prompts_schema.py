# backend/models/prompt.py

import uuid
from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from backend.models.base import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    frame_id = Column(
        UUID(as_uuid=True),
        ForeignKey("frames.id", ondelete="CASCADE"),
        nullable=False,
    )

    # full OpenAI JSON
    prompt_json = Column(JSONB, nullable=False)

    model_name = Column(Text, nullable=False, default="gpt-5.1")

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
