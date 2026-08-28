"""Blender-side placeholder: invoke only inside an isolated worker.

Usage later:
    blender --background approved_base.blend --python export_template.py -- spec.json out.glb
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ALLOWED_SPECIES = {"cat", "dog", "fox", "dinosaur", "dragon"}


def validate_spec(spec_path: Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("species") not in ALLOWED_SPECIES:
        raise ValueError("unsupported_species")
    if len(spec.get("accessories", [])) > 3:
        raise ValueError("too_many_accessories")
    return spec


def main() -> None:
    args = sys.argv[sys.argv.index("--") + 1 :]
    if len(args) != 2:
        raise SystemExit("expected: spec.json output.glb")
    spec_path, output_path = map(Path, args)
    validate_spec(spec_path)

    # TODO: import bpy only in Blender, load an approved base asset, apply whitelisted
    # material/accessory parameters, validate triangle/texture budgets, then export GLB.
    raise NotImplementedError(f"Blender export placeholder: {output_path}")


if __name__ == "__main__":
    main()
