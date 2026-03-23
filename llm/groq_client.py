import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(_ENV_PATH)


class GroqClient:

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

    def complete(self, prompt: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=messages,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
            )
            self.call_count += 1
            usage = response.usage
            if usage:
                self.total_tokens += usage.total_tokens
            return response.choices[0].message.content
        except Exception as exc:
            raise Exception(
                f"Groq API error (model={self.MODEL}): {exc}"
            ) from exc
