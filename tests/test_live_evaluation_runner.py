import json

from backend.app.domain.evaluation import CommunicationEvaluation
from backend.scripts.evaluate_agent import run_live_evaluation


def completed_evaluation() -> CommunicationEvaluation:
    return CommunicationEvaluation(
        evaluator_status="completed",
        abstention_reason=None,
        transcript="I built an app that helps students practice interviews.",
        clarity=7,
        structure=6,
        conciseness=8,
        audience_awareness=7,
        strengths=["The explanation names the user and the core action."],
        weaknesses=["The opening could explain why this matters."],
        recommended_focus=["clarity"],
        evidence=[{
            "skill": "clarity",
            "quote": "I built an app that helps students practice interviews.",
            "note": "The opening names the product clearly.",
        }],
        input_quality="usable",
        evidence_status="quote_verified",
        feedback_status="actionable",
    )


def test_live_evaluation_skips_cleanly_without_gemini_key(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    report_path = tmp_path / "evaluation_report.md"

    result = run_live_evaluation(corpus_dir=tmp_path, report_path=report_path)

    assert result.status == "skipped"
    assert result.failed == 0
    assert "Skipped because GEMINI_API_KEY is not configured" in report_path.read_text(encoding="utf-8")


def test_live_evaluation_uses_injected_evaluator_and_writes_report(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    (tmp_path / "sample.wav").write_bytes(b"RIFFtest")
    (tmp_path / "clear_pitch.json").write_text(json.dumps({
        "id": "clear_pitch",
        "scenario": "Explain a technical project to a recruiter.",
        "audio_path": "sample.wav",
        "expected": {
            "evaluator_status": "completed",
            "recommended_focus": "clarity",
        },
    }), encoding="utf-8")
    report_path = tmp_path / "evaluation_report.md"

    result = run_live_evaluation(
        corpus_dir=tmp_path,
        report_path=report_path,
        evaluator=lambda _audio, _mime_type, _scenario: completed_evaluation(),
    )

    report = report_path.read_text(encoding="utf-8")
    assert result.status == "passed"
    assert result.total == 1
    assert result.passed == 1
    assert "clear_pitch - PASS" in report
