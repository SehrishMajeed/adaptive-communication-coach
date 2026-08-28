from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from .domain.metrics import calculate_deterministic_metrics

app = FastAPI(title="Adaptive Communication Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock transcript for now until transcription service is wired
MOCK_TRANSCRIPT = "Um, hello. I am like, very excited to be here. You know, building this project is actually quite fun."
MOCK_DURATION = 10.0 # seconds

from .agent.graph import build_coaching_graph
from .agent.state import CoachingState

graph = build_coaching_graph()

@app.post("/api/sessions/latest/attempts")
async def process_attempt(audio: UploadFile = File(...)):
    # 1. (Mock) Transcription
    transcript = MOCK_TRANSCRIPT
    duration = MOCK_DURATION # In reality, we extract this from the audio file
    
    # 2. Execute Graph
    initial_state = CoachingState(
        session_id="mock_session",
        user_id="mock_user",
        attempt_number=1,
        scenario="Explain a technical project to a non-technical person in 60 seconds.",
        transcript=transcript,
        duration_seconds=duration,
        deterministic_metrics=None,
        rubric_evaluation=None,
        focus_area=None,
        next_exercise=None,
        previous_attempt_metrics=None,
        comparison_delta=None
    )
    
    final_state = graph.invoke(initial_state)
    metrics = final_state.get("deterministic_metrics", {})
    eval = final_state.get("rubric_evaluation")
    
    if not eval:
        raise ValueError("Failed to evaluate communication")
        
    # 3. Return shaped response for frontend
    return {
        "overallImpression": "Good start, let's keep practicing.",
        "confidenceScore": int(eval.confidence * 10) if eval else 75,
        "clarityScore": int(eval.clarity * 10) if eval else 80,
        "engagementScore": int(eval.audience_awareness * 10) if eval else 70,
        "strengths": {
            "bodyLanguage": ["Good posture (mock)"],
            "vocalVariety": ["Clear volume (mock)"],
            "content": eval.strengths
        },
        "areasForImprovement": {
            "bodyLanguage": ["Maintain eye contact (mock)"],
            "vocalVariety": ["Vary your tone (mock)"],
            "content": eval.weaknesses
        },
        "fillerWords": metrics.get("filler_words_list", []),
        "pace": {
            "wpm": metrics.get("wpm", 0),
            "feedback": "Pace is a bit slow." if metrics.get("wpm", 0) < 120 else "Good pace."
        },
        "actionableTips": [final_state.get("next_exercise", "Keep practicing.")]
    }
