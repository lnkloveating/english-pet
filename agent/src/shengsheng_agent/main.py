from fastapi import FastAPI, WebSocket
from shengsheng_contracts import AgentTurnRequest, AgentTurnResponse

from .asr import StreamingAsrProvider, build_asr_provider
from .config import Settings
from .service import AgentService
from .voice import VoiceConnection


def create_app(
    *,
    app_settings: Settings | None = None,
    agent_service: AgentService | None = None,
    asr_provider: StreamingAsrProvider | None = None,
) -> FastAPI:
    resolved_settings = app_settings or Settings()
    app = FastAPI(title="Shengsheng Agent", version="0.2.0")
    app.state.agent_service = agent_service or AgentService()
    app.state.asr_provider = asr_provider or build_asr_provider(resolved_settings)

    @app.get("/healthz")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "agent"}

    @app.post("/v1/agent/turn", response_model=AgentTurnResponse)
    async def create_turn(request: AgentTurnRequest) -> AgentTurnResponse:
        return await app.state.agent_service.handle_turn(request)

    @app.websocket("/v1/agent/voice")
    async def voice_turn(websocket: WebSocket) -> None:
        connection = VoiceConnection(
            websocket,
            agent_service=app.state.agent_service,
            asr_provider=app.state.asr_provider,
        )
        await connection.run()

    return app


app = create_app()
