from pydantic import BaseModel
from typing import List

class CommunicationEvaluation(BaseModel):
    clarity: float
    structure: float
    conciseness: float
    audience_awareness: float
    
    strengths: List[str]
    weaknesses: List[str]
    
    recommended_focus: List[str]
    
    confidence: float
