import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.result import QAResult


@dataclass
class CheckerContext:
    db: AsyncSession
    job_id: uuid.UUID
    project_id: uuid.UUID
    chapter_ids: list[uuid.UUID]


class BaseChecker(ABC):
    checker_type: str

    @abstractmethod
    async def run(self, ctx: CheckerContext) -> int:
        """Execute the check. Returns the number of issues found."""
        ...

    async def _save_result(
        self,
        ctx: CheckerContext,
        severity: str,
        title: str,
        description: str,
        dialogue_line_id: uuid.UUID | None = None,
        suggestion: str | None = None,
        context: dict | None = None,
    ) -> QAResult:
        result = QAResult(
            job_id=ctx.job_id,
            checker_type=self.checker_type,
            severity=severity,
            dialogue_line_id=dialogue_line_id,
            title=title,
            description=description,
            suggestion=suggestion,
            context=context,
        )
        ctx.db.add(result)
        return result
