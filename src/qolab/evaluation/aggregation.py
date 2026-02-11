from __future__ import annotations

from typing import Dict, Any


def compute_final_score(sample: Dict[str, Any], used_judge: bool) -> float:
    heuristics_total = float(sample["scores"]["heuristics"]["total_heuristics"])
    judge_data = sample["scores"].get("judge")
    judge_total = judge_data.get("total_judge") if isinstance(judge_data, dict) else None
    if used_judge and judge_total is not None:
        return 0.6 * float(judge_total) + 0.4 * heuristics_total
    return heuristics_total
