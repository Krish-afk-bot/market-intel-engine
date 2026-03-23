from abc import ABC, abstractmethod
from typing import Any

from core.cache import SimpleCache
from core.memory import AgentMemory
from llm.groq_client import GroqClient


class BaseAgent(ABC):

    def __init__(
        self,
        llm: GroqClient,
        cache: SimpleCache,
        memory: AgentMemory,
    ):
        self.llm = llm
        self.cache = cache
        self.memory = memory

    @abstractmethod
    def run(self, market: str) -> Any:
        ...

    def llm_call(self, prompt: str, system: str = "") -> str:
        cache_key = f"{system}|||{prompt}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        result = self.llm.complete(prompt, system=system or None)
        self.cache.set(cache_key, result)
        return result
