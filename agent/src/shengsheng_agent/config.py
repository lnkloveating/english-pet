import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    provider: str = os.getenv("AGENT_PROVIDER", "stub")
    asr_provider: str = os.getenv("ASR_PROVIDER", "stub")
    doubao_asr_api_key: str | None = os.getenv("DOUBAO_ASR_API_KEY") or None
    doubao_asr_app_key: str | None = os.getenv("DOUBAO_ASR_APP_KEY") or None
    doubao_asr_access_token: str | None = os.getenv("DOUBAO_ASR_ACCESS_TOKEN") or None
    doubao_asr_resource_id: str = os.getenv(
        "DOUBAO_ASR_RESOURCE_ID", "volc.seedasr.sauc.duration"
    )
    doubao_asr_ws_url: str = os.getenv(
        "DOUBAO_ASR_WS_URL",
        "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async",
    )
    doubao_asr_timeout_seconds: float = float(
        os.getenv("DOUBAO_ASR_TIMEOUT_SECONDS", "30")
    )
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
