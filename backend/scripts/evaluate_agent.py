from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.domain.evaluation import CommunicationEvaluation
from backend.app.services.llm_provider import GEMINI_MODEL, evaluate_communication


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CORPUS_DIR = PROJECT_ROOT / "tests" / "corpus"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "evaluation_report.md"


@dataclass(frozen=True)
class EvaluationCaseResult:
    case_id: str
    passed: bool
    latency_seconds: float
    errors: list[str]


@dataclass(frozen=True)
class EvaluationRunResult:
    status: str
    total: int
    passed: int
    failed: int
    average_latency_seconds: float
    report_path: Path


def _write_report(
    *,
    report_path: Path,
    status: str,
    model: str,
    total: int,
    passed: int,
    failed: int,
    average_latency_seconds: float,
    details: list[EvaluationCaseResult],
    note: str | None = None,
) -> None:
    accuracy = (passed / total * 100) if total else 0.0
    lines = [
        "# Agentic Evaluation Pipeline Report",
        "",
        f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Status**: {status}",
        f"**Model**: {model}",
        "",
        "## Summary",
        f"- **Total Tests**: {total}",
        f"- **Passed**: {passed}",
        f"- **Failed**: {failed}",
        f"- **Accuracy**: {accuracy:.1f}%",
        f"- **Average Latency**: {average_latency_seconds:.2f}s",
        "",
    ]
    if note:
        lines.extend(["## Note", note, ""])
    if details:
        lines.append("## Details")
        for result in details:
            marker = "PASS" if result.passed else "FAIL"
            lines.extend([
                f"### {result.case_id} - {marker}",
                f"- Latency: {result.latency_seconds:.2f}s",
            ])
            if result.errors:
                lines.append(f"- Errors: {', '.join(result.errors)}")
            lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def _validate_case(
    test_case: dict,
    evaluation: CommunicationEvaluation,
) -> list[str]:
    expected = test_case.get("expected", {})
    errors: list[str] = []
    expected_status = expected.get("evaluator_status")
    if expected_status and evaluation.evaluator_status != expected_status:
        errors.append(f"Status mismatch: expected {expected_status}, got {evaluation.evaluator_status}")
    if evaluation.evaluator_status == "completed":
        if not evaluation.evidence:
            errors.append("No evidence provided in completed evaluation.")
        expected_focus = expected.get("recommended_focus")
        if expected_focus and (not evaluation.recommended_focus or evaluation.recommended_focus[0] != expected_focus):
            errors.append(f"Focus mismatch: expected {expected_focus}, got {evaluation.recommended_focus}")
    return errors


def run_live_evaluation(
    *,
    corpus_dir: Path = DEFAULT_CORPUS_DIR,
    report_path: Path = DEFAULT_REPORT_PATH,
    evaluator: Callable[[bytes, str, str], CommunicationEvaluation] = evaluate_communication,
    require_api_key: bool = True,
) -> EvaluationRunResult:
    if require_api_key and not os.getenv("GEMINI_API_KEY"):
        note = "Skipped because GEMINI_API_KEY is not configured. No live provider call was attempted."
        _write_report(
            report_path=report_path,
            status="skipped",
            model=GEMINI_MODEL,
            total=0,
            passed=0,
            failed=0,
            average_latency_seconds=0.0,
            details=[],
            note=note,
        )
        print(note)
        return EvaluationRunResult("skipped", 0, 0, 0, 0.0, report_path)

    if not corpus_dir.exists():
        raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")

    test_files = sorted(corpus_dir.glob("*.json"))
    if not test_files:
        raise FileNotFoundError(f"No .json test cases found in {corpus_dir}")

    print("Starting live Agentic Evaluation Pipeline...")
    results: list[EvaluationCaseResult] = []
    total_latency = 0.0

    for test_file in test_files:
        test_case = json.loads(test_file.read_text(encoding="utf-8"))
        case_id = test_case.get("id", test_file.stem)
        scenario = test_case.get("scenario", "Explain a technical project to a recruiter in 60 seconds.")
        audio_path_name = test_case.get("audio_path")
        errors: list[str] = []
        started = time.monotonic()

        if not audio_path_name:
            errors.append("No audio_path provided in test case.")
        else:
            audio_path = corpus_dir / audio_path_name
            if not audio_path.exists():
                errors.append(f"Audio file not found: {audio_path}")

        if errors:
            latency = time.monotonic() - started
            results.append(EvaluationCaseResult(case_id, False, latency, errors))
            continue

        audio_path = corpus_dir / audio_path_name
        mime_type = "audio/wav" if audio_path.suffix.lower() == ".wav" else "audio/mpeg"
        try:
            evaluation = evaluator(audio_path.read_bytes(), mime_type, scenario)
            errors = _validate_case(test_case, evaluation)
        except Exception as exc:
            errors = [f"{type(exc).__name__}: {exc}"]

        latency = time.monotonic() - started
        total_latency += latency
        passed = not errors
        results.append(EvaluationCaseResult(case_id, passed, latency, errors))
        print(f"{case_id}: {'PASS' if passed else 'FAIL'} ({latency:.2f}s)")

    total = len(results)
    passed_count = sum(1 for result in results if result.passed)
    failed_count = total - passed_count
    average_latency = total_latency / total if total else 0.0
    status = "passed" if failed_count == 0 else "failed"
    _write_report(
        report_path=report_path,
        status=status,
        model=GEMINI_MODEL,
        total=total,
        passed=passed_count,
        failed=failed_count,
        average_latency_seconds=average_latency,
        details=results,
    )
    print(f"Detailed report written to {report_path}")
    return EvaluationRunResult(status, total, passed_count, failed_count, average_latency, report_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the live Gemini evaluation corpus.")
    parser.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS_DIR)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    result = run_live_evaluation(corpus_dir=args.corpus_dir, report_path=args.report_path)
    return 1 if result.status == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
