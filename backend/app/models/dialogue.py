import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class DialogueLine(BaseModel):
    __tablename__ = "dialogue_lines"
    __table_args__ = (
        CheckConstraint(
            "line_type IN ('dialogue', 'sfx', 'narration', 'sign')",
            name="ck_dialogue_line_type",
        ),
    )

    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    panel_id: Mapped[int] = mapped_column(Integer, nullable=False)
    speaker: Mapped[str | None] = mapped_column(String(100), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    line_type: Mapped[str] = mapped_column(String(20), nullable=False)
    line_order: Mapped[int] = mapped_column(Integer, nullable=False)

    chapter = relationship("Chapter", back_populates="dialogue_lines")
    embedding = relationship("Embedding", back_populates="dialogue_line", uselist=False, cascade="all, delete-orphan")
    qa_results = relationship("QAResult", back_populates="dialogue_line")
