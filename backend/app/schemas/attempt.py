from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from ..domain.evaluation import CommunicationEvaluation

ATTEMPT_RESPONSE_SCHEMA_VERSION = "attempt-response-v2"
RUBRIC_VERSION = "technical-explanation-v1"
METRIC_VERSION = "speech-metrics-v1"


class AttemptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Monotonic client capture duration is a cross-check, not the WPM denominator.
    duration_seconds: float = Field(ge=1, le=65, allow_inf_nan=False)


class FillerCount(BaseModel):
    model_config = ConfigDict(extra="forbid")
    word: str = Field(min_length=1)
    count: int = Field(ge=1)


class Measurements(BaseModel):
    model_config = ConfigDict(extra="forbid")
    duration_seconds: float = Field(ge=1, le=65, allow_inf_nan=False)
    duration_source: Literal["pcm_samples"] = "pcm_samples"
    word_count: int = Field(ge=0)
    wpm: int = Field(ge=0)
    total_fillers: int = Field(ge=0)
    filler_words_list: list[FillerCount]


def measurements_from_attempt(attempt) -> Measurements:
    return Measurements(
        duration_seconds=attempt.duration_seconds,
        duration_source=attempt.duration_source,
        word_count=attempt.word_count,
        wpm=attempt.wpm,
        total_fillers=attempt.filler_words_count,
        filler_words_list=attempt.filler_words_list or [],
    )


def measurements_from_practice_measurement(measurement, media_duration_seconds: float) -> Measurements:
    return Measurements(
        duration_seconds=media_duration_seconds,
        duration_source=measurement.duration_source,
        word_count=measurement.word_count,
        wpm=measurement.wpm,
        total_fillers=measurement.total_fillers,
        filler_words_list=measurement.filler_words_json or [],
    )


class EvaluationProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt_version: str
    model_id: str
    schema_version: str
    rubric_version: str
    metric_version: str


class AttemptResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attempt_id: int = Field(ge=1)
    measurements: Measurements
    evaluation: CommunicationEvaluation
    provenance: EvaluationProvenance


class InterventionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intervention_id: int = Field(ge=1)
    target_skill: Literal["clarity", "structure", "conciseness", "audience_awareness"]
    drill_version: str
    drill_text: str
    status: Literal["assigned", "completed", "abandoned"]


class AttemptComparisonResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    comparison_id: int = Field(ge=1)
    baseline_attempt_id: int = Field(ge=1)
    retry_attempt_id: int = Field(ge=1)
    intervention_id: int = Field(ge=1)
    target_skill: Literal["clarity", "structure", "conciseness", "audience_awareness"]
    comparability_status: Literal["comparable", "insufficient_evidence", "context_mismatch", "rubric_mismatch"]
    verdict: Literal["improved", "no_clear_change", "regressed", "insufficient_evidence"]
    deltas: dict[str, float | int]


class PracticeAttemptResponse(AttemptResponse):
    session_id: int = Field(ge=1)
    sequence_number: int = Field(ge=1)
    intervention: InterventionResponse | None = None
    comparison: AttemptComparisonResponse | None = None


class PracticeSessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario: str = Field(default="Explain a technical project to a non-technical person in 60 seconds.", min_length=1, max_length=500)
    audience: str = Field(default="recruiter or non-technical interviewer", min_length=1, max_length=200)
    goal: str = Field(default="make the project understandable and relevant", min_length=1, max_length=300)
    requested_duration_seconds: int = Field(default=60, ge=10, le=300)


class PracticeSessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: int = Field(ge=1)
    scenario: str
    audience: str
    goal: str
    requested_duration_seconds: int
    status: Literal["active", "completed", "abandoned"]


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
