from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
Score = Annotated[float, Field(ge=0, le=10, allow_inf_nan=False, strict=True)]
Skill = Literal["clarity", "structure", "conciseness", "audience_awareness"]
EvaluatorStatus = Literal["completed", "abstained"]
InputQuality = Literal["usable", "limited", "unusable"]
EvidenceStatus = Literal["quote_verified", "insufficient_evidence", "unavailable"]
FeedbackStatus = Literal["actionable", "needs_retry", "abstained"]


class EvidenceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skill: Skill
    quote: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    note: Text


class CommunicationEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evaluator_status: EvaluatorStatus = "completed"
    abstention_reason: Text | None = None
    input_quality: InputQuality
    evidence_status: EvidenceStatus
    feedback_status: FeedbackStatus
    transcript: Annotated[str, StringConstraints(strip_whitespace=True, max_length=20000)]
    clarity: Score | None = None
    structure: Score | None = None
    conciseness: Score | None = None
    audience_awareness: Score | None = None
    strengths: list[Text] = Field(max_length=5)
    weaknesses: list[Text] = Field(max_length=5)
    recommended_focus: list[Skill] = Field(max_length=1)
    evidence: list[EvidenceReference] = Field(max_length=8)

    @model_validator(mode="after")
    def validate_status_and_evidence(self):
        scores = [self.clarity, self.structure, self.conciseness, self.audience_awareness]
        if self.evaluator_status == "completed":
            if not self.transcript.strip():
                raise ValueError("completed evaluation requires transcript")
            if any(score is None for score in scores):
                raise ValueError("completed evaluation requires all scores")
            if self.abstention_reason is not None:
                raise ValueError("completed evaluation cannot include abstention_reason")
            if self.input_quality == "unusable":
                raise ValueError("completed evaluation cannot mark input unusable")
            if self.evidence_status != "quote_verified":
                raise ValueError("completed evaluation requires quote_verified evidence_status")
            if self.feedback_status != "actionable":
                raise ValueError("completed evaluation requires actionable feedback_status")
            if not self.evidence:
                raise ValueError("completed evaluation requires transcript evidence")
            lower_transcript = self.transcript.lower()
            for reference in self.evidence:
                if reference.quote.lower() not in lower_transcript:
                    raise ValueError("evidence quote must appear in transcript")
        else:
            if any(score is not None for score in scores):
                raise ValueError("abstained evaluation cannot include scores")
            if self.recommended_focus:
                raise ValueError("abstained evaluation cannot recommend a focus")
            if self.evidence:
                raise ValueError("abstained evaluation cannot include evidence")
            if self.abstention_reason is None:
                raise ValueError("abstained evaluation requires abstention_reason")
            if self.input_quality == "usable":
                raise ValueError("abstained evaluation cannot mark input usable")
            if self.evidence_status == "quote_verified":
                raise ValueError("abstained evaluation cannot mark evidence quote_verified")
            if self.feedback_status != "abstained":
                raise ValueError("abstained evaluation requires abstained feedback_status")
        return self
