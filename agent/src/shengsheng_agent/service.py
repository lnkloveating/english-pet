from uuid import uuid4

from shengsheng_contracts import AgentTurnRequest, AgentTurnResponse, RewardDecision

from .policies import CorrectionPolicy, LearnerModel, RewardPolicy, SafetyPolicy
from .providers import ResponseProvider, StubResponseProvider


class AgentService:
    def __init__(self, provider: ResponseProvider | None = None) -> None:
        self.safety = SafetyPolicy()
        self.reward = RewardPolicy()
        self.correction = CorrectionPolicy()
        self.learner = LearnerModel()
        self.provider = provider or StubResponseProvider()

    async def handle_turn(self, request: AgentTurnRequest) -> AgentTurnResponse:
        safety = self.safety.evaluate(request.transcript)
        if safety.action != "allow":
            reward = RewardDecision(
                valid_speaking_attempt=False,
                base_voice_fruit=0,
                bonus_voice_fruit=0,
                reasons=["safety_redirect"],
            )
            reply = (
                "Please tell a trusted grown-up who can help you right now."
                if safety.action == "trusted_adult"
                else "Let's keep your private information safe. What animal do you like?"
            )
            return AgentTurnResponse(
                turn_id=f"turn_{uuid4().hex}",
                reply_text=reply,
                teaching_action="redirect",
                reward=reward,
                learner_profile=request.learner_profile,
                safety=safety,
            )

        reward = self.reward.evaluate(request)
        recast = self.correction.recast(request.transcript) if reward.valid_speaking_attempt else None
        updated_profile = self.learner.update(request.learner_profile, reward)
        reply = await self.provider.reply(request, updated_profile, recast)
        action = "recast" if recast else ("encourage" if reward.valid_speaking_attempt else "scaffold")

        return AgentTurnResponse(
            turn_id=f"turn_{uuid4().hex}",
            reply_text=reply,
            teaching_action=action,
            recast_text=recast,
            reward=reward,
            learner_profile=updated_profile,
            safety=safety,
        )
