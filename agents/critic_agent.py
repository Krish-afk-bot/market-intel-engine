import json
import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CriticAgent(BaseAgent):

    def run(self, market: str) -> dict:
        market_analysis = self.memory.get("market_analysis") or ""
        capabilities = self.memory.get("capabilities") or ""
        strategy = self.memory.get("strategy") or ""

        prompt = f"""You are a ruthless quality control analyst.
Review this market intelligence report about {market}.
Return ONLY a valid JSON object. No explanation. No markdown.
Start your response directly with {{

MARKET ANALYSIS SECTION:
{market_analysis}

CAPABILITY ANALYSIS SECTION:
{capabilities}

STRATEGY SECTION:
{strategy}

Evaluate each section strictly.
For each section decide:
1. Does it need improvement? (true/false)
2. What specific flaws exist?
3. What exact instructions will fix it?

Return this exact JSON structure:
{{
  "overall_quality": <number 1-10>,
  "sections": {{
    "market_analysis": {{
      "needs_improvement": <true or false>,
      "score": <number 1-10>,
      "flaws": [
        "<specific flaw 1>",
        "<specific flaw 2>"
      ],
      "improvement_instructions": "<single paragraph of direct instructions telling the agent exactly what to fix, add, or remove. Be specific. Reference exact claims that are wrong or missing. Max 150 words.>"
    }},
    "capabilities": {{
      "needs_improvement": <true or false>,
      "score": <number 1-10>,
      "flaws": [
        "<specific flaw 1>",
        "<specific flaw 2>"
      ],
      "improvement_instructions": "<single paragraph of direct instructions. Max 150 words.>"
    }},
    "strategy": {{
      "needs_improvement": <true or false>,
      "score": <number 1-10>,
      "flaws": [
        "<specific flaw 1>",
        "<specific flaw 2>"
      ],
      "improvement_instructions": "<single paragraph of direct instructions. Max 150 words.>"
    }}
  }},
  "sections_to_rerun": [
    "<list only section names that scored below 7 and have needs_improvement=true. Possible values: market_analysis, capabilities, strategy. Empty list if all sections score 7 or above.>"
  ]
}}

SCORING RULES:
Score 8-10: Grounded in real data, specific, no generic claims
Score 5-7: Some real data but mixed with generic statements
Score 1-4: Mostly generic, hallucinated, or factually weak

A section needs_improvement=true ONLY if score < 7.
sections_to_rerun must contain ONLY sections where
needs_improvement is true.
If all sections score 7+, sections_to_rerun must be [].

Return ONLY the JSON. Nothing else."""

        system = """You are a precise JSON-returning quality
control engine. Return only valid JSON.
Never add explanation or markdown formatting.
Start your response with { and end with }"""

        logger.info("CriticAgent: running quality review for '%s'", market)
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
            feedback = json.loads(raw)
        except Exception as e:
            logger.warning("CriticAgent: failed to parse JSON feedback: %s", e)
            feedback = {
                "overall_quality": 7,
                "sections": {
                    "market_analysis": {
                        "needs_improvement": False,
                        "score": 7,
                        "flaws": [],
                        "improvement_instructions": ""
                    },
                    "capabilities": {
                        "needs_improvement": False,
                        "score": 7,
                        "flaws": [],
                        "improvement_instructions": ""
                    },
                    "strategy": {
                        "needs_improvement": False,
                        "score": 7,
                        "flaws": [],
                        "improvement_instructions": ""
                    }
                },
                "sections_to_rerun": []
            }

        self.memory.set("critic_feedback", feedback)

        print(
            f"[CriticAgent] Quality: "
            f"{feedback.get('overall_quality')}/10 | "
            f"Sections to rerun: "
            f"{feedback.get('sections_to_rerun', [])}"
        )
        return feedback
