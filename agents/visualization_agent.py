import json
import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class VisualizationAgent(BaseAgent):

    def run(self, market: str) -> dict:
        market_analysis = self.memory.get("market_analysis") or ""
        capabilities = self.memory.get("capabilities") or ""
        strategy = self.memory.get("strategy") or ""
        critic = self.memory.get("critic_feedback") or ""

        prompt = f"""You are a data extraction specialist.
Read this market intelligence report about {market}
and extract structured data for charts.

MARKET ANALYSIS:
{market_analysis}

CAPABILITIES:
{capabilities}

STRATEGY:
{strategy}

CRITIC REVIEW:
{critic}

Extract data and return ONLY a valid JSON object.
No explanation. No markdown. No code fences.
Just the raw JSON object starting with {{

Return this exact structure:
{{
  "market_metrics": {{
    "market_name": "{market}",
    "estimated_size_billion": <extract number from report.
If exact number not found, estimate based on context
and scale of companies mentioned. Example: if report mentions a $50B company dominating the market, estimate
market at 100-200B. Never return null — always return
a number with your best estimate>,
    "growth_rate_percent": <extract from report.
If not explicitly stated, estimate based on trend momentum described. Fast growing = 25-40%.
Stable = 8-15%. Declining = 0-5%.
Never return null — always return a number>,
    "funding_activity_score": <number 1-10 based on report>,
    "market_maturity_score": <number 1-10, 1=emerging 10=mature>
  }},
  "trends": [
    {{
      "name": "<trend name, max 5 words>",
      "momentum": <number 1-10, 10=fastest growing>,
      "direction": "<rising|stable|declining>"
    }}
  ],
  "skills": [
    {{
      "name": "<skill name, max 3 words>",
      "demand_score": <number 1-10>,
      "rising": <true|false>
    }}
  ],
  "risks": [
    {{
      "name": "<risk name, max 4 words>",
      "probability": <number 1-10>,
      "impact": <number 1-10>
    }}
  ],
  "section_scores": {{
    "market_analysis": <number 1-10 from critic>,
    "capabilities": <number 1-10 from critic>,
    "strategy": <number 1-10 from critic>
  }},
  "entry_timeline": [
    {{
      "phase": "<phase name>",
      "duration": "<e.g. 0-6 months>",
      "key_action": "<single most important action, max 8 words>"
    }}
  ],
  "top_companies": [
    {{
      "name": "<company name>",
      "relevance_score": <number 1-10>
    }}
  ]
}}

Rules for top_companies:
- Extract minimum 5 companies, maximum 8
- If fewer than 5 are mentioned by name in the report,
  add well-known companies in this market from your knowledge and mark relevance_score as 5 for those
- Never return fewer than 5 companies

Rules:
- trends: extract 4-6 trends from the report
- skills: extract 5-8 skills from the report
- risks: extract 4-6 risks from the report
- entry_timeline: extract 3 phases (beginner/intermediate/advanced)
- top_companies: extract 4-6 companies mentioned in the report
- All scores must be numbers, never strings
- If a value cannot be determined from the report use null
- Return ONLY the JSON, nothing else"""

        system = """You are a precise data extraction engine.
You return only valid JSON. Never explain. Never add text.
Never wrap in code fences. Start your response with {"""

        logger.info("VisualizationAgent: extracting data for '%s'", market)
        raw = self.llm.complete(prompt, system=system)

        logger.debug("VisualizationAgent raw response (first 200 chars): %s", raw[:200])
        print(f"[VizAgent] Raw response start: {repr(raw[:120])}")

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
        else:
            logger.warning("VizAgent: no JSON object found in response")
            raw = "{}"

        data = None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            try:
                import ast
                import re
                fixed = re.sub(r'\bTrue\b', 'true', raw)
                fixed = re.sub(r'\bFalse\b', 'false', fixed)
                fixed = re.sub(r'\bNone\b', 'null', fixed)
                parsed = ast.literal_eval(fixed)
                data = json.loads(json.dumps(parsed))
                logger.info("VizAgent: recovered via ast.literal_eval")
            except Exception as e2:
                logger.warning("VizAgent: ast fallback also failed: %s", e2)
                print(f"[VizAgent] Both parse attempts failed. Raw: {repr(raw[:300])}")

        if data is None:
            logger.warning("Failed to parse visualization JSON: falling back to empty structure")
            data = {
                "market_metrics": {
                    "market_name": market,
                    "estimated_size_billion": None,
                    "growth_rate_percent": None,
                    "funding_activity_score": 5,
                    "market_maturity_score": 5
                },
                "trends": [],
                "skills": [],
                "risks": [],
                "section_scores": {
                    "market_analysis": 5,
                    "capabilities": 5,
                    "strategy": 5
                },
                "entry_timeline": [],
                "top_companies": []
            }

        self.memory.set("visualization_data", data)
        return data
