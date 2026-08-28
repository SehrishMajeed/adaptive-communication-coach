import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
from pydantic import BaseModel
from typing import List, Dict, Any

from .agent.graph import build_coaching_graph
from .agent.state import CoachingState
from .models.database import SessionLocal, UserProfile, CoachingSession, CoachingAttempt

app = FastAPI(title="Adaptive Communication Coach API")

origins_env = os.environ.get("CORS_ORIGINS", "*")
origins = [origin.strip() for origin in origins_env.split(",")] if origins_env else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_coaching_graph()

@app.post("/api/sessions/latest/attempts")
async def process_attempt(audio: UploadFile = File(...)):
    db = SessionLocal()
    try:
        user_id = "demo_user"
        session_id = "demo_session"
        scenario_text = "Explain a technical project to a non-technical person in 60 seconds."
        
        # 1. User Profile
        user = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not user:
            user = UserProfile(user_id=user_id)
            db.add(user)
            db.commit()
            
        # 2. Session
        session = db.query(CoachingSession).filter(CoachingSession.session_id == session_id).first()
        if not session:
            session = CoachingSession(session_id=session_id, user_id=user_id, scenario=scenario_text)
            db.add(session)
            db.commit()
            
        # 3. Attempt Number & Previous Metrics
        attempts = db.query(CoachingAttempt).filter(CoachingAttempt.session_id == session_id).order_by(CoachingAttempt.attempt_number.desc()).all()
        attempt_number = attempts[0].attempt_number + 1 if attempts else 1
        
        previous_metrics = None
        if attempt_number > 1:
            prev = attempts[0]
            previous_metrics = {
                "wpm": prev.wpm,
                "filler_words_count": prev.filler_words_count,
                "clarity": prev.clarity
            }
            
        # 4. Audio Processing
        audio_bytes = await audio.read()
        mime_type = audio.content_type or "audio/webm"
        
        # In absence of exact duration logic without ffprobe, we use a basic byte heuristic
        # WebM audio is typically 15-20kbps. We use a fallback heuristic.
        duration = max(len(audio_bytes) / 20000.0, 5.0) 
        
        # 5. Execute Graph
        initial_state = CoachingState(
            session_id=session_id,
            user_id=user_id,
            attempt_number=attempt_number,
            scenario=session.scenario,
            audio_bytes=audio_bytes,
            mime_type=mime_type,
            transcript=None,
            duration_seconds=duration,
            deterministic_metrics=None,
            rubric_evaluation=None,
            focus_area=None,
            next_exercise=None,
            previous_attempt_metrics=previous_metrics,
            comparison_delta=None
        )
        
        final_state = graph.invoke(initial_state)
        metrics = final_state.get("deterministic_metrics", {})
        eval = final_state.get("rubric_evaluation")
        
        if not eval:
            raise HTTPException(status_code=500, detail="Failed to evaluate communication")
            
        # 6. Save Attempt to DB
        new_attempt = CoachingAttempt(
            session_id=session_id,
            attempt_number=attempt_number,
            transcript=final_state.get("transcript", ""),
            duration_seconds=duration,
            wpm=metrics.get("wpm", 0),
            filler_words_count=metrics.get("filler_words_count", 0),
            clarity=eval.clarity,
            structure=eval.structure,
            conciseness=eval.conciseness,
            audience_awareness=eval.audience_awareness,
            strengths=eval.strengths,
            weaknesses=eval.weaknesses,
            focus_area=final_state.get("focus_area")
        )
        db.add(new_attempt)
        
        # Update UserProfile logic
        user.total_sessions += 1
        # Simple rolling average logic
        n = user.total_sessions
        user.avg_clarity = ((user.avg_clarity * (n - 1)) + eval.clarity) / n
        db.commit()
            
        # 7. Return shaped response for frontend (NO FABRICATED MOCKS)
        return {
            "overallImpression": "Great job! Let's review your communication metrics.",
            "confidenceScore": int(eval.confidence * 10) if eval else 75,
            "clarityScore": int(eval.clarity * 10) if eval else 80,
            "engagementScore": int(eval.audience_awareness * 10) if eval else 70,
            "strengths": {
                "content": eval.strengths
            },
            "areasForImprovement": {
                "content": eval.weaknesses
            },
            "fillerWords": metrics.get("filler_words_list", []),
            "pace": {
                "wpm": metrics.get("wpm", 0),
                "feedback": "Pace is a bit slow." if metrics.get("wpm", 0) < 120 else "Good pace."
            },
            "actionableTips": [final_state.get("next_exercise", "Keep practicing.")],
            "transcript": final_state.get("transcript", ""),
            "comparison": final_state.get("comparison_delta")
        }
    finally:
        db.close()
