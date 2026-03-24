import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a senior market analyst specializing in industry intelligence. "
    "You produce rigorous, data-grounded analysis. "
    "Never invent facts not present in the provided data."
)


def _fmt_web(results: list[dict]) -> str:
    if not results:
        return "_No results available._"
    lines = []
    for r in results:
        title = r.get("title", "Untitled")
        snippet = r.get("snippet", "")
        url = r.get("url", "")
        lines.append(f"- **{title}**: {snippet} ([link]({url}))")
    return "\n".join(lines)


def _fmt_hn(stories: list[dict]) -> str:
    if not stories:
        return "_No HackerNews stories found._"
    lines = []
    for s in stories:
        title = s.get("title", "Untitled")
        points = s.get("points", 0)
        url = s.get("url", "")
        lines.append(f"- **{title}** ({points} pts) ([link]({url}))")
    return "\n".join(lines)
