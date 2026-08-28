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

@app.post("/api/sessions/latest/attempts")
async def process_attempt(audio: UploadFile = File(...)):
    # 1. (Mock) Transcription
    transcript = MOCK_TRANSCRIPT
    duration = MOCK_DURATION # In reality, we extract this from the audio file
    
    # 2. Deterministic Metrics
    metrics = calculate_deterministic_metrics(transcript, duration)
    
    # 3. (Mock) LLM Evaluation
    # We will wire up LangGraph in the next step. 
    # For now, return the mock shape expected by the frontend.
    return {
        "overallImpression": "Good start, but watch the filler words.",
        "confidenceScore": 75,
        "clarityScore": 80,
        "engagementScore": 70,
        "strengths": {
            "bodyLanguage": ["Good posture"],
            "vocalVariety": ["Clear volume"],
            "content": ["Started strong"]
        },
        "areasForImprovement": {
            "bodyLanguage": ["Maintain eye contact"],
            "vocalVariety": ["Vary your tone"],
            "content": ["Reduce filler words"]
        },
        "fillerWords": metrics["filler_words_list"],
        "pace": {
            "wpm": metrics["wpm"],
            "feedback": "Pace is a bit slow." if metrics["wpm"] < 120 else "Good pace."
        },
        "actionableTips": [
            "Pause instead of saying 'um'."
        ]
    }
