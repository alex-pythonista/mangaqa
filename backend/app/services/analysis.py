import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import async_session
from app.models.chapter import Chapter
from app.models.job import AnalysisJob
from app.services.checkers import (
    ConsistencyChecker,
    ToneChecker,
    UntranslatedChecker,
    VoiceChecker,
)
from app.services.checkers.base import CheckerContext
from app.services.embedding import generate_embeddings_for_chapter
from app.services.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)

# In-memory progress tracking (job_id -> progress string)
_job_progress: dict[uuid.UUID, str] = {}


def get_job_progress(job_id: uuid.UUID) -> str | None:
    return _job_progress.get(job_id)


def _set_progress(job_id: uuid.UUID, step: str) -> None:
    _job_progress[job_id] = step
    logger.info("Job %s: %s", job_id, step)


async def run_analysis(job_id: uuid.UUID) -> None:
    """Background worker: runs full QA analysis pipeline for a job."""
    async with async_session() as db:
        job = await db.get(AnalysisJob, job_id)
        if not job:
            logger.error("Job %s not found", job_id)
            return

        llm = OpenRouterClient()
        try:
            # Mark as running
            job.status = "running"
            job.started_at = datetime.now(timezone.utc)
            await db.commit()

            _set_progress(job_id, "Generating embeddings...")

            # Get all chapters for the project
            result = await db.execute(
                select(Chapter)
                .where(Chapter.project_id == job.project_id)
                .order_by(Chapter.chapter_number)
            )
            chapters = result.scalars().all()
            chapter_ids = [ch.id for ch in chapters]

            if not chapter_ids:
                job.status = "completed"
                job.completed_at = datetime.now(timezone.utc)
                await db.commit()
                _job_progress.pop(job_id, None)
                return

            # Generate embeddings
            for i, chapter in enumerate(chapters):
                _set_progress(job_id, f"Generating embeddings ({i+1}/{len(chapters)} chapters)...")
                count = await generate_embeddings_for_chapter(db, chapter.id)
                logger.info("Job %s: %d embeddings for chapter %d", job_id, count, chapter.chapter_number)
            await db.commit()

            # Build checker context
            ctx = CheckerContext(
                db=db,
                job_id=job.id,
                project_id=job.project_id,
                chapter_ids=chapter_ids,
            )

            # Run checkers sequentially
            checkers = [
                ("Checking untranslated text...", UntranslatedChecker()),
                ("Checking consistency...", ConsistencyChecker(llm)),
                ("Checking character voice...", VoiceChecker(llm)),
                ("Checking tone...", ToneChecker(llm)),
            ]

            total_issues = 0
            for i, (label, checker) in enumerate(checkers):
                _set_progress(job_id, f"{label} ({i+1}/{len(checkers)})")
                count = await checker.run(ctx)
                total_issues += count
                await db.commit()
                logger.info("Job %s: %s found %d issues", job_id, checker.checker_type, count)

            # Mark completed
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()
            logger.info("Job %s completed: %d total issues", job_id, total_issues)

        except Exception as e:
            logger.exception("Analysis job %s failed", job_id)
            job.status = "failed"
            msg = str(e)
            if "Embedding API error" in msg:
                job.error_message = msg
            elif "OpenRouter" in msg or "rate limit" in msg.lower():
                job.error_message = f"LLM service error: {msg}"
            else:
                job.error_message = f"Analysis failed: {msg.split(chr(10))[0]}"
            job.error_message = job.error_message[:500]
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()
        finally:
            _job_progress.pop(job_id, None)
            await llm.close()
