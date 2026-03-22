import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# Always load .env from the project root (two levels up from llm/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(_ENV_PATH)


class GroqClient:
    """Thin wrapper around the Groq chat-completion API."""

    MODEL = "llama-3.1-8b-instant"
    TEMPERATURE = 0.3
    MAX_TOKENS = 4096

    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is not set. "
                "Get a free key at https://console.groq.com"
            )
        self.client = Groq(api_key=api_key)
        self.call_count: int = 0
        self.total_tokens: int = 0