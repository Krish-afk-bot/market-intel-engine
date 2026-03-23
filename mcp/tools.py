import logging
import urllib.parse
from typing import Any, Callable

import requests
import wikipedia
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

_TOOL_REGISTRY: dict[str, Callable] = {}


def _register(name: str):
    def decorator(fn):
        _TOOL_REGISTRY[name] = fn
        return fn
    return decorator


def call_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    fn = _TOOL_REGISTRY.get(tool_name)
    if fn is None:
        return {
            "tool": tool_name,
            "result": None,
            "source": "unknown",
            "success": False,
            "error": f"Unknown tool: {tool_name}",
        }
    try:
        result = fn(**arguments)
        return {
            "tool": tool_name,
            "result": result,
            "source": result.get("source", "unknown"),
            "success": True,
        }
    except Exception as exc:
        logger.warning("Tool %s failed: %s", tool_name, exc)
        return {
            "tool": tool_name,
            "result": None,
            "source": "error",
            "success": False,
            "error": str(exc),
        }


@_register("web_search")
def web_search(query: str, max_results: int = 5) -> dict:
    try:
        raw = DDGS().text(query, max_results=max_results)
        results = [
            {
                "title": r.get("title", ""),
                "snippet": r.get("body", r.get("snippet", "")),
                "url": r.get("href", r.get("url", "")),
            }
            for r in raw
        ]
    except Exception as exc:
        logger.warning("web_search failed: %s", exc)
        results = []
    return {
        "results": results,
        "query": query,
        "source": "DuckDuckGo",
    }


@_register("get_market_overview")
def get_market_overview(market: str) -> dict:
    wiki_summary = ""
    try:
        wiki_summary = wikipedia.summary(market, sentences=8)
    except wikipedia.exceptions.DisambiguationError:
        try:
            wiki_summary = wikipedia.summary(market + " industry overview", sentences=8)
        except Exception:
            wiki_summary = ""
    except wikipedia.exceptions.PageError:
        wiki_summary = ""
    except Exception:
        wiki_summary = ""
    
    web_results = web_search(f"{market} industry market size revenue billion growth rate 2024 2025 report", max_results=5)
    funding_results = web_search(f"{market} industry venture capital investment funding rounds startups 2024 2025", max_results=3)
    players_results = web_search(f"{market} industry top companies market leaders market share enterprise 2025", max_results=3)
    disruption_results = web_search(f"{market} industry disruption innovation emerging trends technology 2025", max_results=3)
    
    return {
        "wikipedia_summary": wiki_summary,
        "web_results": web_results.get("results", []),
        "funding_results": funding_results.get("results", []),
        "players_results": players_results.get("results", []),
        "disruption_results": disruption_results.get("results", []),
        "source": "Wikipedia + DuckDuckGo"
    }


@_register("get_latest_news")
def get_latest_news(market: str) -> dict:
    web_news = web_search(f"{market} industry news analysis market update 2025", max_results=5)
    disruption_news = web_search(f"{market} industry disruption new entrants innovation startups 2025", max_results=3)
    
    hn_stories = []
    try:
        encoded_market = urllib.parse.quote(market)
        url = (f"https://hn.algolia.com/api/v1/search"
               f"?query={encoded_market}&tags=story&hitsPerPage=5")
        response = requests.get(url, timeout=10)
        hits = response.json().get("hits", [])
        hn_stories = [
            {
                "title": h.get("title", ""),
                "url": h.get("url", ""),
                "points": h.get("points", 0),
                "created_at": h.get("created_at", "")
            }
            for h in hits
        ]
    except Exception:
        hn_stories = []
    
    return {
        "web_news": web_news.get("results", []),
        "disruption_news": disruption_news.get("results", []),
        "hn_stories": hn_stories,
        "source": "DuckDuckGo + HackerNews"
    }


@_register("get_skills_data")
def get_skills_data(market: str) -> dict:
    skills_results = web_search(f"{market} professional job requirements skills qualifications hiring 2025", max_results=5)
    tools_results = web_search(f"{market} industry professional software tools platforms used by experts 2025", max_results=5)
    salary_results = web_search(f"{market} professional salary compensation average senior entry level 2025", max_results=3)
    hiring_results = web_search(f"{market} job market hiring demand LinkedIn Indeed careers 2025", max_results=3)
    
    return {
        "skills_results": skills_results.get("results", []),
        "tools_results": tools_results.get("results", []),
        "salary_results": salary_results.get("results", []),
        "hiring_results": hiring_results.get("results", []),
        "source": "DuckDuckGo"
    }


@_register("get_learning_resources")
def get_learning_resources(market: str) -> dict:
    courses = web_search(f"{market} professional certification courses training programs 2025", max_results=4)
    roadmap = web_search(f"how to become {market} professional career path entry level guide 2025", max_results=4)
    communities = web_search(f"{market} professional community association forum conference 2025", max_results=3)
    
    return {
        "courses": courses.get("results", []),
        "roadmap": roadmap.get("results", []),
        "communities": communities.get("results", []),
        "source": "DuckDuckGo"
    }
