import hashlib
from typing import Optional


class SimpleCache:

    def __init__(self):
        self._store: dict[str, str] = {}
        self.hit_count: int = 0

    @staticmethod
    def _key(prompt: str) -> str:
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    def get(self, prompt: str) -> Optional[str]:
        key = self._key(prompt)
        value = self._store.get(key)
        if value is not None:
            self.hit_count += 1
        return value

    def set(self, prompt: str, value: str) -> None:
        self._store[self._key(prompt)] = value

    def reset(self) -> None:
        self._store.clear()
        self.hit_count = 0
