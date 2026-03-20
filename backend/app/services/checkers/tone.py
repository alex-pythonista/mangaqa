import logging
from collections import defaultdict

from sqlalchemy import select

from app.models.dialogue import DialogueLine
from app.services.checkers.base import BaseChecker, CheckerContext
from app.services.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a manga translation QA specialist. You analyze whether dialogue lines match
the scene's mood, context, and dramatic tone.

Consider: action scenes should have urgent/tense dialogue, emotional scenes should have
appropriate emotional register, comedy scenes allow informal/playful tone, etc.

Respond in JSON format:
[
  {
    "line_index": 0,
    "has_tone_mismatch": true,
    "severity": "critical",
    "expected_tone": "tense/urgent",
    "actual_tone": "casual/relaxed",
    "explanation": "In a battle scene, this casual greeting breaks immersion",
    "suggestion": "rephrase suggestion"
  }
]

Use "critical" for jarring mismatches that break immersion, "warning" for mild issues.
Most lines should pass. Only flag genuine problems."""

MIN_SCENE_LINES = 3


class ToneChecker(BaseChecker):
    checker_type = "tone"

    def __init__(self, llm: OpenRouterClient) -> None:
        self._llm = llm

    async def run(self, ctx: CheckerContext) -> int:
        # Fetch all lines grouped by page
        result = await ctx.db.execute(
            select(DialogueLine)
            .where(DialogueLine.chapter_id.in_(ctx.chapter_ids))
            .order_by(DialogueLine.page_number, DialogueLine.line_order)
        )
        lines = result.scalars().all()

        if not lines:
            return 0

        # Group by page
        pages: dict[int, list[DialogueLine]] = defaultdict(list)
        for line in lines:
            pages[line.page_number].append(line)

        # Merge adjacent small pages into scene blocks
        scenes: list[list[DialogueLine]] = []
        current_scene: list[DialogueLine] = []
        current_pages: list[int] = []

        for page_num in sorted(pages.keys()):
            current_scene.extend(pages[page_num])
            current_pages.append(page_num)
            if len(current_scene) >= MIN_SCENE_LINES:
                scenes.append(current_scene)
                current_scene = []
                current_pages = []

        if current_scene:
            if scenes:
                scenes[-1].extend(current_scene)
            else:
                scenes.append(current_scene)

        count = 0
        for scene_lines in scenes:
            if len(scene_lines) < 2:
                continue

            # Build scene transcript
            scene_pages = sorted(set(l.page_number for l in scene_lines))
            page_range = (
                f"Page {scene_pages[0]}"
                if len(scene_pages) == 1
                else f"Pages {scene_pages[0]}-{scene_pages[-1]}"
            )

            transcript_lines = []
            for i, line in enumerate(scene_lines):
                speaker_info = f"{line.speaker}, " if line.speaker else ""
                transcript_lines.append(
                    f"Line {i} (page {line.page_number}, panel {line.panel_id}, "
                    f"{speaker_info}{line.line_type}): \"{line.text}\""
                )

            user_prompt = (
                f"Scene: {page_range}\n\n"
                + "\n".join(transcript_lines)
            )

            results = await self._llm.chat_json(SYSTEM_PROMPT, user_prompt)
            if not isinstance(results, list):
                continue

            for item in results:
                if not isinstance(item, dict) or not item.get("has_tone_mismatch"):
                    continue
                idx = item.get("line_index", 0)
                if idx >= len(scene_lines):
                    continue
                flagged_line = scene_lines[idx]
                severity = item.get("severity", "warning")
                if severity not in ("critical", "warning"):
                    severity = "warning"

                await self._save_result(
                    ctx=ctx,
                    severity=severity,
                    title="Tone mismatch in dialogue",
                    description=item.get("explanation", "Dialogue tone doesn't match scene mood"),
                    dialogue_line_id=flagged_line.id,
                    suggestion=item.get("suggestion"),
                    context={
                        "page_numbers": scene_pages,
                        "expected_tone": item.get("expected_tone"),
                        "actual_tone": item.get("actual_tone"),
                        "scene_line_count": len(scene_lines),
                    },
                )
                count += 1

        logger.info("Tone checker: found %d issues", count)
        return count
