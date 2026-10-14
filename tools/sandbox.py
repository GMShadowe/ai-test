import os
from pathlib import Path

WORKSPACE = Path(os.getenv("WORKSPACE", "/workspace")).resolve()


def resolve_path(path: str) -> Path:
    requested = Path(path)
    if not requested.is_absolute():
        requested = WORKSPACE / requested

    # Resolve existing symlinks to prevent simple workspace traversal.
    resolved = requested.resolve(strict=False)

    if resolved != WORKSPACE and WORKSPACE not in resolved.parents:
        raise ValueError("Path is outside the permitted workspace")

    return resolved
