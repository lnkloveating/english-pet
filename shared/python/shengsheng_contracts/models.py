from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LearnerProfile(ContractModel):
    grade: int = Field(default=1, ge=1, le=6)
    level: int = Field(default=1, ge=1, le=5)
    confidence: float = Field(default=0.5, ge=0, le=1)
    target_sentence_words: int = Field(default=4, ge=1, le=20)
    interests: list[str] = Field(default_factory=list)
    recent_topics: list[str] = Field(default_factory=list)


class AudioMetadata(ContractModel):
    duration_ms: int | None = Field(default=None, ge=0)
    asr_confidence: float | None = Field(default=None, ge=0, le=1)
    detected_language: str | None = None
    is_human_voice: bool | None = None


class ContextMessage(ContractModel):
    role: Literal["child", "pet"]
    text: str


class AgentTurnRequest(ContractModel):
    session_id: str = Field(min_length=1)
    child_id: str = Field(min_length=1)
    transcript: str = Field(max_length=1000)
    learner_profile: LearnerProfile
    audio_metadata: AudioMetadata | None = None
    context: list[ContextMessage] = Field(default_factory=list, max_length=10)


class RewardDecision(ContractModel):
    valid_speaking_attempt: bool
    base_voice_fruit: int = Field(ge=0)
    bonus_voice_fruit: int = Field(ge=0)
    reasons: list[str]


class SafetyResult(ContractModel):
    action: Literal["allow", "redirect", "trusted_adult"]
    reason_code: str


class AgentTurnResponse(ContractModel):
    turn_id: str
    reply_text: str
    teaching_action: Literal["encourage", "recast", "scaffold", "redirect"]
    recast_text: str | None = None
    reward: RewardDecision
    learner_profile: LearnerProfile
    safety: SafetyResult


class PetJobStatus(StrEnum):
    QUEUED = "queued"
    STRUCTURING = "structuring"
    GENERATING_CONCEPT = "generating_concept"
    REVIEW_REQUIRED = "review_required"
    GENERATING_3D = "generating_3d"
    COMPLETED = "completed"
    FAILED = "failed"


class PetSpecification(ContractModel):
    species: Literal["cat", "dog", "fox", "dinosaur", "dragon"]
    primary_color: str
    personality: str
    theme: str
    style: Literal["child-friendly"] = "child-friendly"
    accessories: list[str] = Field(default_factory=list, max_length=3)


class PetJobRequest(ContractModel):
    child_id: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=500)
    output_mode: Literal["concept_2d", "template_3d"] = "concept_2d"


class PetJobResponse(ContractModel):
    job_id: str
    status: PetJobStatus
    created_at: datetime
    specification: PetSpecification | None = None
    concept_image_url: HttpUrl | None = None
    model_url: HttpUrl | None = None
    error_code: str | None = None


class ErrorDetail(ContractModel):
    code: str
    message: str
    request_id: str
    retryable: bool = False


class ErrorResponse(ContractModel):
    error: ErrorDetail
