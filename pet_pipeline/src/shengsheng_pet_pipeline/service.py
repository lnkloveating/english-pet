from datetime import UTC, datetime
from uuid import uuid4

from pydantic import HttpUrl, TypeAdapter
from shengsheng_contracts import PetJobRequest, PetJobResponse, PetJobStatus

from .config import settings
from .description import PetDescriptionParser, PetSafetyRewriter
from .providers import (
    BlenderAdapter,
    ConceptImageProvider,
    DisabledBlenderAdapter,
    StubConceptImageProvider,
)
from .repository import InMemoryJobRepository

http_url_adapter = TypeAdapter(HttpUrl)


class PetPipelineService:
    def __init__(
        self,
        repository: InMemoryJobRepository | None = None,
        image_provider: ConceptImageProvider | None = None,
        blender: BlenderAdapter | None = None,
    ) -> None:
        self.repository = repository or InMemoryJobRepository()
        self.image_provider = image_provider or StubConceptImageProvider()
        self.blender = blender or DisabledBlenderAdapter()
        self.safety = PetSafetyRewriter()
        self.parser = PetDescriptionParser()

    def create(self, request: PetJobRequest) -> PetJobResponse:
        job = PetJobResponse(
            job_id=f"petjob_{uuid4().hex}",
            status=PetJobStatus.QUEUED,
            created_at=datetime.now(UTC),
        )
        self.repository.save(job)
        return job

    async def process(self, job_id: str, request: PetJobRequest) -> None:
        job = self._required(job_id)
        try:
            job.status = PetJobStatus.STRUCTURING
            safe_description = self.safety.rewrite(request.description)
            job.specification = self.parser.parse(safe_description)
            self.repository.save(job)

            job.status = PetJobStatus.GENERATING_CONCEPT
            concept_url = await self.image_provider.generate(job.specification, job_id)
            job.concept_image_url = http_url_adapter.validate_python(concept_url)

            if request.output_mode == "template_3d":
                if not settings.blender_enabled:
                    job.status = PetJobStatus.REVIEW_REQUIRED
                else:
                    job.status = PetJobStatus.GENERATING_3D
                    model_url = await self.blender.build_from_template(job.specification, job_id)
                    job.model_url = http_url_adapter.validate_python(model_url)
                    job.status = PetJobStatus.COMPLETED
            else:
                job.status = PetJobStatus.COMPLETED
            self.repository.save(job)
        # Provider SDKs expose different exception families; map all failures to the
        # public job state here and retain provider details only in protected logs later.
        except Exception:  # noqa: BLE001
            job.status = PetJobStatus.FAILED
            job.error_code = "pipeline_failed"
            self.repository.save(job)

    def get(self, job_id: str) -> PetJobResponse | None:
        return self.repository.get(job_id)

    def _required(self, job_id: str) -> PetJobResponse:
        job = self.repository.get(job_id)
        if job is None:
            raise KeyError(job_id)
        return job
