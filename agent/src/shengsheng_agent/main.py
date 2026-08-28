from fastapi import FastAPI
from shengsheng_contracts import AgentTurnRequest, AgentTurnResponse

from .service import AgentService

app = FastAPI(title="Shengsheng Agent", version="0.1.0")
service = AgentService()


@app.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "agent"}


@app.post("/v1/agent/turn", response_model=AgentTurnResponse)
async def create_turn(request: AgentTurnRequest) -> AgentTurnResponse:
    return await service.handle_turn(request)
