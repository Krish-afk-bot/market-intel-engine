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
