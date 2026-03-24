import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a chief strategy officer advising a board of directors. "
    "Be specific, brutally honest, and avoid motivational language. "
    "Every recommendation must be grounded in the data and analysis provided."
)


class StrategyAgent(BaseAgent):

    def run(self, market: str) -> str:
        market_analysis = self.memory.get("market_analysis") or "_Unavailable_"
        capabilities = self.memory.get("capabilities") or "_Unavailable_"
        research = self.memory.get("research") or {}

        news = research.get("latest_news", {})
        news_count = len(news.get("web_news", []))
        hn_count = len(news.get("hn_stories", []))

        prompt = f"""You are a chief strategy officer.

Here is a complete market and capability analysis for **{market}**:

## MARKET ANALYSIS
{market_analysis}

## CAPABILITY ANALYSIS
{capabilities}

## RAW DATA SUMMARY
- Recent news articles found: {news_count}
- HackerNews stories found: {hn_count}

Write a strategic entry plan:

## Best Entry Paths
Specific strategies. Not generic advice.
What angle gives a new entrant the best chance?

## Who Should Enter Now
Exact profile. Skills, resources, timing.

## Who Should Wait
What is missing? What needs to be fixed first?

## Unfair Advantages
What gives an entrant an edge that cannot be copied?

## Key Risks
What kills most entrants in this market?
Be brutally honest. No motivational language."""

        logger.info("StrategyAgent: running LLM analysis for '%s'", market)
        result = self.llm_call(prompt, system=SYSTEM_PROMPT)
        self.memory.set("strategy", result)
        return result