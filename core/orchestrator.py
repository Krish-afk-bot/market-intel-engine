import datetime
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.capability_agent import CapabilityAgent
from agents.critic_agent import CriticAgent
from agents.market_agent import MarketAgent
from agents.research_agent import ResearchAgent
from agents.strategy_agent import StrategyAgent
from agents.tldr_agent import TLDRAgent
from agents.visualization_agent import VisualizationAgent
from core.cache import SimpleCache
from core.memory import AgentMemory
from llm.groq_client import GroqClient

logger = logging.getLogger(__name__)


class Orchestrator:

    def __init__(self, api_key: str):
        import os
        os.environ["GROQ_API_KEY"] = api_key

        self.llm = GroqClient()
        self.cache = SimpleCache()
        self.memory = AgentMemory()

        self.research = ResearchAgent(self.llm, self.cache, self.memory)
        self.market = MarketAgent(self.llm, self.cache, self.memory)
        self.capability = CapabilityAgent(self.llm, self.cache, self.memory)
        self.strategy = StrategyAgent(self.llm, self.cache, self.memory)
        self.critic = CriticAgent(self.llm, self.cache, self.memory)
        self.visualization = VisualizationAgent(self.llm, self.cache, self.memory)
        self.tldr = TLDRAgent(self.llm, self.cache, self.memory)

    def run(self, market: str, progress_callback=None) -> dict:
        logger.info("Starting MNI pipeline for market: %s", market)
        start_time = time.time()
        analysis_start = datetime.datetime.utcnow()

        def update_progress(stage: str, message: str):
            if progress_callback:
                progress_callback(stage, message)
            logger.info("[%s] %s", stage, message)

        update_progress("Research", "Fetching live data from all sources...")
        self.research.run(market)
        update_progress("Research", "✓ Data collection complete")

        update_progress("Analysis", "Running market and capability analysis in parallel...")

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.market.run, market): "Market",
                executor.submit(self.capability.run, market): "Capability",
            }
            for future in as_completed(futures):
                agent_name = futures[future]
                try:
                    future.result()
                    update_progress("Analysis", f"✓ {agent_name} analysis complete")
                except Exception as exc:
                    logger.error("%s agent failed: %s", agent_name, exc)
                    raise

        update_progress("Strategy", "Synthesizing strategic entry plan...")
        self.strategy.run(market)
        update_progress("Strategy", "✓ Strategy synthesis complete")

        update_progress("Review", "Running quality review...")
        critic_feedback = self.critic.run(market)
        sections_to_rerun = critic_feedback.get("sections_to_rerun", [])
        update_progress("Review", "✓ Quality review complete")

        refinement_count = 0

        if sections_to_rerun:
            update_progress("Refinement", f"Refining {len(sections_to_rerun)} section(s)...")

        if "market_analysis" in sections_to_rerun:
            instructions = (
                critic_feedback.get("sections", {})
                .get("market_analysis", {})
                .get("improvement_instructions", "")
            )
            if instructions:
                self.market.refine(market, instructions)
                refinement_count += 1
                print("[Orchestrator] Refined: market_analysis")

        if "capabilities" in sections_to_rerun:
            instructions = (
                critic_feedback.get("sections", {})
                .get("capabilities", {})
                .get("improvement_instructions", "")
            )
            if instructions:
                self.capability.refine(market, instructions)
                refinement_count += 1
                print("[Orchestrator] Refined: capabilities")

        if "strategy" in sections_to_rerun:
            instructions = (
                critic_feedback.get("sections", {})
                .get("strategy", {})
                .get("improvement_instructions", "")
            )
            if instructions:
                self.strategy.refine(market, instructions)
                refinement_count += 1
                print("[Orchestrator] Refined: strategy")

        if refinement_count:
            update_progress("Refinement", f"✓ {refinement_count} section(s) refined")

        final_market = self.memory.get("market_analysis") or ""
        final_capabilities = self.memory.get("capabilities") or ""
        final_strategy = self.memory.get("strategy") or ""
        final_research = self.memory.get("research") or {}

        final_report = f"""# Market Intelligence Report — {market}

## 1. Market Analysis

{final_market}

## 2. Capability Analysis

{final_capabilities}

## 3. Strategic Entry Plan

{final_strategy}

---

*Report generated by Market Narrative Intelligence (MNI).
Data sourced in real-time from DuckDuckGo, Wikipedia,
and HackerNews. Self-refined using AI quality control.*
"""
        self.memory.set("final_report", final_report)

        update_progress("Visualization", "Extracting data for charts...")
        visualization_data = self.visualization.run(market)
        update_progress("Visualization", "✓ Visualization data ready")

        update_progress("Summary", "Generating executive summary...")
        tldr_data = self.tldr.run(market)
        update_progress("Summary", "✓ Executive summary ready")

        execution_time = time.time() - start_time

        return {
            "research_summary": self._format_research_summary(final_research, market),
            "market_analysis": final_market,
            "capabilities": final_capabilities,
            "strategy": final_strategy,
            "final_report": final_report,
            "visualization_data": visualization_data,
            "tldr": tldr_data,
            "llm_calls": self.llm.call_count,
            "tokens": self.llm.total_tokens,
            "cache_hits": self.cache.hit_count,
            "tool_calls": self._count_tool_calls(final_research),
            "execution_time": execution_time,
            "agents_executed": 6 + refinement_count,
            "refinements_made": refinement_count,
            "sections_refined": sections_to_rerun,
            "generated_at": analysis_start.strftime("%B %d, %Y at %H:%M UTC"),
            "generated_at_short": analysis_start.strftime("%Y-%m-%d %H:%M"),
            "generated_timestamp": analysis_start.isoformat(),
        }

    def reset(self):
        self.memory.clear()
        self.cache.reset()
        self.llm.call_count = 0
        self.llm.total_tokens = 0

    def _format_research_summary(self, research: dict, market: str) -> str:
        news_count = len(research.get("latest_news", {}).get("web_news", []))
        hn_count = len(research.get("latest_news", {}).get("hn_stories", []))
        players_count = len(
            research.get("market_overview", {}).get("players_results", [])
        )
        return (
            f"Research completed for **{market}**.\n\n"
            f"- Web news articles: {news_count}\n"
            f"- HackerNews stories: {hn_count}\n"
            f"- Market player results: {players_count}\n"
            f"- Wikipedia summary: available\n"
        )

    def _count_tool_calls(self, research: dict) -> int:
        count = 0
        if research.get("market_overview"):
            count += 4
        if research.get("latest_news"):
            count += 2
        if research.get("skills_data"):
            count += 4
        if research.get("learning_resources"):
            count += 3
        return count
