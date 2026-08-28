from typing import TypedDict, Optional, Dict, Any
from ..domain.evaluation import CommunicationEvaluation

class CoachingState(TypedDict):
    session_id: str
    user_id: str
    attempt_number: int
    scenario: str
    
    audio_bytes: Optional[bytes]
    mime_type: Optional[str]
    
    transcript: Optional[str]
    duration_seconds: float
    
    deterministic_metrics: Optional[Dict[str, Any]]
    
    rubric_evaluation: Optional[CommunicationEvaluation]
    focus_area: Optional[str]
    next_exercise: Optional[str]
    
    previous_attempt_metrics: Optional[Dict[str, Any]]
    comparison_delta: Optional[str]
