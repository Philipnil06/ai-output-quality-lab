from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from .pipeline import run_experiment, render_summary_markdown


console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qolab", description="AI Output Quality Lab CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run an experiment")
    run_parser.add_argument("--case", required=True, help="Path to case JSON config")
    run_parser.add_argument("--suite", required=True, help="Path to prompt suite JSON")
    run_parser.add_argument(
        "--runs-dir",
        default="runs",
        help="Directory where run folders are stored",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use mocked outputs (no API key required)",
    )
    run_parser.add_argument(
        "--use-judge",
        action="store_true",
        help="Enable LLM-as-judge scoring (requires OPENAI_API_KEY)",
    )
    run_parser.add_argument(
        "--model",
        default=None,
        help="Override generator model (default gpt-4.1-mini)",
    )
    run_parser.add_argument(
        "--judge-model",
        default=None,
        help="Override judge model (default gpt-4.1-mini)",
    )
    run_parser.add_argument(
        "--rubric",
        default=None,
        help="Path to judge rubric JSON",
    )

    report_parser = subparsers.add_parser("report", help="Regenerate summary from results.json")
    report_parser.add_argument(
        "--run",
        required=True,
        help="Path to results.json",
    )

    return parser


def cmd_run(args: argparse.Namespace) -> None:
    console.print("[bold]Running experiment...[/bold]")
    results_path = run_experiment(
        case_path=args.case,
        suite_path=args.suite,
        runs_dir=args.runs_dir,
        dry_run=args.dry_run,
        use_judge=args.use_judge,
        model=args.model,
        judge_model=args.judge_model,
        rubric_path=args.rubric,
    )
    console.print(f"[green]Saved results:[/green] {results_path}")
    summary_path = render_summary_markdown(results_path)
    console.print(f"[green]Saved summary:[/green] {summary_path}")


def cmd_report(args: argparse.Namespace) -> None:
    console.print("[bold]Generating report...[/bold]")
    results_path = Path(args.run)
    summary_path = render_summary_markdown(results_path)
    console.print(f"[green]Saved summary:[/green] {summary_path}")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        cmd_run(args)
    elif args.command == "report":
        cmd_report(args)
    else:
        parser.error(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()

