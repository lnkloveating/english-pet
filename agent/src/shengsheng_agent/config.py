import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    provider: str = os.getenv("AGENT_PROVIDER", "stub")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
