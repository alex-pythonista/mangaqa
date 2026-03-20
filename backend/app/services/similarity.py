import uuid

import numpy as np
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.dialogue import DialogueLine
from app.models.embedding import Embedding


async def find_similar_pairs(
    db: AsyncSession,
    chapter_ids: list[uuid.UUID],
    threshold: float = 0.15,
    limit: int = 100,
) -> list[dict]:
    """Find pairs of semantically similar but textually different dialogue lines.
    Returns list of dicts with line_a, line_b, and distance."""
    line_b = aliased(DialogueLine, name="line_b")
    emb_a = aliased(Embedding, name="emb_a")
    emb_b = aliased(Embedding, name="emb_b")

    distance_expr = emb_a.embedding.cosine_distance(emb_b.embedding)

    stmt = (
        select(
            DialogueLine.id.label("id_a"),
            DialogueLine.text.label("text_a"),
            DialogueLine.speaker.label("speaker_a"),
            DialogueLine.page_number.label("page_a"),
            line_b.id.label("id_b"),
            line_b.text.label("text_b"),
            line_b.speaker.label("speaker_b"),
            line_b.page_number.label("page_b"),
            distance_expr.label("distance"),
        )
        .join(emb_a, emb_a.dialogue_line_id == DialogueLine.id)
        .join(
            line_b,
            and_(
                line_b.chapter_id.in_(chapter_ids),
                line_b.id > DialogueLine.id,
            ),
        )
        .join(emb_b, emb_b.dialogue_line_id == line_b.id)
        .where(
            DialogueLine.chapter_id.in_(chapter_ids),
            distance_expr < threshold,
            DialogueLine.text != line_b.text,
        )
        .order_by("distance")
        .limit(limit)
    )

    result = await db.execute(stmt)
    return [dict(row._mapping) for row in result.all()]


async def compute_speaker_centroid(
    db: AsyncSession,
    chapter_ids: list[uuid.UUID],
    speaker: str,
) -> list[float] | None:
    """Compute the average (centroid) embedding for a speaker's lines."""
    stmt = (
        select(Embedding.embedding)
        .join(DialogueLine, Embedding.dialogue_line_id == DialogueLine.id)
        .where(
            DialogueLine.chapter_id.in_(chapter_ids),
            DialogueLine.speaker == speaker,
            DialogueLine.line_type == "dialogue",
        )
    )
    result = await db.execute(stmt)
    vectors = [row[0] for row in result.all()]
    if not vectors:
        return None

    arr = np.array(vectors, dtype=np.float32)
    centroid = arr.mean(axis=0)
    norm = np.linalg.norm(centroid)
    if norm > 0:
        centroid = centroid / norm
    return centroid.tolist()


async def find_speaker_outliers(
    db: AsyncSession,
    chapter_ids: list[uuid.UUID],
    speaker: str,
    centroid: list[float],
    limit: int = 5,
) -> list[dict]:
    """Find dialogue lines by a speaker that are farthest from their centroid."""
    distance_expr = Embedding.embedding.cosine_distance(centroid)

    stmt = (
        select(
            DialogueLine.id,
            DialogueLine.text,
            DialogueLine.page_number,
            DialogueLine.panel_id,
            distance_expr.label("distance"),
        )
        .join(Embedding, Embedding.dialogue_line_id == DialogueLine.id)
        .where(
            DialogueLine.chapter_id.in_(chapter_ids),
            DialogueLine.speaker == speaker,
            DialogueLine.line_type == "dialogue",
        )
        .order_by(distance_expr.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    return [dict(row._mapping) for row in result.all()]


async def find_speaker_typical(
    db: AsyncSession,
    chapter_ids: list[uuid.UUID],
    speaker: str,
    centroid: list[float],
    limit: int = 5,
) -> list[dict]:
    """Find dialogue lines by a speaker closest to their centroid (most typical)."""
    distance_expr = Embedding.embedding.cosine_distance(centroid)

    stmt = (
        select(
            DialogueLine.id,
            DialogueLine.text,
            DialogueLine.page_number,
            distance_expr.label("distance"),
        )
        .join(Embedding, Embedding.dialogue_line_id == DialogueLine.id)
        .where(
            DialogueLine.chapter_id.in_(chapter_ids),
            DialogueLine.speaker == speaker,
            DialogueLine.line_type == "dialogue",
        )
        .order_by(distance_expr.asc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    return [dict(row._mapping) for row in result.all()]
