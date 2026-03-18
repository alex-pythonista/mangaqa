import uuid
from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str
    description: str | None = None
    source_language: str = "ja"
    target_language: str = "en"


class ProjectResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    source_language: str
    target_language: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
