import uuid
from datetime import datetime

from pydantic import BaseModel


class PanelInput(BaseModel):
    panel_id: int
    speaker: str | None = None
    text: str
    type: str  # dialogue, sfx, narration, sign


class PageInput(BaseModel):
    page_number: int
    panels: list[PanelInput]


class ChapterUpload(BaseModel):
    chapter_number: int
    title: str | None = None
    pages: list[PageInput]


class ChapterResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    chapter_number: int
    title: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
