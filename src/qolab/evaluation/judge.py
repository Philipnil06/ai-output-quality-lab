from __future__ import annotations

import json
from typing import Any, Dict

from openai import OpenAI

from .rubric import JudgeRubric


JUDGE_SYSTEM_PROMPT = (
    "You are an impartial writing quality judge for LinkedIn posts. "
    "Respond ONLY with strict JSON, no commentary."
)


def build_judge_prompt(
    rubric: JudgeRubric,
    case_description: str,
    constraints: Dict[str, Any],
    keywords: list[str],
    output_text: str,
) -> str:
    checklist_lines = [
        "- Word range: "
        f"{constraints.get('min_words')}–{constraints.get('max_words')} words.",
        f"- Max emojis: {constraints.get('max_emojis', 0)}.",
        f"- Max exclamation marks: {constraints.get('max_exclamation_marks', 1)}.",
        "- Banned phrases must not appear: "
        f"{constraints.get('banned_phrases', [])}.",
        f"- Prefer first-person voice: {constraints.get('prefer_first_person', False)}.",
        f"- Avoid salesy ad copy: {constraints.get('avoid_salesy_ad_copy', False)}.",
        f"- Prefer ending with a light audience question: {constraints.get('prefer_question_ending', False)}.",
        f"- No fabricated metrics (percentages, timeframes) if no_fabricated_metrics is true: {constraints.get('no_fabricated_metrics', False)}.",
        f"- Keywords are nice-to-have only: {keywords}.",
    ]
    rubric_text = "\n".join(rubric.instructions)
    checklist_text = "\n".join(checklist_lines)
    return (
        f"{rubric_text}\n\n"
        "CASE CONTEXT:\n"
        f"{case_description}\n\n"
        "CONSTRAINT CHECKLIST (verify explicitly):\n"
        f"{checklist_text}\n\n"
        "CANDIDATE OUTPUT:\n"
        f"{output_text}\n\n"
        "When scoring, apply these HARD rules:\n"
        "- If feels_like_ad_copy is true, then tone_voice must be <= 2 and usefulness must be <= 2.\n"
        "- If fabricated_metrics_present is true and no_fabricated_metrics is true, then instruction_following must be <= 2.\n"
        "- Scores of 5 must be rare and require excellence on that category.\n\n"
        "Return STRICT JSON with EXACTLY these top-level keys: checks, scores, rationales, total_judge.\n"
        "No markdown, no commentary, no extra keys.\n\n"
        "The JSON schema is:\n"
        "{\n"
        "  \"checks\": {\n"
        "    \"word_range_ok\": true/false,\n"
        "    \"emoji_limit_ok\": true/false,\n"
        "    \"exclamation_limit_ok\": true/false,\n"
        "    \"banned_phrases_present\": true/false,\n"
        "    \"first_person_present\": true/false,\n"
        "    \"feels_like_ad_copy\": true/false,\n"
        "    \"fabricated_metrics_present\": true/false,\n"
        "    \"ends_with_audience_question\": true/false\n"
        "  },\n"
        "  \"scores\": {\n"
        "    \"instruction_following\": 0-5,\n"
        "    \"clarity_structure\": 0-5,\n"
        "    \"tone_voice\": 0-5,\n"
        "    \"usefulness\": 0-5,\n"
        "    \"conciseness\": 0-5,\n"
        "    \"non_repetition\": 0-5\n"
        "  },\n"
        "  \"rationales\": {\n"
        "    \"instruction_following\": \"one short sentence\",\n"
        "    \"clarity_structure\": \"one short sentence\",\n"
        "    \"tone_voice\": \"one short sentence\",\n"
        "    \"usefulness\": \"one short sentence\",\n"
        "    \"conciseness\": \"one short sentence\",\n"
        "    \"non_repetition\": \"one short sentence\"\n"
        "  },\n"
        "  \"total_judge\": 0-30\n"
        "}"
    )


def call_judge(
    client: OpenAI,
    model: str,
    rubric: JudgeRubric,
    case_description: str,
    constraints: Dict[str, Any],
    keywords: list[str],
    output_text: str,
) -> Dict[str, Any]:
    user_prompt = build_judge_prompt(rubric, case_description, constraints, keywords, output_text)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=400,
    )
    raw = resp.choices[0].message.content or ""
    try:
        parsed = json.loads(raw)
        scores = parsed.get("scores", {}) or {}
        total = parsed.get("total_judge")
        if total is None and scores:
            total = sum(float(v) for v in scores.values())
        checks = parsed.get("checks", {}) or {}
        rationales = parsed.get("rationales", {}) or {}
        return {
            "checks": checks,
            "scores": scores,
            "rationales": rationales,
            "total_judge": total,
            "judge_error": None,
            "raw_judge": raw,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "checks": None,
            "scores": None,
            "rationales": None,
            "total_judge": None,
            "judge_error": f"Failed to parse judge JSON: {exc}",
            "raw_judge": raw,
        }
