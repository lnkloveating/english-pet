import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    agent_service_url: str = os.getenv("AGENT_SERVICE_URL", "http://localhost:8001")
    pet_pipeline_url: str = os.getenv("PET_PIPELINE_URL", "http://localhost:8002")
    agent_timeout_seconds: float = 10.0
    pet_timeout_seconds: float = 3.0

    @property
    def agent_voice_url(self) -> str:
        base = self.agent_service_url.rstrip("/")
        if base.startswith("https://"):
            base = f"wss://{base.removeprefix('https://')}"
        elif base.startswith("http://"):
            base = f"ws://{base.removeprefix('http://')}"
        return f"{base}/v1/agent/voice"


settings = Settings()
