from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
Score = Annotated[float, Field(ge=0, le=10, allow_inf_nan=False, strict=True)]
Skill = Literal["clarity", "structure", "conciseness", "audience_awareness"]


class CommunicationEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transcript: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20000)]
    clarity: Score
    structure: Score
    conciseness: Score
    audience_awareness: Score
    strengths: list[Text] = Field(max_length=5)
    weaknesses: list[Text] = Field(max_length=5)
    recommended_focus: list[Skill] = Field(max_length=1)
