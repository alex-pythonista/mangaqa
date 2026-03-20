import asyncio
import logging
import uuid

import httpx
import numpy as np
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.dialogue import DialogueLine
from app.models.embedding import Embedding

logger = logging.getLogger(__name__)

BATCH_SIZE = 32


async def _call_hf_embedding(texts: list[str]) -> list[list[float]]:
    """Call HuggingFace Inference API for feature-extraction embeddings."""
    url = f"{settings.HF_API_URL}/{settings.EMBEDDING_MODEL_NAME}"
    headers = {"Content-Type": "application/json"}
    if settings.HF_API_TOKEN:
        headers["Authorization"] = f"Bearer {settings.HF_API_TOKEN}"

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, headers=headers, json={"inputs": texts})

        # Model may be cold-starting
        if response.status_code == 503:
            logger.info("HF model loading, retrying in 20s...")
            await asyncio.sleep(20)
            response = await client.post(url, headers=headers, json={"inputs": texts})

        if response.status_code >= 400:
            error_detail = response.text[:300]
            logger.error("HF API error %d: %s", response.status_code, error_detail)
            raise RuntimeError(f"Embedding API error ({response.status_code}): {error_detail}")

        raw = response.json()

    # HF feature-extraction may return [batch, tokens, dim] — mean pool to [batch, dim]
    if raw and isinstance(raw[0], list) and raw[0] and isinstance(raw[0][0], list):
        vectors = [np.mean(v, axis=0).tolist() for v in raw]
    else:
        vectors = raw

    # Normalize for cosine similarity
    arr = np.array(vectors, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    return (arr / norms).tolist()


async def encode_texts(texts: list[str]) -> list[list[float]]:
    """Encode texts into embeddings, batching as needed."""
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        embeddings = await _call_hf_embedding(batch)
        all_embeddings.extend(embeddings)
    return all_embeddings


async def generate_embeddings_for_chapter(
    db: AsyncSession, chapter_id: uuid.UUID
) -> int:
    """Generate and store embeddings for all dialogue lines in a chapter.
    Deletes existing embeddings first (safe for re-runs).
    Returns count of embeddings created.
    """
    result = await db.execute(
        select(DialogueLine)
        .where(DialogueLine.chapter_id == chapter_id)
        .order_by(DialogueLine.line_order)
    )
    lines = result.scalars().all()
    if not lines:
        return 0

    # Delete existing embeddings for re-runs
    line_ids = [line.id for line in lines]
    await db.execute(
        delete(Embedding).where(Embedding.dialogue_line_id.in_(line_ids))
    )

    # Generate embeddings
    texts = [line.text for line in lines]
    vectors = await encode_texts(texts)

    # Bulk insert
    embeddings = [
        Embedding(
            dialogue_line_id=line.id,
            embedding=vector,
            model_name=settings.EMBEDDING_MODEL_NAME,
        )
        for line, vector in zip(lines, vectors)
    ]
    db.add_all(embeddings)
    await db.flush()

    logger.info("Generated %d embeddings for chapter %s", len(embeddings), chapter_id)
    return len(embeddings)
