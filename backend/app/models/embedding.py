import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

EMBEDDING_DIMENSION = 1536  # Will adjust in Phase 3 when model is chosen


class Embedding(BaseModel):
    __tablename__ = "embeddings"

    dialogue_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dialogue_lines.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    embedding = mapped_column(Vector(EMBEDDING_DIMENSION), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)

    dialogue_line = relationship("DialogueLine", back_populates="embedding")
