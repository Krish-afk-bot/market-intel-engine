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


class MarketAgent(BaseAgent):

    def run(self, market: str) -> str:
        research = self.memory.get("research") or {}

        prompt = f"""You are a senior market analyst writing in 2025.
You specialize in industry and business market analysis.

Here is real-time data gathered about the {market} market:

WIKIPEDIA BACKGROUND:
{research.get("market_overview", {}).get("wikipedia_summary", "Not available")}

MARKET SIZE AND GROWTH:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("market_overview", {}).get("web_results", [])])}

TOP COMPANIES AND MARKET LEADERS:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("market_overview", {}).get("players_results", [])])}

FUNDING AND INVESTMENT ACTIVITY:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("market_overview", {}).get("funding_results", [])])}

DISRUPTION AND INNOVATION:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("market_overview", {}).get("disruption_results", [])])}

INDUSTRY NEWS (2025):
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("latest_news", {}).get("web_news", [])])}

HACKERNEWS DEVELOPER SENTIMENT (low weight — context only):
{chr(10).join([f"- {s.get('title', 'N/A')}" for s in research.get("latest_news", {}).get("hn_stories", [])])}

---

CRITICAL RULES FOR THIS ANALYSIS:

1. DATA SOURCE HIERARCHY — follow this strictly:

HIGHEST WEIGHT: Industry web results, news, funding data
MEDIUM WEIGHT: Wikipedia background context
LOWEST WEIGHT: HackerNews stories

HackerNews point scores do NOT indicate market importance.
A post with 1800 HN points about a consumer product does NOT
mean that product is a market trend.

Use HN only to understand developer and technical sentiment.
Never cite HN as evidence for business market trends.

2. MARKET SCOPE:

You are analyzing the {market} as an INDUSTRY and BUSINESS MARKET.

Focus on: enterprises, B2B dynamics, institutional players,
investment flows, professional workforce, and industry structure.

Ignore: viral consumer content, hobbyist communities,
or social media trends unless they directly impact the industry.

3. FACTUAL DISCIPLINE:

If a specific number appears in the data above, use it.
If no number appears, provide a reasoned estimate and
label it clearly as "estimated".

Do not cite data older than 2022.
Do not invent company names or statistics.

Write a deep market analysis with these exact sections:

## Dominant Market Narrative
What is the single most important business story this industry is telling in 2025?
Who is driving it — enterprises, startups, or investors?
Why does this narrative exist now and not 2 years ago?
Ground every sentence in the data above.

## Current Trends (with evidence)
List 4-6 trends confirmed by the INDUSTRY DATA above.
Ignore any trend that is only supported by HN posts.

Format each as:
**[Trend Name]** → Evidence: [specific source from data]
→ Momentum: [rising/stable/declining] → Why: [reason]

After confirmed trends, add 1-2 hidden trends the
industry data hints at but does not state explicitly.

## Future Outlook
Base case (12 months): specific scenario with numbers
where data supports it. Label estimates clearly.

Bull case: state exact conditions required.

Key risks: 3-4 specific risks with realistic impact.
Each risk must be grounded in something from the data.

Be analytical, direct, and opinionated.
Write for a professional investor or executive audience."""

        logger.info("MarketAgent: running LLM analysis for '%s'", market)
        result = self.llm_call(prompt, system=SYSTEM_PROMPT)
        self.memory.set("market_analysis", result)
        return result