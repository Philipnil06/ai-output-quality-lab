from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SampleScores(BaseModel):
    heuristics: Dict[str, Any]
    judge: Optional[Dict[str, Any]] = None
    final_score: float


class SampleRecord(BaseModel):
    variant_name: str
    temperature: float
    full_prompt: str
    output_text: str
    scores: SampleScores


class RunMetadata(BaseModel):
    run_id: str
    created_at: str
    case: Dict[str, Any]
    suite: Dict[str, Any]
    generator_model: str
    judge_model: Optional[str] = None
    used_judge: bool
    temperatures: List[float]
    variants: List[str]


class RunResults(BaseModel):
    metadata: RunMetadata
    samples: List[SampleRecord] = Field(default_factory=list)
