from __future__ import annotations

import datetime as dt
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

from .evaluation.aggregation import compute_final_score
from .evaluation.heuristics import evaluate_heuristics
from .evaluation.judge import call_judge
from .evaluation.rubric import load_rubric
from .generation.client import LLMClient, OpenAIClientConfig, DEFAULT_MODEL, DEFAULT_JUDGE_MODEL
from .generation.dryrun import generate_dryrun
from .generation.prompts import CaseConfig, PromptVariant, render_user_prompt
from .logging.run_store import save_run
from .logging.schemas import RunMetadata, RunResults, SampleRecord, SampleScores
from .utils.io import load_json, load_text


TEMPERATURES = [0.2, 0.7, 1.0]


def load_case(path: str) -> Dict[str, Any]:
    return load_json(path)


def load_suite(path: str) -> Dict[str, Any]:
    return load_json(path)


def build_case_config(case_data: Dict[str, Any]) -> CaseConfig:
    return CaseConfig(
        name=case_data["name"],
        task=case_data["task"],
        audience=case_data["audience"],
        tone=case_data["tone"],
        constraints=case_data["constraints"],
        keywords_file=case_data["keywords_file"],
    )


def build_variants(suite_data: Dict[str, Any]) -> List[PromptVariant]:
    variants = []
    for v in suite_data["variants"]:
        variants.append(
            PromptVariant(
                name=v["name"],
                system_prompt=v["system_prompt"],
                user_prompt_template=v["user_prompt_template"],
            )
        )
    return variants


def run_experiment(
    case_path: str,
    suite_path: str,
    runs_dir: str,
    dry_run: bool,
    use_judge: bool,
    model: str | None = None,
    judge_model: str | None = None,
    rubric_path: str | None = None,
) -> Path:
    load_dotenv()

    case_data = load_case(case_path)
    suite_data = load_suite(suite_path)

    case = build_case_config(case_data)
    variants = build_variants(suite_data)

    keywords = []
    if case.keywords_file:
        keywords_text = load_text(case.keywords_file)
        keywords = [k.strip() for k in keywords_text.splitlines() if k.strip()]

    cta_phrases = [
        "book a demo",
        "book your demo",
        "try it",
        "dm me",
        "contact us",
        "start a trial",
    ]

    generator_model = model or DEFAULT_MODEL
    judge_model = judge_model or DEFAULT_JUDGE_MODEL

    api_key = os.getenv("OPENAI_API_KEY")

    llm_client = None
    if not dry_run:
        llm_client = LLMClient(OpenAIClientConfig(api_key=api_key, model=generator_model))

    judge_client = None
    rubric = None
    if use_judge:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when using --use-judge.")
        from openai import OpenAI as JudgeClient

        judge_client = JudgeClient(api_key=api_key)
        rubric_path = rubric_path or "configs/rubrics/judge_rubric_v1.json"
        rubric = load_rubric(rubric_path)

    slug = case.name.lower().replace(" ", "_")
    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    run_id = f"{timestamp}_{slug}"

    metadata = RunMetadata(
        run_id=run_id,
        created_at=dt.datetime.utcnow().isoformat(),
        case=case_data,
        suite=suite_data,
        generator_model=generator_model,
        judge_model=judge_model if use_judge else None,
        used_judge=use_judge,
        temperatures=TEMPERATURES,
        variants=[v.name for v in variants],
    )

    results = RunResults(metadata=metadata)

    for variant in variants:
        for temp in TEMPERATURES:
            user_prompt = render_user_prompt(variant.user_prompt_template, case)
            full_prompt = f"SYSTEM:\n{variant.system_prompt}\n\nUSER:\n{user_prompt}"
            if dry_run:
                output = generate_dryrun(case.name, variant.name, temp)
            else:
                assert llm_client is not None
                output = llm_client.generate(variant.system_prompt, user_prompt, temp)

            heuristics_scores = evaluate_heuristics(
                output,
                case.constraints,
                keywords,
                cta_phrases,
            )

            judge_scores: Dict[str, Any] | None = None
            if use_judge and judge_client and rubric:
                case_desc = (
                    f"Task: {case.task}\n"
                    f"Audience: {case.audience}\n"
                    f"Tone: {case.tone}\n"
                    f"Constraints: {case.constraints}"
                )
                judge_result = call_judge(
                    judge_client,
                    judge_model,
                    rubric,
                    case_desc,
                    case.constraints,
                    keywords,
                    output,
                )
                judge_scores = judge_result

            scores = {
                "heuristics": heuristics_scores,
                "judge": judge_scores,
            }
            sample_dict = {
                "variant_name": variant.name,
                "temperature": float(temp),
                "full_prompt": full_prompt,
                "output_text": output,
                "scores": scores,
            }
            sample_record = SampleRecord(
                **{
                    **sample_dict,
                    "scores": SampleScores(
                        heuristics=heuristics_scores,
                        judge=judge_scores,
                        final_score=0.0,  # placeholder
                    ),
                }
            )
            results.samples.append(sample_record)

    for s in results.samples:
        s.scores.final_score = compute_final_score(
            {"scores": {"heuristics": s.scores.heuristics, "judge": s.scores.judge}},
            used_judge=use_judge,
        )

    results_path = save_run(results, runs_dir)
    return results_path


def render_summary_markdown(results_path: str | Path, output_path: str | Path | None = None) -> Path:
    from .logging.run_store import load_run

    run = load_run(results_path)
    samples = list(run.samples)
    samples.sort(key=lambda s: s.scores.final_score, reverse=True)

    lines: List[str] = []
    md_append = lines.append

    md_append(f"# Run Summary: {run.metadata.run_id}")
    md_append("")
    md_append("## Metadata")
    md_append(f"- Case: **{run.metadata.case.get('name', '')}**")
    md_append(f"- Generator model: `{run.metadata.generator_model}`")
    if run.metadata.used_judge:
        md_append(f"- Judge model: `{run.metadata.judge_model}`")
    md_append(f"- Temperatures: {', '.join(str(t) for t in run.metadata.temperatures)}")
    md_append(f"- Variants: {', '.join(run.metadata.variants)}")
    md_append(f"- Judge enabled: {run.metadata.used_judge}")
    md_append("")

    md_append("## Scores Overview")
    md_append("")
    header = "| Variant | Temp | Heuristics | Judge | Final |"
    md_append(header)
    md_append("|---|---|---|---|---|")
    for s in samples:
        heur_total = s.scores.heuristics.get("total_heuristics", 0)
        judge_total = None
        if s.scores.judge:
            judge_total = s.scores.judge.get("total_judge")
        md_append(
            f"| {s.variant_name} | {s.temperature:.1f} | {heur_total:.1f} | "
            f"{'' if judge_total is None else f'{judge_total:.1f}'} | {s.scores.final_score:.1f} |"
        )

    md_append("")
    md_append("## Top 3 Outputs")
    md_append("")

    for idx, s in enumerate(samples[:3], start=1):
        md_append(f"### #{idx}: {s.variant_name} @ temp={s.temperature}")
        md_append("")
        md_append(f"- Final score: {s.scores.final_score:.1f}")
        md_append(
            f"- Heuristics total: {s.scores.heuristics.get('total_heuristics', 0):.1f}"
        )
        if s.scores.judge:
            jt = s.scores.judge.get("total_judge")
            md_append(f"- Judge total: {'' if jt is None else f'{jt:.1f}'}")
            checks = s.scores.judge.get("checks") or {}
            failed = [
                name
                for name, value in checks.items()
                if isinstance(value, bool) and value is True and name.endswith("_present")
                or (isinstance(value, bool) and value is False and name.endswith("_ok"))
            ]
            if failed:
                md_append(f"- Failed checks: {', '.join(sorted(failed))}")
        md_append("")
        md_append("#### Output")
        md_append("")
        md_append(s.output_text.strip())
        md_append("")
        md_append("#### Heuristics breakdown")
        md_append("")
        for key, value in s.scores.heuristics.items():
            if key == "total_heuristics":
                continue
            md_append(f"- **{key}**: {value}")
        md_append("")

    results_path = Path(results_path)
    summary_path = (
        Path(output_path)
        if output_path is not None
        else results_path.with_name("summary.md")
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return summary_path
