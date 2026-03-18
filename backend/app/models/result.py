import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class QAResult(BaseModel):
    __tablename__ = "qa_results"
    __table_args__ = (
        CheckConstraint(
            "checker_type IN ('untranslated', 'consistency', 'voice', 'tone')",
            name="ck_result_checker_type",
        ),
        CheckConstraint(
            "severity IN ('critical', 'warning', 'info')",
            name="ck_result_severity",
        ),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    checker_type: Mapped[str] = mapped_column(String(20), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)
    dialogue_line_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dialogue_lines.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    job = relationship("AnalysisJob", back_populates="qa_results")
    dialogue_line = relationship("DialogueLine", back_populates="qa_results")
