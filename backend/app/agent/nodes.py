from .state import CoachingState
from ..domain.metrics import calculate_deterministic_metrics
from ..services.llm_provider import evaluate_communication


def evaluate_communication_node(state: CoachingState) -> dict:
    evaluation = evaluate_communication(state["audio_bytes"], state["mime_type"], state["scenario"])
    return {"rubric_evaluation": evaluation, "transcript": evaluation.transcript}


def compute_deterministic_metrics(state: CoachingState) -> dict:
    return {"deterministic_metrics": calculate_deterministic_metrics(state["transcript"], state["duration_seconds"])}
