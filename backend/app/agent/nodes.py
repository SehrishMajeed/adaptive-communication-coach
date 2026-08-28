from .state import CoachingState
from ..domain.metrics import calculate_deterministic_metrics
from ..services.llm_provider import evaluate_communication
from ..domain.comparison import generate_comparison_feedback

def compute_deterministic_metrics(state: CoachingState) -> CoachingState:
    transcript = state.get("transcript", "")
    metrics = calculate_deterministic_metrics(transcript, state["duration_seconds"])
    state["deterministic_metrics"] = metrics
    return state

def evaluate_communication_node(state: CoachingState) -> CoachingState:
    if not state.get("audio_bytes"):
        return state
        
    evaluation = evaluate_communication(state["audio_bytes"], state.get("mime_type", "audio/webm"), state["scenario"])
    state["rubric_evaluation"] = evaluation
    state["transcript"] = evaluation.transcript
    
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
