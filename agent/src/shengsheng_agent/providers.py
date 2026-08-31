from typing import Protocol

from shengsheng_contracts import AgentTurnRequest, LearnerProfile

from .prompts import AgentPrompt


class ResponseProvider(Protocol):
    async def reply(
        self,
        request: AgentTurnRequest,
        profile: LearnerProfile,
        recast_text: str | None,
        prompt: AgentPrompt,
    ) -> str: ...


class StubResponseProvider:
    """Deterministic child-friendly replies for local development and contract tests."""

    async def reply(
        self,
        request: AgentTurnRequest,
        profile: LearnerProfile,
        recast_text: str | None,
        prompt: AgentPrompt,
    ) -> str:
        _ = prompt
        if recast_text:
            lead = recast_text
        elif request.transcript.strip():
            lead = "I hear you!"
        else:
            return "That's okay. You can say one word, like 'cat'."

        if profile.grade <= 2:
            question = "Do you like it?"
        elif profile.grade <= 4:
            question = "What happened next?"
        else:
            question = "Why do you think so?"
        return f"{lead} {question}"
