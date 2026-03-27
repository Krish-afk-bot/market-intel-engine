import json
import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class TLDRAgent(BaseAgent):

    def run(self, market: str) -> dict:
        market_analysis = self.memory.get("market_analysis") or ""
        capabilities = self.memory.get("capabilities") or ""
        strategy = self.memory.get("strategy") or ""

        prompt = f"""You are a senior analyst who specializes in writing concise executive briefings.

Read this full market intelligence report about {market} and extract key facts for a summary card.

MARKET ANALYSIS:
{market_analysis[:1500]}

CAPABILITY ANALYSIS:
{capabilities[:1000]}

STRATEGY:
{strategy[:1000]}

Return ONLY a valid JSON object. No explanation. No markdown. Start directly with {{

{{
  "market_size": "<number + unit or 'Data unavailable'> Examples: '$190B', '$2.4T', '$800M', 'Emerging'",
  "growth_rate": "<percent + timeframe or 'Estimated'> Examples: '12% CAGR', '35% YoY', 'Declining'",
  "entry_difficulty": "<one word: LOW | MEDIUM | HIGH | VERY HIGH>",
  "entry_difficulty_reason": "<one sentence max explaining why. Be specific to this market.>",
  "best_opportunity": "<specific opportunity in 6 words max. Not generic. Must be from the report. Example: 'Cloud security for SMB segment' NOT: 'There are many opportunities'>",
  "biggest_risk": "<specific risk in 6 words max. Must be from the report. Example: 'Regulatory crackdown on data privacy' NOT: 'Market competition'>",
  "verdict": "<one sentence verdict on whether to enter this market. Opinionated. Not wishy-washy. Example: 'Attractive for well-funded teams with deep domain expertise — avoid if bootstrapping.' Max 20 words.>",
  "sentiment": "<BULLISH | NEUTRAL | BEARISH based on overall market analysis>",
  "top_3_companies": ["<company 1>", "<company 2>", "<company 3>"],
  "time_to_revenue": "<realistic estimate for new entrant to generate first revenue. Example: '12-18 months', '6-12 months', '2-3 years'>"
}}

Rules:
- Every field must be filled. No nulls. No empty strings.
- market_size and growth_rate must come from the report. If not in the report, write 'Estimated' + your professional assessment.
- top_3_companies must be real companies from the report. If fewer than 3 mentioned, use your knowledge and mark them as (est.)
- verdict must be opinionated. Never say 'it depends'.
- Return ONLY the JSON object."""

        system = """You are a precise data extraction engine that returns only valid JSON.
Never explain. Never add text outside the JSON.
Start your response with {{ and end with }}"""

        logger.info("TLDRAgent: generating summary for '%s'", market)
        raw = self.llm_call(prompt, system)

        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        try:
            data = json.loads(raw)
        except Exception:
            logger.warning("TLDRAgent: failed to parse JSON, using fallback")
            data = {
                "market_size": "Data unavailable",
                "growth_rate": "Estimated",
                "entry_difficulty": "MEDIUM",
                "entry_difficulty_reason": "Insufficient data for assessment.",
                "best_opportunity": "See full report for details",
                "biggest_risk": "See full report for details",
                "verdict": "Run analysis again for a complete assessment.",
                "sentiment": "NEUTRAL",
                "top_3_companies": ["See report", "for details", ""],
                "time_to_revenue": "Unknown",
            }

        self.memory.set("tldr", data)
        return data
