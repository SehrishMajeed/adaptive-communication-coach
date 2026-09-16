from dataclasses import dataclass
from typing import Literal

from .evaluation import Skill

DRILL_VERSION = "technical-explanation-drills-v1"
DRILLS: dict[Skill, str] = {
    "clarity": "Say the main idea in one plain sentence before adding details.",
    "structure": "Use this order: problem, what you built, result, why it matters.",
    "conciseness": "Cut one side detail and keep only what helps the listener decide.",
    "audience_awareness": "Replace one technical term with the listener-facing benefit.",
}

CoachingGateReason = Literal[
    "eligible",
    "evaluation_not_completed",
    "input_not_usable",
    "evidence_not_quote_verified",
    "feedback_not_actionable",
    "missing_focus",
]


@dataclass(frozen=True)
class CoachingWriteEligibility:
    allowed: bool
    reason: CoachingGateReason
    target_skill: Skill | None


def target_skill_for_evaluation(evaluation) -> Skill | None:
    focus = getattr(evaluation, "recommended_focus", None)
    if isinstance(focus, list):
        return focus[0] if focus else None
    return focus


def coaching_write_eligibility(evaluation) -> CoachingWriteEligibility:
    target_skill = target_skill_for_evaluation(evaluation)
    if evaluation.evaluator_status != "completed":
        return CoachingWriteEligibility(False, "evaluation_not_completed", None)
    if evaluation.input_quality != "usable":
        return CoachingWriteEligibility(False, "input_not_usable", None)
    if evaluation.evidence_status != "quote_verified":
        return CoachingWriteEligibility(False, "evidence_not_quote_verified", None)
    if evaluation.feedback_status != "actionable":
        return CoachingWriteEligibility(False, "feedback_not_actionable", None)
    if target_skill is None:
        return CoachingWriteEligibility(False, "missing_focus", None)
    return CoachingWriteEligibility(True, "eligible", target_skill)


def comparison_verdict(delta: float) -> str:
    if delta >= 1:
        return "improved"
    if delta <= -1:
        return "regressed"
    return "no_clear_change"
