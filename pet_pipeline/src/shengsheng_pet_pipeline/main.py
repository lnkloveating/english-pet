from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, Header, status
from fastapi.responses import JSONResponse
from shengsheng_contracts import ErrorDetail, ErrorResponse, PetJobRequest, PetJobResponse

from .service import PetPipelineService

app = FastAPI(title="Shengsheng Pet Pipeline", version="0.1.0")
service = PetPipelineService()


@app.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "pet-pipeline"}


@app.post("/v1/pets/jobs", response_model=PetJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_pet_job(
    request: PetJobRequest,
    background_tasks: BackgroundTasks,
    idempotency_key: str | None = Header(default=None),
) -> PetJobResponse:
    # TODO: persist idempotency_key with a unique constraint when repository is replaced.
    _ = idempotency_key
    job = service.create(request)
    background_tasks.add_task(service.process, job.job_id, request)
    return job


@app.get("/v1/pets/jobs/{job_id}", response_model=PetJobResponse)
async def get_pet_job(job_id: str) -> PetJobResponse:
    job = service.get(job_id)
    if job is None:
        error = ErrorResponse(
            error=ErrorDetail(
                code="pet_job_not_found",
                message="The pet job was not found.",
                request_id=f"req_{uuid4().hex}",
                retryable=False,
            )
        )
        return JSONResponse(status_code=404, content=error.model_dump(mode="json"))
    return job
