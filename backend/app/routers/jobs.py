import logging
import uuid
from collections import Counter

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.dialogue import DialogueLine
from app.models.job import AnalysisJob
from app.models.project import Project
from app.models.result import QAResult
from app.schemas.job import AnalyzeResponse, JobDetailResponse, JobResponse
from app.schemas.report import (
    DialogueLineContext,
    QAResultResponse,
    ReportResponse,
    ReportSummary,
)
from app.services.analysis import get_job_progress, run_analysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects/{project_id}")


@router.post("/jobs/analyze", response_model=AnalyzeResponse, status_code=202)
async def trigger_analysis(
    project_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # Validate project
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check no job already pending/running
    existing = await db.execute(
        select(AnalysisJob).where(
            AnalysisJob.project_id == project_id,
            AnalysisJob.status.in_(["pending", "running"]),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Analysis already in progress")

    # Check project has dialogue lines
    line_count = await db.execute(
        select(func.count(DialogueLine.id))
        .join(DialogueLine.chapter)
        .where(DialogueLine.chapter.has(project_id=project_id))
    )
    if line_count.scalar_one() == 0:
        raise HTTPException(status_code=400, detail="No dialogue lines to analyze. Upload chapters first.")

    # Create job
    job = AnalysisJob(project_id=project_id, status="pending")
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Kick off background worker
    background_tasks.add_task(run_analysis, job.id)
    logger.info("Triggered analysis job %s for project %s", job.id, project_id)

    return AnalyzeResponse(
        job_id=job.id,
        status=job.status,
        message="Analysis job created",
    )


@router.get("/jobs", response_model=list[JobResponse])
async def list_jobs(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(AnalysisJob)
        .where(AnalysisJob.project_id == project_id)
        .order_by(AnalysisJob.created_at.desc())
    )
    return result.scalars().all()


@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job(
    project_id: uuid.UUID,
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    # Expire all cached state so we read fresh data (progress updates from background worker)
    db.expire_all()
    result = await db.execute(
        select(AnalysisJob).where(AnalysisJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job or job.project_id != project_id:
        raise HTTPException(status_code=404, detail="Job not found")

    result_counts = None
    if job.status == "completed":
        result = await db.execute(
            select(QAResult.severity, func.count(QAResult.id))
            .where(QAResult.job_id == job_id)
            .group_by(QAResult.severity)
        )
        result_counts = {row[0]: row[1] for row in result.all()}

    # Get live progress from in-memory tracker
    progress = get_job_progress(job_id)

    return JobDetailResponse(
        id=job.id,
        project_id=job.project_id,
        status=job.status,
        progress=progress,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        result_counts=result_counts,
    )


@router.get("/report", response_model=ReportResponse)
async def get_report(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Find latest completed job
    result = await db.execute(
        select(AnalysisJob)
        .where(
            AnalysisJob.project_id == project_id,
            AnalysisJob.status == "completed",
        )
        .order_by(AnalysisJob.completed_at.desc())
        .limit(1)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="No completed analysis found")

    # Fetch all results with dialogue line context
    result = await db.execute(
        select(QAResult)
        .options(selectinload(QAResult.dialogue_line))
        .where(QAResult.job_id == job.id)
        .order_by(QAResult.created_at)
    )
    qa_results = result.scalars().all()

    # Build summary
    severity_counts: dict[str, int] = Counter()
    checker_counts: dict[str, int] = Counter()
    issues: list[QAResultResponse] = []

    for qr in qa_results:
        severity_counts[qr.severity] += 1
        checker_counts[qr.checker_type] += 1

        dl_context = None
        if qr.dialogue_line:
            dl_context = DialogueLineContext(
                page_number=qr.dialogue_line.page_number,
                panel_id=qr.dialogue_line.panel_id,
                speaker=qr.dialogue_line.speaker,
                text=qr.dialogue_line.text,
                line_type=qr.dialogue_line.line_type,
            )

        issues.append(
            QAResultResponse(
                id=qr.id,
                checker_type=qr.checker_type,
                severity=qr.severity,
                title=qr.title,
                description=qr.description,
                suggestion=qr.suggestion,
                context=qr.context,
                dialogue_line=dl_context,
            )
        )

    summary = ReportSummary(
        total_issues=len(issues),
        by_severity=dict(severity_counts),
        by_checker=dict(checker_counts),
    )

    return ReportResponse(
        project_id=project_id,
        job_id=job.id,
        job_completed_at=job.completed_at,
        summary=summary,
        issues=issues,
    )
