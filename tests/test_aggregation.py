from qolab.evaluation.aggregation import compute_final_score


def test_final_score_without_judge():
    sample = {"scores": {"heuristics": {"total_heuristics": 24}, "judge": None}}
    assert compute_final_score(sample, used_judge=False) == 24


def test_final_score_with_judge():
    sample = {
        "scores": {
            "heuristics": {"total_heuristics": 20},
            "judge": {"total_judge": 25},
        }
    }
    final = compute_final_score(sample, used_judge=True)
    assert final == 0.6 * 25 + 0.4 * 20

