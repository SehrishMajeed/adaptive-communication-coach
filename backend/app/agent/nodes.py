from .state import CoachingState
from ..domain.metrics import calculate_deterministic_metrics
from ..services.llm_provider import evaluate_communication
from ..domain.comparison import generate_comparison_feedback

def compute_deterministic_metrics(state: CoachingState) -> CoachingState:
    metrics = calculate_deterministic_metrics(state["transcript"], state["duration_seconds"])
    state["deterministic_metrics"] = metrics
    return state

def evaluate_communication_node(state: CoachingState) -> CoachingState:
    if not state.get("transcript"):
        return state
        
    evaluation = evaluate_communication(state["transcript"], state["scenario"])
    state["rubric_evaluation"] = evaluation
    
    if evaluation.recommended_focus:
        state["focus_area"] = evaluation.recommended_focus[0]
        state["next_exercise"] = f"For your next attempt, focus on: {state['focus_area']}."
    
    return state

def compare_attempts_node(state: CoachingState) -> CoachingState:
    feedback = generate_comparison_feedback(
        state.get("deterministic_metrics", {}),
        state.get("previous_attempt_metrics")
    )
    state["comparison_delta"] = feedback
    return state
