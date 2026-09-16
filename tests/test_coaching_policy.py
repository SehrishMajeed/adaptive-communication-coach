from types import SimpleNamespace

from backend.app.domain.coaching import (
    DRILLS,
    coaching_write_eligibility,
    comparison_verdict,
    decide_attempt_workflow,
    target_skill_for_evaluation,
)


def evaluation(**overrides):
    fields = {
        "evaluator_status": "completed",
        "input_quality": "usable",
        "evidence_status": "quote_verified",
        "feedback_status": "actionable",
        "recommended_focus": ["clarity"],
    }
    fields.update(overrides)
    return SimpleNamespace(**fields)


def test_coaching_write_policy_allows_only_usable_quote_verified_actionable_feedback():
    result = coaching_write_eligibility(evaluation())
    assert result.allowed is True
    assert result.reason == "eligible"
    assert result.target_skill == "clarity"
    assert DRILLS[result.target_skill] == "Say the main idea in one plain sentence before adding details."


def test_coaching_write_policy_blocks_abstained_or_low_quality_feedback():
    cases = [
        ({"evaluator_status": "abstained"}, "evaluation_not_completed"),
        ({"input_quality": "limited"}, "input_not_usable"),
        ({"evidence_status": "insufficient_evidence"}, "evidence_not_quote_verified"),
        ({"feedback_status": "needs_retry"}, "feedback_not_actionable"),
        ({"recommended_focus": []}, "missing_focus"),
    ]
    for update, reason in cases:
        result = coaching_write_eligibility(evaluation(**update))
        assert result.allowed is False
        assert result.reason == reason
        assert result.target_skill is None


def test_target_skill_policy_supports_pydantic_and_persisted_evaluations():
    assert target_skill_for_evaluation(evaluation(recommended_focus=["structure"])) == "structure"
    assert target_skill_for_evaluation(evaluation(recommended_focus="conciseness")) == "conciseness"
    assert target_skill_for_evaluation(evaluation(recommended_focus=[])) is None


def test_comparison_verdict_thresholds_are_domain_policy():
    assert comparison_verdict(1) == "improved"
    assert comparison_verdict(0.9) == "no_clear_change"
    assert comparison_verdict(-0.9) == "no_clear_change"
    assert comparison_verdict(-1) == "regressed"


def test_workflow_routes_baseline_abstained_and_retry_comparable_paths():
    eligible = coaching_write_eligibility(evaluation())
    abstained = coaching_write_eligibility(evaluation(evaluator_status="abstained"))

    baseline = decide_attempt_workflow(1, eligible, has_prior_intervention=False)
    abstained_route = decide_attempt_workflow(1, abstained, has_prior_intervention=False)
    retry = decide_attempt_workflow(2, eligible, has_prior_intervention=True, baseline_eligibility=eligible)

    assert baseline.route == "baseline"
    assert baseline.should_create_intervention is True
    assert baseline.should_create_comparison is False
    assert abstained_route.route == "abstained"
    assert abstained_route.should_create_intervention is False
    assert abstained_route.should_create_comparison is False
    assert retry.route == "retry_comparable"
    assert retry.should_create_intervention is False
    assert retry.should_create_comparison is True


def test_workflow_routes_blocked_retry_cases_without_coaching_writes():
    eligible = coaching_write_eligibility(evaluation())
    limited = coaching_write_eligibility(evaluation(input_quality="limited"))

    no_baseline = decide_attempt_workflow(2, eligible, has_prior_intervention=False)
    limited_retry = decide_attempt_workflow(2, limited, has_prior_intervention=True)
    blocked_baseline = decide_attempt_workflow(2, eligible, has_prior_intervention=True, baseline_eligibility=limited)

    assert no_baseline.route == "retry_without_baseline"
    assert limited_retry.route == "retry_blocked"
    assert limited_retry.reason == "retry_not_eligible"
    assert blocked_baseline.route == "retry_blocked"
    assert blocked_baseline.reason == "baseline_not_eligible"
    assert no_baseline.should_create_comparison is False
    assert limited_retry.should_create_comparison is False
    assert blocked_baseline.should_create_comparison is False
