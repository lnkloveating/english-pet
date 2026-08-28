import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    image_provider: str = os.getenv("PET_IMAGE_PROVIDER", "stub")
    blender_enabled: bool = os.getenv("ENABLE_BLENDER_JOBS", "false").lower() == "true"
    blender_executable: str = os.getenv("BLENDER_EXECUTABLE", "blender")


settings = Settings()
