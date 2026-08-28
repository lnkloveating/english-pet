from typing import Protocol

from shengsheng_contracts import AgentTurnRequest, LearnerProfile


class ResponseProvider(Protocol):
    async def reply(
        self,
        request: AgentTurnRequest,
        profile: LearnerProfile,
        recast_text: str | None,
    ) -> str: ...


class StubResponseProvider:
    """Deterministic child-friendly replies for local development and contract tests."""

    async def reply(
        self,
        request: AgentTurnRequest,
        profile: LearnerProfile,
        recast_text: str | None,
    ) -> str:
        if recast_text:
            lead = recast_text
        elif request.transcript.strip():
            lead = "I hear you!"
        else:
            return "That's okay. You can say one word, like 'cat'."

        if profile.level <= 1:
            question = "Do you like it?"
        elif profile.level <= 3:
            question = "What happened next?"
        else:
            question = "How did that make you feel?"
        return f"{lead} {question}"
