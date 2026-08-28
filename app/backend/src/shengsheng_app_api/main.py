from uuid import uuid4

from fastapi import FastAPI, Header, Request
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
