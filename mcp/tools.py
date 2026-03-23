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
