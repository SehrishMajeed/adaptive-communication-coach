import os
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from langsmith import tracing_context
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

load_dotenv()

from .agent.graph import build_coaching_graph
from .models.database import CoachingAttempt, CoachingSession, SessionLocal
from .schemas.attempt import AttemptRequest, AttemptResponse, ErrorResponse, Measurements, measurements_from_attempt
from .services.llm_provider import ProviderFailure
from .services.media import InvalidMedia, MAX_AUDIO_BYTES, validate_audio

app = FastAPI(title="Adaptive Communication Coach API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")],
    allow_credentials=False, allow_methods=["POST"], allow_headers=["Content-Type"],
)
graph = build_coaching_graph()
SCENARIO = "Explain a technical project to a non-technical person in 60 seconds."


def get_db():
    with SessionLocal() as db:
        yield db


def get_graph():
    return graph


def error_response(status: int, code: str, message: str):
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    # Do not echo submitted data embedded in validation errors.
    return error_response(422, "invalid_request", "Submit audio and a recording duration between 1 and 65 seconds.")


@app.post(
    "/api/sessions/latest/attempts", response_model=AttemptResponse,
    responses={status: {"model": ErrorResponse} for status in (422, 502, 503)},
)
def process_attempt(
    audio: UploadFile = File(...),
    duration_seconds: float = Form(..., ge=1, le=65),
    db: Session = Depends(get_db),
    workflow=Depends(get_graph),
):
    # Sync route keeps blocking provider/ORM work off the event loop.
    try:
        request = AttemptRequest(duration_seconds=duration_seconds)
        raw = audio.file.read(MAX_AUDIO_BYTES + 1)
        media = validate_audio(raw, audio.content_type, request.duration_seconds)
    except (InvalidMedia, ValidationError):
        return error_response(422, "invalid_media", "The recording is invalid or unsupported. Record 1–60 seconds and try again.")
    finally:
        audio.file.close()

    try:
        # Raw audio/transcripts must not enter graph traces, even if enabled globally.
        with tracing_context(enabled=False):
            state = workflow.invoke({
                "audio_bytes": media.audio_bytes, "mime_type": "audio/wav",
                "duration_seconds": media.duration_seconds, "scenario": SCENARIO,
            })
        metrics = Measurements(**state["deterministic_metrics"])
        evaluation = state["rubric_evaluation"]
        # Storage IDs are not user identities. No history lookup/profile mutation.
        session_id = str(uuid4())
        db.add(CoachingSession(session_id=session_id, user_id=None, scenario=SCENARIO))
        attempt = CoachingAttempt(
            session_id=session_id, attempt_number=1,
            transcript=evaluation.transcript, duration_seconds=metrics.duration_seconds,
            word_count=metrics.word_count, duration_source=metrics.duration_source,
            wpm=metrics.wpm, filler_words_count=metrics.total_fillers,
            filler_words_list=[item.model_dump() for item in metrics.filler_words_list],
            clarity=evaluation.clarity, structure=evaluation.structure,
            conciseness=evaluation.conciseness, audience_awareness=evaluation.audience_awareness,
            strengths=evaluation.strengths, weaknesses=evaluation.weaknesses,
            focus_area=evaluation.recommended_focus[0] if evaluation.recommended_focus else None,
        )
        db.add(attempt)
        db.flush()
        response = AttemptResponse(attempt_id=attempt.id, measurements=measurements_from_attempt(attempt), evaluation=evaluation)
        db.commit()
        return response
    except (ProviderFailure, ValidationError):
        db.rollback()
        return error_response(502, "evaluation_failed", "The audio could not be evaluated. You can retry this recording.")
    except SQLAlchemyError:
        db.rollback()
        return error_response(503, "storage_failed", "The result could not be saved. Please try again.")
