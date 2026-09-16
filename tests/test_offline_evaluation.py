from backend.app.evaluation.offline_runner import run_offline_evals


def test_offline_evaluation_fixtures_all_pass():
    results = run_offline_evals()
    assert len(results) == 3
    failures = {result.fixture_id: result.errors for result in results if not result.passed}
    assert failures == {}


def test_offline_evaluation_suite_covers_required_risks():
    results = {result.fixture_id: result for result in run_offline_evals()}
    assert "technical_project_clear" in results
    assert "too_little_speech_abstain" in results
    assert "spoken_prompt_injection_resisted" in results
    assert "prompt_injection_not_obeyed" in results["spoken_prompt_injection_resisted"].checks
    assert "spoken_instructions_untrusted" in results["spoken_prompt_injection_resisted"].checks
