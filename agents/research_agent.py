import datetime
import logging

from agents.base_agent import BaseAgent
from mcp.tools import call_tool

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):

    def _clarify_market(self, market: str) -> str:
        disambiguation_map = {
            "trading": "financial trading stock market industry",
            "forex": "forex foreign exchange trading market",
            "crypto": "cryptocurrency blockchain trading market",
            "ai": "artificial intelligence software market",
            "ml": "machine learning AI software industry",
            "cloud": "cloud computing services market",
            "saas": "software as a service SaaS market",
            "fintech": "financial technology fintech market",
            "health": "healthcare technology market",
            "food": "food and beverage industry market",
        }
        
        key = market.lower().strip()
        for trigger, clarified in disambiguation_map.items():
            if trigger in key:
                return clarified
        return market
    