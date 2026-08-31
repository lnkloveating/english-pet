from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class AsrAudioConfig:
    format: Literal["pcm"] = "pcm"
    sample_rate: int = 16_000
    bits: Literal[16] = 16
    channels: Literal[1] = 1


@dataclass(frozen=True)
class AsrTranscript:
    text: str
    is_final: bool
    confidence: float | None = None
    detected_language: str | None = None
