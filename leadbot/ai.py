from typing import Protocol

from leadbot.config import Settings


class AIProvider(Protocol):
    async def analyze(self, message: str) -> str: ...


class HeuristicAIProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def analyze(self, message: str) -> str:
        return message.lower()


def build_ai_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "heuristic":
        return HeuristicAIProvider(settings)
    raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
