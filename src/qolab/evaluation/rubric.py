from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

from ..utils.io import load_json


@dataclass
class JudgeRubric:
    instructions: List[str]
    categories: Dict[str, str]


def load_rubric(path: str) -> JudgeRubric:
    data: Dict[str, Any] = load_json(path)
    return JudgeRubric(
        instructions=data["instructions"],
        categories=data["categories"],
    )
