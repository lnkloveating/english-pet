from shengsheng_contracts import PetJobResponse


class InMemoryJobRepository:
    def __init__(self) -> None:
        self._jobs: dict[str, PetJobResponse] = {}

    def save(self, job: PetJobResponse) -> None:
        self._jobs[job.job_id] = job

    def get(self, job_id: str) -> PetJobResponse | None:
        return self._jobs.get(job_id)
