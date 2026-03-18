import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Project(BaseModel):
    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_language: Mapped[str] = mapped_column(String(10), server_default="ja")
    target_language: Mapped[str] = mapped_column(String(10), server_default="en")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="project", cascade="all, delete-orphan")
