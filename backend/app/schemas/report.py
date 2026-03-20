import uuid
from datetime import datetime

from pydantic import BaseModel


class DialogueLineContext(BaseModel):
    page_number: int
    panel_id: int
    speaker: str | None
    text: str
    line_type: str


class QAResultResponse(BaseModel):
    id: uuid.UUID
    checker_type: str
    severity: str
    title: str
    description: str
    suggestion: str | None
    context: dict | None
    dialogue_line: DialogueLineContext | None

    model_config = {"from_attributes": True}


class ReportSummary(BaseModel):
    total_issues: int
    by_severity: dict[str, int]
    by_checker: dict[str, int]


class ReportResponse(BaseModel):
    project_id: uuid.UUID
    job_id: uuid.UUID
    job_completed_at: datetime | None
    summary: ReportSummary
    issues: list[QAResultResponse]
