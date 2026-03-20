import logging

import numpy as np
from sqlalchemy import func, select

from app.models.dialogue import DialogueLine
from app.models.embedding import Embedding
from app.services.checkers.base import BaseChecker, CheckerContext
from app.services.openrouter import OpenRouterClient
from app.services.similarity import (
    compute_speaker_centroid,
    find_speaker_outliers,
    find_speaker_typical,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a manga translation QA specialist. You analyze whether a character's dialogue
is consistent with their established speech patterns and personality.

Respond in JSON format:
[
  {
    "line_index": 0,
    "is_out_of_character": true,
    "explanation": "brief explanation of why this line doesn't match the character's voice",
    "suggestion": "how to rephrase to match character voice"
  }
]

Only flag lines that genuinely break character voice. Different topics are fine — focus
on tone, formality level, vocabulary, and speech mannerisms."""

MIN_LINES_PER_SPEAKER = 5


class VoiceChecker(BaseChecker):
    checker_type = "voice"

    def __init__(self, llm: OpenRouterClient) -> None:
        self._llm = llm

    async def run(self, ctx: CheckerContext) -> int:
        # Get speakers with enough lines
        stmt = (
            select(DialogueLine.speaker, func.count(DialogueLine.id).label("cnt"))
            .where(
                DialogueLine.chapter_id.in_(ctx.chapter_ids),
                DialogueLine.speaker.isnot(None),
                DialogueLine.line_type == "dialogue",
            )
            .group_by(DialogueLine.speaker)
            .having(func.count(DialogueLine.id) >= MIN_LINES_PER_SPEAKER)
        )
        result = await ctx.db.execute(stmt)
        speakers = [(row.speaker, row.cnt) for row in result.all()]

        if not speakers:
            logger.info("Voice checker: no speakers with enough lines")
            return 0

        count = 0
        for speaker, total_lines in speakers:
            centroid = await compute_speaker_centroid(ctx.db, ctx.chapter_ids, speaker)
            if centroid is None:
                continue

            outliers = await find_speaker_outliers(
                ctx.db, ctx.chapter_ids, speaker, centroid
            )
            if not outliers:
                continue

            # Compute distance stats for threshold
            all_distances = [o["distance"] for o in outliers]
            typical = await find_speaker_typical(
                ctx.db, ctx.chapter_ids, speaker, centroid
            )

            # Only keep outliers with meaningful distance
            mean_dist = np.mean(all_distances) if all_distances else 0
            if mean_dist < 0.2:
                continue  # Speaker is very consistent, skip

            # Build LLM prompt
            typical_texts = [
                f'{i+1}. "{t["text"]}"' for i, t in enumerate(typical)
            ]
            outlier_texts = [
                f'{i}. (page {o["page_number"]}) "{o["text"]}"'
                for i, o in enumerate(outliers)
            ]

            user_prompt = (
                f'Character: "{speaker}" (appears in {total_lines} lines)\n\n'
                f"Typical dialogue examples (representative of this character's voice):\n"
                + "\n".join(typical_texts)
                + "\n\nLines to check (flagged as potentially out of character):\n"
                + "\n".join(outlier_texts)
            )

            results = await self._llm.chat_json(SYSTEM_PROMPT, user_prompt)
            if not isinstance(results, list):
                continue

            for item in results:
                if not isinstance(item, dict) or not item.get("is_out_of_character"):
                    continue
                idx = item.get("line_index", 0)
                if idx >= len(outliers):
                    continue
                outlier = outliers[idx]

                await self._save_result(
                    ctx=ctx,
                    severity="warning",
                    title=f"Out-of-character dialogue for {speaker}",
                    description=item.get("explanation", "Dialogue breaks character voice"),
                    dialogue_line_id=outlier["id"],
                    suggestion=item.get("suggestion"),
                    context={
                        "speaker": speaker,
                        "total_lines": total_lines,
                        "centroid_distance": round(outlier["distance"], 3),
                        "typical_examples": [t["text"] for t in typical[:3]],
                    },
                )
                count += 1

        logger.info("Voice checker: found %d issues", count)
        return count
