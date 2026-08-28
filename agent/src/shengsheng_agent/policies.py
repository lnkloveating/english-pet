import hashlib
import re

from shengsheng_contracts import (
    AgentTurnRequest,
    LearnerProfile,
    RewardDecision,
    SafetyResult,
)


class SafetyPolicy:
    _trusted_adult_terms = (
        "kill myself",
        "hurt myself",
        "suicide",
        "自杀",
        "伤害自己",
    )
    _redirect_terms = (
        "my phone number",
        "my address",
        "my school is",
        "weapon",
        "porn",
        "电话号码",
        "我家地址",
        "我的学校",
        "武器",
    )

    def evaluate(self, text: str) -> SafetyResult:
        normalized = text.casefold()
        if any(term in normalized for term in self._trusted_adult_terms):
            return SafetyResult(action="trusted_adult", reason_code="high_risk_wellbeing")
        if any(term in normalized for term in self._redirect_terms):
            return SafetyResult(action="redirect", reason_code="privacy_or_inappropriate")
        return SafetyResult(action="allow", reason_code="none")


class RewardPolicy:
    _english_word = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

    def evaluate(self, request: AgentTurnRequest) -> RewardDecision:
        words = self._english_word.findall(request.transcript)
        metadata = request.audio_metadata
        human_voice = metadata is None or metadata.is_human_voice is not False
        language_ok = (
            metadata is None
            or not metadata.detected_language
            or metadata.detected_language.lower().startswith("en")
        )
        valid = bool(words) and human_voice and language_ok
        reasons = ["meaningful_english_attempt"] if valid else ["no_valid_english_attempt"]

        # Bonus should feel occasional, not like a visible score. Stable hashing keeps tests repeatable.
        bonus_eligible = valid and len(words) >= request.learner_profile.target_sentence_words + 2
        surprise_bucket = int(
            hashlib.sha256(f"{request.session_id}:{request.transcript}".encode()).hexdigest()[:2], 16
        )
        bonus = 1 if bonus_eligible and surprise_bucket % 3 == 0 else 0
        if bonus:
            reasons.append("clear_or_expanded_expression")

        return RewardDecision(
            valid_speaking_attempt=valid,
            base_voice_fruit=1 if valid else 0,
            bonus_voice_fruit=bonus,
            reasons=reasons,
        )


class CorrectionPolicy:
    _rules = (
        (re.compile(r"\bYesterday I go to ([^.?!]+)", re.IGNORECASE), r"Yesterday I went to \1"),
        (re.compile(r"\bI like dinosaur\b", re.IGNORECASE), "I like dinosaurs"),
        (re.compile(r"\bHe like\b", re.IGNORECASE), "He likes"),
        (re.compile(r"\bShe like\b", re.IGNORECASE), "She likes"),
    )

    def recast(self, text: str) -> str | None:
        for pattern, replacement in self._rules:
            corrected = pattern.sub(replacement, text).strip()
            if corrected != text.strip():
                return corrected.rstrip(".?!") + "."
        return None


class LearnerModel:
    def update(self, profile: LearnerProfile, reward: RewardDecision) -> LearnerProfile:
        if not reward.valid_speaking_attempt:
            return profile
        confidence = min(1.0, round(profile.confidence + 0.02, 2))
        target_words = profile.target_sentence_words
        if confidence >= 0.8 and target_words < 20:
            target_words += 1
        # Explicit construction avoids mutating input models shared with request validation.
        data = profile.model_dump()
        data.update(confidence=confidence, target_sentence_words=target_words)
        return LearnerProfile(**data)
