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

    def run(self, market: str) -> str:
        logger.info("ResearchAgent: fetching data for '%s'", market)

        clarified = self._clarify_market(market)

        overview_resp = call_tool("get_market_overview", {"market": clarified})
        market_overview = (
            overview_resp["result"] if overview_resp["success"] else {}
        )

        news_resp = call_tool("get_latest_news", {"market": clarified})
        latest_news = news_resp["result"] if news_resp["success"] else {}

        skills_resp = call_tool("get_skills_data", {"market": clarified})
        skills_data = skills_resp["result"] if skills_resp["success"] else {}

        learn_resp = call_tool("get_learning_resources", {"market": clarified})
        learning_resources = (
            learn_resp["result"] if learn_resp["success"] else {}
        )

        research_context = {
            "original_market": market,
            "clarified_market": clarified,
            "market_overview": market_overview,
            "latest_news": latest_news,
            "skills_data": skills_data,
            "learning_resources": learning_resources,
            "fetched_at": datetime.datetime.utcnow().isoformat(),
        }

        self.memory.set("market", market)
        self.memory.set("research", research_context)

        wiki_len = len(market_overview.get("wikipedia_summary", ""))
        web_count = len(market_overview.get("web_results", []))
        news_web = len(latest_news.get("web_news", []))
        hn_count = len(latest_news.get("hn_stories", []))
        skills_count = len(skills_data.get("skills_results", []))
        tools_count = len(skills_data.get("tools_results", []))
        learn_count = len(learning_resources.get("courses", []))

        fetched_time = datetime.datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")

        summary = (
            f"# Research Summary — {market}\n\n"
            f"_Analysis initiated: {fetched_time}_\n\n"
            f"## Data Collected\n"
            f"- **Wikipedia summary**: {wiki_len} characters\n"
            f"- **Market-size web results**: {web_count}\n"
            f"- **News web results**: {news_web}\n"
            f"- **HackerNews stories**: {hn_count}\n"
            f"- **Skills search results**: {skills_count}\n"
            f"- **Tools search results**: {tools_count}\n"
            f"- **Learning resources**: {learn_count}\n\n"
            f"All data fetched in real-time from DuckDuckGo, "
            f"Wikipedia, and HackerNews.\n"
        )
        return summary
