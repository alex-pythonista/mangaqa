import uuid
from datetime import datetime

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    progress: str | None = None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class JobDetailResponse(JobResponse):
    result_counts: dict[str, int] | None = None


class AnalyzeResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    message: str
