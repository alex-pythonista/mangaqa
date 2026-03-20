import logging
import re

from sqlalchemy import select

from app.models.dialogue import DialogueLine
from app.services.checkers.base import BaseChecker, CheckerContext

logger = logging.getLogger(__name__)

JAPANESE_PATTERN = re.compile(
    r"[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF65-\uFF9F]+"
)


class UntranslatedChecker(BaseChecker):
    checker_type = "untranslated"

    async def run(self, ctx: CheckerContext) -> int:
        result = await ctx.db.execute(
            select(DialogueLine)
            .where(DialogueLine.chapter_id.in_(ctx.chapter_ids))
            .order_by(DialogueLine.line_order)
        )
        lines = result.scalars().all()

        count = 0
        for line in lines:
            matches = JAPANESE_PATTERN.findall(line.text)
            if not matches:
                continue

            jp_char_count = sum(len(m) for m in matches)
            total_chars = len(re.sub(r"\s", "", line.text))
            ratio = jp_char_count / total_chars if total_chars > 0 else 0

            severity = "critical" if ratio >= 0.8 else "warning"
            title = (
                "Fully untranslated line"
                if ratio >= 0.8
                else "Partially untranslated text"
            )

            await self._save_result(
                ctx=ctx,
                severity=severity,
                title=title,
                description=f"Japanese text found: {''.join(matches)}",
                dialogue_line_id=line.id,
                suggestion="Translate the remaining Japanese text",
                context={
                    "japanese_fragments": matches,
                    "japanese_ratio": round(ratio, 3),
                    "page_number": line.page_number,
                    "speaker": line.speaker,
                },
            )
            count += 1

        logger.info("Untranslated checker: found %d issues", count)
        return count
