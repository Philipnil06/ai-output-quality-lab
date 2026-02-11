from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .schemas import RunResults
from ..utils.io import dump_json, load_json


def _to_dict(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj


def save_run(results: RunResults, base_dir: str | Path) -> Path:
    base = Path(base_dir)
    run_dir = base / results.metadata.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "results.json"
    dump_json(path, _to_dict(results))
    return path


def load_run(path: str | Path) -> RunResults:
    data = load_json(path)
    return RunResults(**data)

