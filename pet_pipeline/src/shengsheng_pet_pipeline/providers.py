from typing import Protocol

from shengsheng_contracts import PetSpecification


class ConceptImageProvider(Protocol):
    async def generate(self, specification: PetSpecification, job_id: str) -> str: ...


class StubConceptImageProvider:
    async def generate(self, specification: PetSpecification, job_id: str) -> str:
        # A stable URL shape lets the App integrate before a paid image provider is selected.
        return f"https://example.invalid/shengsheng/concepts/{job_id}.webp"


class BlenderAdapter(Protocol):
    async def build_from_template(self, specification: PetSpecification, job_id: str) -> str: ...


class DisabledBlenderAdapter:
    async def build_from_template(self, specification: PetSpecification, job_id: str) -> str:
        raise RuntimeError("blender_jobs_disabled")
