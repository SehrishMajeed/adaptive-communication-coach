from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from ..domain.evaluation import CommunicationEvaluation


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


class AttemptResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attempt_id: int = Field(ge=1)
    measurements: Measurements
    evaluation: CommunicationEvaluation


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
