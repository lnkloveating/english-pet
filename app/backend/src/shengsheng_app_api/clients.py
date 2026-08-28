import httpx
from shengsheng_contracts import (
    AgentTurnRequest,
    AgentTurnResponse,
    PetJobRequest,
    PetJobResponse,
)

from .config import settings


class UpstreamServiceError(RuntimeError):
    def __init__(self, service: str, retryable: bool = True) -> None:
        super().__init__(f"{service}_unavailable")
        self.service = service
        self.retryable = retryable


class ServiceClient:
    async def create_agent_turn(self, request: AgentTurnRequest) -> AgentTurnResponse:
        try:
            async with httpx.AsyncClient(timeout=settings.agent_timeout_seconds) as client:
                response = await client.post(
                    f"{settings.agent_service_url}/v1/agent/turn",
                    json=request.model_dump(mode="json"),
                )
                response.raise_for_status()
            return AgentTurnResponse.model_validate(response.json())
        except (httpx.HTTPError, ValueError) as exc:
            raise UpstreamServiceError("agent") from exc

    async def create_pet_job(
        self, request: PetJobRequest, idempotency_key: str | None
    ) -> PetJobResponse:
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
        try:
            async with httpx.AsyncClient(timeout=settings.pet_timeout_seconds) as client:
                response = await client.post(
                    f"{settings.pet_pipeline_url}/v1/pets/jobs",
                    json=request.model_dump(mode="json"),
                    headers=headers,
                )
                response.raise_for_status()
            return PetJobResponse.model_validate(response.json())
        except (httpx.HTTPError, ValueError) as exc:
            raise UpstreamServiceError("pet_pipeline") from exc

    async def get_pet_job(self, job_id: str) -> PetJobResponse:
        try:
            async with httpx.AsyncClient(timeout=settings.pet_timeout_seconds) as client:
                response = await client.get(f"{settings.pet_pipeline_url}/v1/pets/jobs/{job_id}")
                response.raise_for_status()
            return PetJobResponse.model_validate(response.json())
        except (httpx.HTTPError, ValueError) as exc:
            raise UpstreamServiceError("pet_pipeline") from exc
