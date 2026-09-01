from uuid import uuid4

import asyncio

import websockets
from fastapi import FastAPI, Header, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from shengsheng_contracts import (
    AgentTurnRequest,
    AgentTurnResponse,
    ErrorDetail,
    ErrorResponse,
    PetJobRequest,
    PetJobResponse,
)

from .clients import ServiceClient, UpstreamServiceError
from .config import settings

app = FastAPI(title="Shengsheng App API", version="0.1.0")
service_client = ServiceClient()


@app.exception_handler(UpstreamServiceError)
async def upstream_error_handler(
    request: Request, exc: UpstreamServiceError
) -> JSONResponse:
    _ = request
    error = ErrorResponse(
        error=ErrorDetail(
            code="upstream_unavailable",
            message="This part of the island is taking a short break. Please try again.",
            request_id=f"req_{uuid4().hex}",
            retryable=exc.retryable,
        )
    )
    return JSONResponse(status_code=503, content=error.model_dump(mode="json"))


@app.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "app-api"}


@app.websocket("/v1/voice")
async def voice_proxy(client: WebSocket) -> None:
    """Proxy the additive voice protocol without exposing Agent provider credentials."""
    await client.accept()
    try:
        async with websockets.connect(
            settings.agent_voice_url,
            max_size=2_100_000,
            open_timeout=settings.agent_timeout_seconds,
        ) as upstream:
            async def client_to_agent() -> None:
                while True:
                    message = await client.receive()
                    if message["type"] == "websocket.disconnect":
                        return
                    if message.get("bytes") is not None:
                        await upstream.send(message["bytes"])
                    elif message.get("text") is not None:
                        await upstream.send(message["text"])

            async def agent_to_client() -> None:
                async for message in upstream:
                    if isinstance(message, bytes):
                        await client.send_bytes(message)
                    else:
                        await client.send_text(message)

            tasks = [asyncio.create_task(client_to_agent()), asyncio.create_task(agent_to_client())]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            await asyncio.gather(*done, return_exceptions=True)
    except (WebSocketDisconnect, websockets.WebSocketException, OSError):
        try:
            await client.send_json({
                "type": "error",
                "error": {
                    "code": "voice_service_unavailable",
                    "message": "The voice service is taking a short break",
                    "retryable": True,
                },
            })
        except (RuntimeError, WebSocketDisconnect):
            pass
    finally:
        try:
            await client.close()
        except (RuntimeError, WebSocketDisconnect):
            pass


@app.post("/v1/sessions/{session_id}/turns", response_model=AgentTurnResponse)
async def create_session_turn(session_id: str, request: AgentTurnRequest) -> AgentTurnResponse:
    normalized_request = request.model_copy(update={"session_id": session_id})
    return await service_client.create_agent_turn(normalized_request)


@app.post("/v1/pets", response_model=PetJobResponse, status_code=202)
async def create_pet(
    request: PetJobRequest,
    idempotency_key: str | None = Header(default=None),
) -> PetJobResponse:
    return await service_client.create_pet_job(request, idempotency_key)


@app.get("/v1/pets/jobs/{job_id}", response_model=PetJobResponse)
async def get_pet_job(job_id: str) -> PetJobResponse:
    return await service_client.get_pet_job(job_id)
