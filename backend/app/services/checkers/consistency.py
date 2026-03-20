import logging

from app.services.checkers.base import BaseChecker, CheckerContext
from app.services.openrouter import OpenRouterClient
from app.services.similarity import find_similar_pairs

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a manga translation QA specialist. You check for consistency in translated text.
Analyze pairs of similar dialogue lines and identify REAL translation inconsistencies
where the same term, name, or concept is translated differently.

Respond in JSON format:
[
  {
    "pair_index": 0,
    "is_inconsistent": true,
    "term": "the inconsistent term",
    "explanation": "brief explanation",
    "suggested_translation": "recommended consistent term"
  }
]

Only flag TRUE inconsistencies. Different sentences that happen to be similar are NOT inconsistencies.
Character names should always be translated the same way."""

BATCH_SIZE = 10


class ConsistencyChecker(BaseChecker):
    checker_type = "consistency"

    def __init__(self, llm: OpenRouterClient) -> None:
        self._llm = llm

    async def run(self, ctx: CheckerContext) -> int:
        pairs = await find_similar_pairs(ctx.db, ctx.chapter_ids)
        if not pairs:
            logger.info("Consistency checker: no similar pairs found")
            return 0

        count = 0
        for i in range(0, len(pairs), BATCH_SIZE):
            batch = pairs[i : i + BATCH_SIZE]
            prompt_lines = []
            for j, pair in enumerate(batch):
                prompt_lines.append(
                    f"Pair {j}:\n"
                    f"  A (page {pair['page_a']}, speaker: {pair['speaker_a'] or 'N/A'}): "
                    f"\"{pair['text_a']}\"\n"
                    f"  B (page {pair['page_b']}, speaker: {pair['speaker_b'] or 'N/A'}): "
                    f"\"{pair['text_b']}\""
                )

            user_prompt = (
                "Check these pairs of dialogue lines for translation inconsistencies:\n\n"
                + "\n\n".join(prompt_lines)
            )

            results = await self._llm.chat_json(SYSTEM_PROMPT, user_prompt)
            if not isinstance(results, list):
                continue

            for item in results:
                if not isinstance(item, dict) or not item.get("is_inconsistent"):
                    continue
                idx = item.get("pair_index", 0)
                if idx >= len(batch):
                    continue
                pair = batch[idx]

                await self._save_result(
                    ctx=ctx,
                    severity="warning",
                    title=f"Inconsistent translation: {item.get('term', 'unknown')}",
                    description=item.get("explanation", "Translation inconsistency detected"),
                    dialogue_line_id=pair["id_a"],
                    suggestion=item.get("suggested_translation"),
                    context={
                        "line_a_text": pair["text_a"],
                        "line_b_text": pair["text_b"],
                        "line_b_id": str(pair["id_b"]),
                        "similarity": round(1 - pair["distance"], 3),
                    },
                )
                count += 1

        logger.info("Consistency checker: found %d issues", count)
        return count
