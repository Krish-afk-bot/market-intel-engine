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
