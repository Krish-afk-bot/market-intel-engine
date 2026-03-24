import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a senior talent strategist and technical career advisor. "
    "You produce actionable capability analyses grounded in real data. "
    "Go beyond the raw data — add strategic insight."
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


class CapabilityAgent(BaseAgent):

    def run(self, market: str) -> str:
        research = self.memory.get("research") or {}

        prompt = f"""You are a senior talent and workforce strategist
writing in 2025. You specialize in professional career markets.

Here is real-time data about skills and careers in {market}:

JOB REQUIREMENTS AND QUALIFICATIONS:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("skills_data", {}).get("skills_results", [])])}

PROFESSIONAL TOOLS AND SOFTWARE:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("skills_data", {}).get("tools_results", [])])}

SALARY AND COMPENSATION DATA:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("skills_data", {}).get("salary_results", [])])}

HIRING AND JOB MARKET DATA:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("skills_data", {}).get("hiring_results", [])])}

COURSES AND CERTIFICATIONS:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("learning_resources", {}).get("courses", [])])}

CAREER ROADMAPS:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("learning_resources", {}).get("roadmap", [])])}

PROFESSIONAL COMMUNITIES:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("learning_resources", {}).get("communities", [])])}

---

CRITICAL RULES:

1. TOOLS RULE:
Only list tools that are professional software, platforms,
hardware, or frameworks used in actual job roles.

NEVER list these as industry tools:
- Wikipedia, GeeksforGeeks, Britannica, Investopedia
- Any .edu website or tutorial platform
- News websites or blogs

These are research sources, not professional tools.

2. SKILLS RULE:
Only list skills that appear in job requirements data.
If the data is sparse, use your expert knowledge for
this specific industry and label it "Expert assessment".
Never list skills from unrelated industries.

3. SALARY RULE:
If salary data exists, cite specific ranges.
If no data exists, provide industry-standard estimates
based on your knowledge and label as "Estimated".
Always include entry-level vs senior comparison.

Write a capability analysis with these exact sections:

## Core Skills Required
List 5-8 skills confirmed by the job data above.
For each skill:
- Why it matters specifically in {market}
- Demand trend: rising / stable / declining + reason
- What most job postings get wrong about this skill

## Professional Tools and Platforms
Separate into two clear groups:

ESSENTIAL (used in most professional roles):
[list with brief explanation of each]

SPECIALIZED (used in specific roles or advanced positions):
[list with brief explanation of each]

If data is insufficient, use expert assessment and label it.

## Salary and Demand Reality
Entry level range: [range or estimate]
Mid-level range: [range or estimate]
Senior level range: [range or estimate]

Highest paying specialization: [with reason]
Most in-demand role right now: [with reason from data]

## Learning Roadmap
Beginner (0-6 months):
Cite specific resources from the courses/roadmap data.
Give 3 concrete weekly actions.

Intermediate (6-18 months):
What 2-3 real projects prove competence to employers?
Which certifications appear in the job data?

Advanced (18+ months):
What is the single biggest skill gap between mid and senior?
Where do the top experts in this field gather and what
do they discuss based on the community data?"""

        logger.info("CapabilityAgent: running LLM analysis for '%s'", market)
        result = self.llm_call(prompt, system=SYSTEM_PROMPT)
        self.memory.set("capabilities", result)
        return result

    def refine(self, market: str, improvement_instructions: str) -> str:
        research = self.memory.get("research") or {}
        original = self.memory.get("capabilities") or ""

        prompt = f"""You are a senior talent and capability strategist.
You previously wrote a capability analysis for {market}.
A quality control review found specific problems with it.

YOUR ORIGINAL ANALYSIS:
{original}

QUALITY CONTROL FEEDBACK — YOU MUST FIX THESE ISSUES:
{improvement_instructions}

ORIGINAL RESEARCH DATA:

JOB REQUIREMENTS:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("skills_data", {}).get("skills_results", [])])}

PROFESSIONAL TOOLS:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("skills_data", {}).get("tools_results", [])])}

SALARY DATA:
{chr(10).join([f"- {r.get('title', 'N/A')}: {r.get('snippet', '')}" for r in research.get("skills_data", {}).get("salary_results", [])])}

Rewrite the full capability analysis.
Directly fix every issue listed in the feedback above.
Maintain the same structure:
## Core Skills Required
## Professional Tools and Platforms
## Salary and Demand Reality
## Learning Roadmap

Do not mention that this is a rewrite or that feedback
was received. Write as a clean final analysis."""

        system = """You are a senior talent strategist.
You write clear, specific, grounded capability analysis.
You incorporate feedback directly without mentioning it."""

        logger.info("CapabilityAgent: refining analysis for '%s'", market)
        result = self.llm_call(prompt, system)
        self.memory.set("capabilities", result)
        return result
