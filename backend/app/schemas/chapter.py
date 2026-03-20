import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PanelInput(BaseModel):
    panel_id: int
    speaker: str | None = None
    text: str = Field(min_length=1)
    type: Literal["dialogue", "sfx", "narration", "sign"]


class PageInput(BaseModel):
    page_number: int = Field(gt=0)
    panels: list[PanelInput]


class ChapterUpload(BaseModel):
    chapter_number: int = Field(gt=0)
    title: str | None = None
    pages: list[PageInput]


class ChapterResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    chapter_number: int
    title: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChapterDetailResponse(ChapterResponse):
    dialogue_line_count: int
