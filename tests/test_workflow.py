import pytest
from backend.app.agent.state import CoachingState
from backend.app.agent.nodes import compute_deterministic_metrics, compare_attempts_node

def test_deterministic_metrics():
    state = CoachingState(
        session_id="test",
        user_id="test",
        attempt_number=1,
        scenario="Test",
        transcript="Um, hello. I am like, happy.", 
        duration_seconds=5.0,
        deterministic_metrics=None,
        rubric_evaluation=None,
        focus_area=None,
        next_exercise=None,
        previous_attempt_metrics=None,
        comparison_delta=None
    )
    result = compute_deterministic_metrics(state)
    
    assert result["deterministic_metrics"]["word_count"] == 6
    assert result["deterministic_metrics"]["total_fillers"] == 2
    assert result["deterministic_metrics"]["wpm"] == 72
    
def test_compare_attempts_node():
    state = CoachingState(
        session_id="test",
        user_id="test",
        attempt_number=2,
        scenario="Test",
        transcript="Hello. I am happy.", 
        duration_seconds=5.0,
        deterministic_metrics={"wpm": 48, "total_fillers": 0},
        rubric_evaluation=None,
        focus_area=None,
        next_exercise=None,
        previous_attempt_metrics={"wpm": 72, "total_fillers": 2},
        comparison_delta=None
    )
    result = compare_attempts_node(state)
    assert "reduced your filler words" in result["comparison_delta"]
