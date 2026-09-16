import os
from hashlib import sha256
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, Header, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langsmith import tracing_context
from pydantic import ValidationError
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

load_dotenv()

from .agent.graph import build_coaching_graph
from .models.database import (
    CoachingAttempt,
    CoachingSession,
    PracticeAttempt,
    AttemptComparison,
    PracticeEvaluation,
    PracticeIntervention,
    PracticeMeasurement,
    PracticeSession,
    PracticeUser,
    SessionLocal,
)
from .schemas.attempt import (
    ATTEMPT_RESPONSE_SCHEMA_VERSION,
    METRIC_VERSION,
    RUBRIC_VERSION,
    AttemptRequest,
    AttemptResponse,
    AttemptComparisonResponse,
    ErrorResponse,
    EvaluationProvenance,
    InterventionResponse,
    Measurements,
    PracticeAttemptResponse,
    PracticeSessionCreate,
    PracticeSessionResponse,
    measurements_from_attempt,
    measurements_from_practice_measurement,
)
from .services.llm_provider import GEMINI_MODEL, ProviderFailure
from .services.media import InvalidMedia, MAX_AUDIO_BYTES, validate_audio
from .services.prompts import EVALUATION_PROMPT_VERSION

app = FastAPI(title="Adaptive Communication Coach API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Owner-Token"],
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


def owner_hash(owner_token: str) -> str:
    return sha256(owner_token.encode("utf-8")).hexdigest()


def get_or_create_practice_user(db: Session, owner_token: str) -> PracticeUser:
    token_hash = owner_hash(owner_token)
    user = db.query(PracticeUser).filter(PracticeUser.anonymous_device_id_hash == token_hash).one_or_none()
    if user:
        return user
    user = PracticeUser(anonymous_device_id_hash=token_hash)
    db.add(user)
    db.flush()
    return user


def read_validated_audio(audio: UploadFile, duration_seconds: float):
    try:
        request = AttemptRequest(duration_seconds=duration_seconds)
        raw = audio.file.read(MAX_AUDIO_BYTES + 1)
        return validate_audio(raw, audio.content_type, request.duration_seconds)
    except (InvalidMedia, ValidationError):
        return None
    finally:
        audio.file.close()


def evaluate_media(media, scenario: str, workflow):
    with tracing_context(enabled=False):
        state = workflow.invoke({
            "audio_bytes": media.audio_bytes,
            "mime_type": "audio/wav",
            "duration_seconds": media.duration_seconds,
            "scenario": scenario,
        })
    return Measurements(**state["deterministic_metrics"]), state["rubric_evaluation"]


def evaluation_provenance() -> EvaluationProvenance:
    return EvaluationProvenance(
        prompt_version=EVALUATION_PROMPT_VERSION,
        model_id=GEMINI_MODEL,
        schema_version=ATTEMPT_RESPONSE_SCHEMA_VERSION,
        rubric_version=RUBRIC_VERSION,
        metric_version=METRIC_VERSION,
    )


DRILL_VERSION = "technical-explanation-drills-v1"
DRILLS = {
    "clarity": "Say the main idea in one plain sentence before adding details.",
    "structure": "Use this order: problem, what you built, result, why it matters.",
    "conciseness": "Cut one side detail and keep only what helps the listener decide.",
    "audience_awareness": "Replace one technical term with the listener-facing benefit.",
}


def score_for_skill(evaluation: PracticeEvaluation, skill: str) -> float | None:
    return getattr(evaluation, skill)


def comparison_verdict(delta: float) -> str:
    if delta >= 1:
        return "improved"
    if delta <= -1:
        return "regressed"
    return "no_clear_change"


def evaluation_allows_coaching_write(evaluation) -> bool:
    recommended_focus = getattr(evaluation, "recommended_focus", None)
    has_focus = bool(recommended_focus)
    return (
        evaluation.evaluator_status == "completed"
        and evaluation.input_quality == "usable"
        and evaluation.evidence_status == "quote_verified"
        and evaluation.feedback_status == "actionable"
        and has_focus
    )


def intervention_response(intervention: PracticeIntervention | None) -> InterventionResponse | None:
    if intervention is None:
        return None
    return InterventionResponse(
        intervention_id=intervention.id,
        target_skill=intervention.target_skill,
        drill_version=intervention.drill_version,
        drill_text=intervention.drill_text,
        status=intervention.status,
    )


def comparison_response(comparison: AttemptComparison | None) -> AttemptComparisonResponse | None:
    if comparison is None:
        return None
    return AttemptComparisonResponse(
        comparison_id=comparison.id,
        baseline_attempt_id=comparison.baseline_attempt_id,
        retry_attempt_id=comparison.retry_attempt_id,
        intervention_id=comparison.intervention_id,
        target_skill=comparison.target_skill,
        comparability_status=comparison.comparability_status,
        verdict=comparison.verdict,
        deltas=comparison.deltas_json or {},
    )


def response_from_practice_attempt(
    attempt: PracticeAttempt,
    measurement: PracticeMeasurement,
    evaluation: PracticeEvaluation,
    intervention: PracticeIntervention | None = None,
    comparison: AttemptComparison | None = None,
) -> PracticeAttemptResponse:
    rubric = {
        "evaluator_status": evaluation.evaluator_status,
        "abstention_reason": evaluation.abstention_reason,
        "input_quality": evaluation.input_quality,
        "evidence_status": evaluation.evidence_status,
        "feedback_status": evaluation.feedback_status,
        "transcript": attempt.transcript,
        "clarity": evaluation.clarity,
        "structure": evaluation.structure,
        "conciseness": evaluation.conciseness,
        "audience_awareness": evaluation.audience_awareness,
        "strengths": evaluation.strengths_json or [],
        "weaknesses": evaluation.weaknesses_json or [],
        "recommended_focus": [evaluation.recommended_focus] if evaluation.recommended_focus else [],
        "evidence": evaluation.evidence_json or [],
    }
    return PracticeAttemptResponse(
        attempt_id=attempt.id,
        session_id=attempt.session_id,
        sequence_number=attempt.sequence_number,
        measurements=measurements_from_practice_measurement(measurement, attempt.media_duration_seconds),
        evaluation=rubric,
        provenance=evaluation_provenance(),
        intervention=intervention_response(intervention),
        comparison=comparison_response(comparison),
    )


def latest_intervention_for_session(db: Session, session_id: int) -> PracticeIntervention | None:
    return (
        db.query(PracticeIntervention)
        .filter(PracticeIntervention.session_id == session_id)
        .order_by(PracticeIntervention.id.desc())
        .first()
    )


def comparison_for_attempt(db: Session, attempt_id: int) -> AttemptComparison | None:
    return db.query(AttemptComparison).filter(AttemptComparison.retry_attempt_id == attempt_id).one_or_none()


def create_intervention_if_possible(
    db: Session,
    session_id: int,
    attempt_id: int,
    evaluation,
) -> PracticeIntervention | None:
    if not evaluation_allows_coaching_write(evaluation):
        return None
    target_skill = evaluation.recommended_focus[0] if evaluation.recommended_focus else None
    intervention = PracticeIntervention(
        session_id=session_id,
        source_attempt_id=attempt_id,
        target_skill=target_skill,
        drill_version=DRILL_VERSION,
        drill_text=DRILLS[target_skill],
        status="assigned",
    )
    db.add(intervention)
    db.flush()
    return intervention


def create_comparison_if_possible(
    db: Session,
    session_id: int,
    retry_attempt: PracticeAttempt,
    retry_evaluation: PracticeEvaluation,
) -> tuple[PracticeIntervention | None, AttemptComparison | None]:
    intervention = latest_intervention_for_session(db, session_id)
    if intervention is None or intervention.source_attempt_id == retry_attempt.id:
        return intervention, None

    if not evaluation_allows_coaching_write(retry_evaluation):
        return intervention, None

    baseline_evaluation = (
        db.query(PracticeEvaluation)
        .filter(PracticeEvaluation.attempt_id == intervention.source_attempt_id)
        .one_or_none()
    )
    if baseline_evaluation is None:
        return intervention, None
    if not evaluation_allows_coaching_write(baseline_evaluation):
        return intervention, None

    baseline_score = score_for_skill(baseline_evaluation, intervention.target_skill)
    retry_score = score_for_skill(retry_evaluation, intervention.target_skill)
    if baseline_score is None or retry_score is None:
        comparability_status = "insufficient_evidence"
        verdict = "insufficient_evidence"
        deltas = {}
    elif baseline_evaluation.rubric_version != retry_evaluation.rubric_version:
        comparability_status = "rubric_mismatch"
        verdict = "insufficient_evidence"
        deltas = {}
    else:
        delta = round(retry_score - baseline_score, 2)
        comparability_status = "comparable"
        verdict = comparison_verdict(delta)
        deltas = {
            intervention.target_skill: delta,
            "wpm": 0,
            "total_fillers": 0,
        }

    baseline_measurement = db.query(PracticeMeasurement).filter(PracticeMeasurement.attempt_id == intervention.source_attempt_id).one_or_none()
    retry_measurement = db.query(PracticeMeasurement).filter(PracticeMeasurement.attempt_id == retry_attempt.id).one_or_none()
    if baseline_measurement and retry_measurement and deltas:
        deltas["wpm"] = retry_measurement.wpm - baseline_measurement.wpm
        deltas["total_fillers"] = retry_measurement.total_fillers - baseline_measurement.total_fillers

    comparison = AttemptComparison(
        session_id=session_id,
        baseline_attempt_id=intervention.source_attempt_id,
        retry_attempt_id=retry_attempt.id,
        intervention_id=intervention.id,
        target_skill=intervention.target_skill,
        comparability_status=comparability_status,
        verdict=verdict,
        deltas_json=deltas,
    )
    intervention.status = "completed"
    db.add(comparison)
    db.flush()
    return intervention, comparison


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    # Do not echo submitted data embedded in validation errors.
    return error_response(422, "invalid_request", "Submit audio and a recording duration between 1 and 65 seconds.")


@app.post(
    "/api/practice-sessions",
    response_model=PracticeSessionResponse,
    responses={status: {"model": ErrorResponse} for status in (422, 503)},
)
def create_practice_session(
    request: PracticeSessionCreate,
    x_owner_token: str = Header(..., min_length=8, max_length=200),
    db: Session = Depends(get_db),
):
    try:
        user = get_or_create_practice_user(db, x_owner_token)
        session = PracticeSession(
            owner_id=user.id,
            scenario=request.scenario,
            audience=request.audience,
            goal=request.goal,
            requested_duration_seconds=request.requested_duration_seconds,
            status="active",
        )
        db.add(session)
        db.flush()
        response = PracticeSessionResponse(
            session_id=session.id,
            scenario=session.scenario,
            audience=session.audience,
            goal=session.goal,
            requested_duration_seconds=session.requested_duration_seconds,
            status=session.status,
        )
        db.commit()
        return response
    except SQLAlchemyError:
        db.rollback()
        return error_response(503, "storage_failed", "The practice session could not be created. Please try again.")


@app.post(
    "/api/practice-sessions/{session_id}/attempts",
    response_model=PracticeAttemptResponse,
    responses={status: {"model": ErrorResponse} for status in (403, 404, 409, 422, 502, 503)},
)
def process_practice_session_attempt(
    session_id: int,
    audio: UploadFile = File(...),
    duration_seconds: float = Form(..., ge=1, le=65),
    idempotency_key: str = Form(..., min_length=8, max_length=200),
    x_owner_token: str = Header(..., min_length=8, max_length=200),
    db: Session = Depends(get_db),
    workflow=Depends(get_graph),
):
    media = read_validated_audio(audio, duration_seconds)
    if media is None:
        return error_response(422, "invalid_media", "The recording is invalid or unsupported. Record 1-60 seconds and try again.")

    try:
        session = db.get(PracticeSession, session_id)
        if session is None:
            return error_response(404, "session_not_found", "The practice session does not exist.")
        owner = db.get(PracticeUser, session.owner_id)
        if owner is None or owner.anonymous_device_id_hash != owner_hash(x_owner_token):
            return error_response(403, "forbidden", "You cannot add attempts to this practice session.")

        existing = (
            db.query(PracticeAttempt)
            .filter(PracticeAttempt.session_id == session.id, PracticeAttempt.idempotency_key == idempotency_key)
            .one_or_none()
        )
        if existing:
            existing_measurement = db.query(PracticeMeasurement).filter(PracticeMeasurement.attempt_id == existing.id).one_or_none()
            existing_evaluation = db.query(PracticeEvaluation).filter(PracticeEvaluation.attempt_id == existing.id).one_or_none()
            if existing.status in {"completed", "abstained"} and existing_measurement and existing_evaluation:
                existing_intervention = (
                    db.query(PracticeIntervention)
                    .filter(PracticeIntervention.source_attempt_id == existing.id)
                    .one_or_none()
                )
                existing_comparison = comparison_for_attempt(db, existing.id)
                if existing_intervention is None and existing_comparison is not None:
                    existing_intervention = db.get(PracticeIntervention, existing_comparison.intervention_id)
                return response_from_practice_attempt(
                    existing,
                    existing_measurement,
                    existing_evaluation,
                    existing_intervention,
                    existing_comparison,
                )
            return error_response(409, "attempt_in_progress", "An attempt with this idempotency key already exists but is not complete.")

        metrics, evaluation = evaluate_media(media, session.scenario, workflow)
        next_sequence = (
            db.query(func.coalesce(func.max(PracticeAttempt.sequence_number), 0))
            .filter(PracticeAttempt.session_id == session.id)
            .scalar()
            + 1
        )
        attempt = PracticeAttempt(
            session_id=session.id,
            sequence_number=next_sequence,
            idempotency_key=idempotency_key,
            status="abstained" if evaluation.evaluator_status == "abstained" else "completed",
            capture_duration_seconds=duration_seconds,
            media_duration_seconds=metrics.duration_seconds,
            transcript=evaluation.transcript,
        )
        db.add(attempt)
        db.flush()
        measurement = PracticeMeasurement(
            attempt_id=attempt.id,
            metric_version=METRIC_VERSION,
            duration_source=metrics.duration_source,
            word_count=metrics.word_count,
            wpm=metrics.wpm,
            total_fillers=metrics.total_fillers,
            filler_words_json=[item.model_dump() for item in metrics.filler_words_list],
        )
        stored_evaluation = PracticeEvaluation(
            attempt_id=attempt.id,
            prompt_version=EVALUATION_PROMPT_VERSION,
            model_id=GEMINI_MODEL,
            schema_version=ATTEMPT_RESPONSE_SCHEMA_VERSION,
            rubric_version=RUBRIC_VERSION,
            evaluator_status=evaluation.evaluator_status,
            input_quality=evaluation.input_quality,
            evidence_status=evaluation.evidence_status,
            feedback_status=evaluation.feedback_status,
            clarity=evaluation.clarity,
            structure=evaluation.structure,
            conciseness=evaluation.conciseness,
            audience_awareness=evaluation.audience_awareness,
            strengths_json=evaluation.strengths,
            weaknesses_json=evaluation.weaknesses,
            recommended_focus=evaluation.recommended_focus[0] if evaluation.recommended_focus else None,
            evidence_json=[item.model_dump() for item in evaluation.evidence],
            abstention_reason=evaluation.abstention_reason,
        )
        db.add_all([measurement, stored_evaluation])
        db.flush()
        if next_sequence == 1:
            intervention = create_intervention_if_possible(db, session.id, attempt.id, evaluation)
            comparison = None
        else:
            intervention, comparison = create_comparison_if_possible(db, session.id, attempt, stored_evaluation)
        response = response_from_practice_attempt(attempt, measurement, stored_evaluation, intervention, comparison)
        db.commit()
        return response
    except IntegrityError:
        db.rollback()
        return error_response(409, "duplicate_attempt", "This attempt was already submitted.")
    except (ProviderFailure, ValidationError):
        db.rollback()
        return error_response(502, "evaluation_failed", "The audio could not be evaluated. You can retry this recording.")
    except SQLAlchemyError:
        db.rollback()
        return error_response(503, "storage_failed", "The result could not be saved. Please try again.")


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
    # Compatibility shim for the original web prototype endpoint.
    media = read_validated_audio(audio, duration_seconds)
    if media is None:
        return error_response(422, "invalid_media", "The recording is invalid or unsupported. Record 1-60 seconds and try again.")

    try:
        metrics, evaluation = evaluate_media(media, SCENARIO, workflow)
        # Storage IDs are not user identities. No history lookup/profile mutation.
        session_id = str(uuid4())
        db.add(CoachingSession(session_id=session_id, user_id=None, scenario=SCENARIO))
        attempt = CoachingAttempt(
            session_id=session_id,
            attempt_number=1,
            transcript=evaluation.transcript,
            duration_seconds=metrics.duration_seconds,
            word_count=metrics.word_count,
            duration_source=metrics.duration_source,
            wpm=metrics.wpm,
            filler_words_count=metrics.total_fillers,
            filler_words_list=[item.model_dump() for item in metrics.filler_words_list],
            clarity=evaluation.clarity,
            structure=evaluation.structure,
            conciseness=evaluation.conciseness,
            audience_awareness=evaluation.audience_awareness,
            strengths=evaluation.strengths,
            weaknesses=evaluation.weaknesses,
            focus_area=evaluation.recommended_focus[0] if evaluation.recommended_focus else None,
        )
        db.add(attempt)
        db.flush()
        response = AttemptResponse(
            attempt_id=attempt.id,
            measurements=measurements_from_attempt(attempt),
            evaluation=evaluation,
            provenance=evaluation_provenance(),
        )
        db.commit()
        return response
    except (ProviderFailure, ValidationError):
        db.rollback()
        return error_response(502, "evaluation_failed", "The audio could not be evaluated. You can retry this recording.")
    except SQLAlchemyError:
        db.rollback()
        return error_response(503, "storage_failed", "The result could not be saved. Please try again.")
