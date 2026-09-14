from typing import TypedDict
from ..domain.evaluation import CommunicationEvaluation


class CoachingState(TypedDict, total=False):
    scenario: str
    audio_bytes: bytes
    mime_type: str
    duration_seconds: float
    transcript: str
    rubric_evaluation: CommunicationEvaluation
    deterministic_metrics: dict
