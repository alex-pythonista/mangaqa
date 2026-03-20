import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.chapter import Chapter
from app.models.dialogue import DialogueLine
from app.models.project import Project
from app.schemas.chapter import ChapterDetailResponse, ChapterResponse, ChapterUpload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects/{project_id}/chapters")


@router.post("/", response_model=ChapterDetailResponse, status_code=201)
async def upload_chapter(
    project_id: uuid.UUID,
    body: ChapterUpload,
    db: AsyncSession = Depends(get_db),
):
    # Validate project exists
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check for duplicate chapter number
    existing = await db.execute(
        select(Chapter).where(
            Chapter.project_id == project_id,
            Chapter.chapter_number == body.chapter_number,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Chapter {body.chapter_number} already exists for this project",
        )

    # Create chapter
    chapter = Chapter(
        project_id=project_id,
        chapter_number=body.chapter_number,
        title=body.title,
    )
    db.add(chapter)
    await db.flush()  # Get chapter.id without committing

    # Flatten pages → panels into dialogue lines
    line_order = 0
    lines = []
    for page in body.pages:
        for panel in page.panels:
            line_order += 1
            lines.append(
                DialogueLine(
                    chapter_id=chapter.id,
                    page_number=page.page_number,
                    panel_id=panel.panel_id,
                    speaker=panel.speaker,
                    text=panel.text,
                    line_type=panel.type,
                    line_order=line_order,
                )
            )

    db.add_all(lines)
    await db.commit()
    await db.refresh(chapter)

    logger.info(
        "Uploaded chapter %s for project %s (%d lines)",
        chapter.chapter_number,
        project_id,
        len(lines),
    )

    return ChapterDetailResponse(
        id=chapter.id,
        project_id=chapter.project_id,
        chapter_number=chapter.chapter_number,
        title=chapter.title,
        created_at=chapter.created_at,
        dialogue_line_count=len(lines),
    )


@router.get("/", response_model=list[ChapterResponse])
async def list_chapters(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    # Validate project exists
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(Chapter)
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.chapter_number)
    )
    return result.scalars().all()
