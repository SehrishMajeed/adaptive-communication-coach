import io
import wave
from unittest.mock import patch
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from backend.app.models.database import (
    AttemptComparison,
    CoachingAttempt,
    CoachingSession,
    PracticeAttempt,
    PracticeEvaluation,
    PracticeIntervention,
    PracticeMeasurement,
    PracticeSession,
    PracticeUser,
    UserProfile,
)
from backend.app.models.database import ensure_attempt_measurement_columns
from backend.app.schemas.attempt import ATTEMPT_RESPONSE_SCHEMA_VERSION, METRIC_VERSION, RUBRIC_VERSION, measurements_from_attempt
from backend.app.services.llm_provider import ProviderFailure
from backend.app.services.media import validate_audio, InvalidMedia, MAX_AUDIO_BYTES
from backend.app.services.prompts import EVALUATION_PROMPT_VERSION

URL = "/api/sessions/latest/attempts"
SESSION_URL = "/api/practice-sessions"
OWNER_HEADERS = {"X-Owner-Token": "owner-token-123"}


def wav(seconds=5, rate=8000, channels=1, width=2):
    output = io.BytesIO()
    with wave.open(output, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(width)
        writer.setframerate(rate)
        writer.writeframes(b"\x01" * int(seconds * rate * channels * width))
    return output.getvalue()


def submit(client, data=None, duration="5", mime="audio/wav"):
    return client.post(URL, files={"audio": ("recording.wav", wav() if data is None else data, mime)}, data={"duration_seconds": duration})


def create_session(client, headers=None, payload=None):
    return client.post(SESSION_URL, headers=headers or OWNER_HEADERS, json=payload or {})


def submit_session_attempt(client, session_id, idempotency_key="attempt-key-1", headers=None, data=None, duration="5", mime="audio/wav"):
    return client.post(
        f"{SESSION_URL}/{session_id}/attempts",
        headers=headers or OWNER_HEADERS,
        files={"audio": ("recording.wav", wav() if data is None else data, mime)},
        data={"duration_seconds": duration, "idempotency_key": idempotency_key},
    )


def test_http_contract_and_persistence(client, database, evaluator, contract):
    response = submit(client)
    assert response.status_code == 200
    assert response.json() == contract
    database.expire_all()
    saved = database.query(CoachingAttempt).one()
    assert saved.word_count == response.json()["measurements"]["word_count"] == 6
    assert saved.duration_source == response.json()["measurements"]["duration_source"] == "pcm_samples"
    assert saved.filler_words_count == response.json()["measurements"]["total_fillers"] == 2
    assert saved.filler_words_list == response.json()["measurements"]["filler_words_list"]
    assert saved.duration_seconds == 5
    assert saved.wpm == 72
    assert database.query(UserProfile).count() == 0
    audio, mime, scenario = evaluator.call_args.args
    assert mime == "audio/wav"
    assert audio == wav()
    assert "non-technical" in scenario


def test_create_practice_session_persists_anonymous_owner(client, database):
    result = create_session(client, payload={
        "scenario": "Explain my AI project",
        "audience": "recruiter",
        "goal": "make value clear",
        "requested_duration_seconds": 60,
    })
    assert result.status_code == 200
    body = result.json()
    assert body["session_id"] == 1
    assert body["scenario"] == "Explain my AI project"
    assert body["audience"] == "recruiter"
    assert body["goal"] == "make value clear"
    assert body["requested_duration_seconds"] == 60
    assert body["status"] == "active"
    assert database.query(PracticeUser).count() == 1
    saved = database.query(PracticeSession).one()
    assert saved.owner_id == database.query(PracticeUser).one().id


def test_practice_session_attempt_is_owned_versioned_and_sequence_scoped(client, database, evaluator, contract):
    session = create_session(client).json()
    first = submit_session_attempt(client, session["session_id"], idempotency_key="attempt-key-1")
    second = submit_session_attempt(client, session["session_id"], idempotency_key="attempt-key-2")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["measurements"] == contract["measurements"]
    assert [attempt.sequence_number for attempt in database.query(PracticeAttempt).order_by(PracticeAttempt.sequence_number)] == [1, 2]
    assert database.query(CoachingAttempt).count() == 0

    measurement = database.query(PracticeMeasurement).filter(PracticeMeasurement.attempt_id == first.json()["attempt_id"]).one()
    evaluation = database.query(PracticeEvaluation).filter(PracticeEvaluation.attempt_id == first.json()["attempt_id"]).one()
    assert measurement.metric_version == METRIC_VERSION
    assert evaluation.prompt_version == EVALUATION_PROMPT_VERSION
    assert evaluation.model_id == "gemini-2.5-flash"
    assert evaluation.schema_version == ATTEMPT_RESPONSE_SCHEMA_VERSION
    assert evaluation.rubric_version == RUBRIC_VERSION
    assert evaluation.evaluator_status == "completed"
    assert evaluation.input_quality == "usable"
    assert evaluation.evidence_status == "quote_verified"
    assert evaluation.feedback_status == "actionable"
    assert evaluation.evidence_json == contract["evaluation"]["evidence"]
    first_attempt = database.query(PracticeAttempt).filter(PracticeAttempt.id == first.json()["attempt_id"]).one()
    second_attempt = database.query(PracticeAttempt).filter(PracticeAttempt.id == second.json()["attempt_id"]).one()
    assert first_attempt.workflow_route == "baseline"
    assert first_attempt.workflow_reason == "first_eligible_attempt"
    assert second_attempt.workflow_route == "retry_comparable"
    assert second_attempt.workflow_reason == "retry_eligible_with_baseline"
    assert first.json()["provenance"] == contract["provenance"]
    assert first.json()["workflow"] == {
        "route": "baseline",
        "reason": "first_eligible_attempt",
        "creates_intervention": True,
        "creates_comparison": False,
    }
    assert first.json()["intervention"]["target_skill"] == "clarity"
    assert first.json()["intervention"]["status"] == "assigned"
    assert first.json()["comparison"] is None
    assert second.json()["comparison"]["baseline_attempt_id"] == first.json()["attempt_id"]
    assert second.json()["comparison"]["retry_attempt_id"] == second.json()["attempt_id"]
    assert second.json()["comparison"]["target_skill"] == "clarity"
    assert second.json()["workflow"] == {
        "route": "retry_comparable",
        "reason": "retry_eligible_with_baseline",
        "creates_intervention": False,
        "creates_comparison": True,
    }
    assert second.json()["comparison"]["comparability_status"] == "comparable"
    assert second.json()["comparison"]["verdict"] == "no_clear_change"
    assert database.query(PracticeIntervention).count() == 1
    assert database.query(AttemptComparison).count() == 1


def test_practice_session_retry_comparison_reports_improvement(client, database, evaluator, contract):
    session_id = create_session(client).json()["session_id"]
    submit_session_attempt(client, session_id, idempotency_key="baseline-key")
    improved = contract["evaluation"].copy()
    improved["clarity"] = 9
    evaluator.return_value = type(evaluator.return_value)(**improved)
    retry = submit_session_attempt(client, session_id, idempotency_key="retry-key")
    assert retry.status_code == 200
    comparison = retry.json()["comparison"]
    assert comparison["verdict"] == "improved"
    assert comparison["deltas"]["clarity"] == 2
    assert comparison["deltas"]["wpm"] == 0
    assert comparison["deltas"]["total_fillers"] == 0
    saved = database.query(AttemptComparison).one()
    assert saved.verdict == "improved"
    assert saved.deltas_json["clarity"] == 2


def test_quality_gate_blocks_intervention_for_abstained_attempt_and_replays_idempotently(client, database, evaluator, contract):
    session_id = create_session(client).json()["session_id"]
    abstained = {
        **contract["evaluation"],
        "evaluator_status": "abstained",
        "abstention_reason": "The audio did not contain enough intelligible speech.",
        "input_quality": "unusable",
        "evidence_status": "unavailable",
        "feedback_status": "abstained",
        "transcript": "",
        "clarity": None,
        "structure": None,
        "conciseness": None,
        "audience_awareness": None,
        "strengths": [],
        "weaknesses": [],
        "recommended_focus": [],
        "evidence": [],
    }
    evaluator.return_value = type(evaluator.return_value)(**abstained)

    first = submit_session_attempt(client, session_id, idempotency_key="abstain-key").json()
    second = submit_session_attempt(client, session_id, idempotency_key="abstain-key").json()

    assert second == first
    assert first["evaluation"]["evaluator_status"] == "abstained"
    assert first["workflow"] == {
        "route": "abstained",
        "reason": "abstained_evaluation",
        "creates_intervention": False,
        "creates_comparison": False,
    }
    assert first["intervention"] is None
    assert first["comparison"] is None
    saved_attempt = database.query(PracticeAttempt).one()
    assert saved_attempt.status == "abstained"
    assert saved_attempt.workflow_route == "abstained"
    assert saved_attempt.workflow_reason == "abstained_evaluation"
    assert database.query(PracticeIntervention).count() == 0
    assert database.query(AttemptComparison).count() == 0
    assert evaluator.call_count == 1


def test_quality_gate_blocks_comparison_for_limited_quality_retry(client, database, evaluator, contract):
    session_id = create_session(client).json()["session_id"]
    baseline = submit_session_attempt(client, session_id, idempotency_key="baseline-key").json()
    limited = contract["evaluation"].copy()
    limited["input_quality"] = "limited"
    evaluator.return_value = type(evaluator.return_value)(**limited)

    retry = submit_session_attempt(client, session_id, idempotency_key="limited-retry-key").json()

    assert baseline["intervention"]["target_skill"] == "clarity"
    assert retry["evaluation"]["input_quality"] == "limited"
    assert retry["workflow"] == {
        "route": "retry_blocked",
        "reason": "retry_not_eligible",
        "creates_intervention": False,
        "creates_comparison": False,
    }
    assert retry["comparison"] is None
    assert retry["intervention"]["status"] == "assigned"
    saved_retry = database.query(PracticeAttempt).filter(PracticeAttempt.id == retry["attempt_id"]).one()
    assert saved_retry.workflow_route == "retry_blocked"
    assert saved_retry.workflow_reason == "retry_not_eligible"
    assert database.query(PracticeIntervention).count() == 1
    assert database.query(PracticeIntervention).one().status == "assigned"
    assert database.query(AttemptComparison).count() == 0


def test_practice_session_attempt_idempotency_returns_existing_completed_attempt(client, database, evaluator):
    session_id = create_session(client).json()["session_id"]
    first = submit_session_attempt(client, session_id, idempotency_key="same-key-123").json()
    second = submit_session_attempt(client, session_id, idempotency_key="same-key-123").json()
    assert second == first
    assert database.query(PracticeAttempt).count() == 1
    assert database.query(PracticeIntervention).count() == 1
    assert evaluator.call_count == 1


def test_practice_session_retry_idempotency_replays_existing_comparison(client, database, evaluator):
    session_id = create_session(client).json()["session_id"]
    submit_session_attempt(client, session_id, idempotency_key="baseline-key")
    first_retry = submit_session_attempt(client, session_id, idempotency_key="retry-key").json()
    second_retry = submit_session_attempt(client, session_id, idempotency_key="retry-key").json()
    assert second_retry == first_retry
    assert second_retry["comparison"]["baseline_attempt_id"] == 1
    assert database.query(PracticeAttempt).count() == 2
    assert database.query(AttemptComparison).count() == 1
    assert evaluator.call_count == 2


def test_practice_session_attempt_rejects_wrong_owner(client, database, evaluator):
    session_id = create_session(client).json()["session_id"]
    result = submit_session_attempt(client, session_id, headers={"X-Owner-Token": "other-owner-123"})
    assert result.status_code == 403
    evaluator.assert_not_called()
    assert database.query(PracticeAttempt).count() == 0


def test_practice_session_attempt_provider_failure_does_not_complete_attempt(client, database, evaluator):
    session_id = create_session(client).json()["session_id"]
    evaluator.side_effect = ProviderFailure("secret-provider-detail")
    result = submit_session_attempt(client, session_id)
    assert result.status_code == 502
    assert database.query(PracticeAttempt).count() == 0
    assert database.query(PracticeEvaluation).count() == 0
    assert database.query(PracticeMeasurement).count() == 0


def test_practice_session_attempt_rejects_missing_session_before_provider(client, database, evaluator):
    result = submit_session_attempt(client, 999)
    assert result.status_code == 404
    evaluator.assert_not_called()
    assert database.query(PracticeAttempt).count() == 0


def test_measurements_round_trip_from_committed_database_row(client, database, evaluator, contract):
    result = submit(client)
    assert result.status_code == 200

    attempt_id = result.json()["attempt_id"]
    database.close()
    factory = sessionmaker(bind=database.get_bind())
    with factory() as fresh:
        loaded = fresh.get(CoachingAttempt, attempt_id)
        reconstructed = measurements_from_attempt(loaded).model_dump()
        assert reconstructed == contract["measurements"]
        assert loaded.transcript == contract["evaluation"]["transcript"]
        assert loaded.clarity == contract["evaluation"]["clarity"]
        assert loaded.structure == contract["evaluation"]["structure"]
        assert loaded.conciseness == contract["evaluation"]["conciseness"]
        assert loaded.audience_awareness == contract["evaluation"]["audience_awareness"]
        assert loaded.strengths == contract["evaluation"]["strengths"]
        assert loaded.weaknesses == contract["evaluation"]["weaknesses"]
        assert loaded.focus_area == contract["evaluation"]["recommended_focus"][0]


def test_repeat_uploads_never_read_or_update_shared_profile(client, database, evaluator):
    profile = UserProfile(user_id="demo_user", avg_clarity=9, total_sessions=10)
    database.add(profile)
    database.commit()
    first, second = submit(client).json(), submit(client).json()
    assert "comparison" not in first and "comparison" not in second
    sessions = database.query(CoachingSession).all()
    assert len({x.session_id for x in sessions}) == 2
    assert all(x.user_id is None for x in sessions)
    database.refresh(profile)
    assert profile.avg_clarity == 9 and profile.total_sessions == 10
    assert [a.attempt_number for a in database.query(CoachingAttempt).all()] == [1, 1]


@pytest.mark.parametrize("duration", ["0", "-1", "66", "nan", "inf", "not-a-number", "1"])
def test_invalid_duration_before_provider(client, evaluator, database, duration):
    assert submit(client, duration=duration).status_code == 422
    evaluator.assert_not_called()
    assert database.query(CoachingAttempt).count() == 0


@pytest.mark.parametrize("data,mime", [
    (b"", "audio/wav"), (b"fake media" * 10, "audio/wav"),
    (wav(), "video/webm"), (wav()[:-10], "audio/wav"),
    (wav(channels=2), "audio/wav"), (wav(width=1), "audio/wav"),
    (wav(seconds=0.5), "audio/wav"), (b"x" * (MAX_AUDIO_BYTES + 1), "audio/wav"),
], ids=["empty", "garbage", "video", "truncated", "stereo", "pcm8", "short", "oversized"])
def test_invalid_media_before_provider(client, evaluator, database, data, mime):
    assert submit(client, data, mime=mime).status_code == 422
    evaluator.assert_not_called()
    assert database.query(CoachingSession).count() == 0


def test_missing_fields_are_safe(client, evaluator):
    result = client.post(URL, data={"duration_seconds": "private-invalid-input"})
    assert result.status_code == 422
    assert "private-invalid-input" not in result.text
    evaluator.assert_not_called()


def test_provider_failure_does_not_persist(client, database, evaluator):
    evaluator.side_effect = ProviderFailure("secret-provider-detail")
    result = submit(client)
    assert result.status_code == 502
    assert "secret-provider-detail" not in result.text
    assert database.query(CoachingAttempt).count() == 0
    assert database.query(CoachingSession).count() == 0
    assert database.query(UserProfile).count() == 0


def test_commit_failure_rolls_back(client, database, evaluator):
    with patch.object(database, "commit", side_effect=SQLAlchemyError("private-db-detail")):
        result = submit(client)
    assert result.status_code == 503
    assert "private-db-detail" not in result.text
    assert database.query(CoachingAttempt).count() == 0
    assert database.query(CoachingSession).count() == 0


def test_duration_is_sample_based_not_compressed_byte_guess():
    small = validate_audio(wav(rate=8000), "audio/wav", 5)
    large = validate_audio(wav(rate=48000), "audio/wav", 5)
    assert len(small.audio_bytes) != len(large.audio_bytes)
    assert small.duration_seconds == large.duration_seconds == 5


def test_ancillary_payload_does_not_reach_provider():
    data = wav()
    assert validate_audio(data + b"private-trailing-payload", "audio/wav", 5).audio_bytes == data


@pytest.mark.parametrize("duration", [float("nan"), float("inf"), -1, 0, 66])
def test_direct_media_validation_bounds(duration):
    with pytest.raises(InvalidMedia):
        validate_audio(wav(), "audio/wav", duration)

def test_invalid_provider_json_through_http(client, database, monkeypatch):
    from unittest.mock import MagicMock
    sdk = MagicMock()
    sdk.__enter__.return_value = sdk
    sdk.models.generate_content.return_value.text = '{"transcript":"hello","clarity":999}'
    monkeypatch.setattr("backend.app.services.llm_provider.genai.Client", lambda **kwargs: sdk)
    result = submit(client)
    assert result.status_code == 502
    assert database.query(CoachingAttempt).count() == 0
    assert database.query(UserProfile).count() == 0


def test_invalid_provider_score_through_http(client, database, monkeypatch, contract):
    import json
    from unittest.mock import MagicMock
    contract["evaluation"]["clarity"] = 11
    sdk = MagicMock()
    sdk.__enter__.return_value = sdk
    sdk.models.generate_content.return_value.text = json.dumps(contract["evaluation"])
    monkeypatch.setattr("backend.app.services.llm_provider.genai.Client", lambda **kwargs: sdk)
    assert submit(client).status_code == 502
    assert database.query(CoachingAttempt).count() == 0


def test_openapi_documents_success_and_error_contracts(client):
    operation = client.get("/openapi.json").json()["paths"][URL]["post"]
    responses = operation["responses"]
    assert responses["200"]["content"]["application/json"]["schema"]["$ref"].endswith("AttemptResponse")
    for status in ("422", "502", "503"):
        assert responses[status]["content"]["application/json"]["schema"]["$ref"].endswith("ErrorResponse")


def test_schema_compatibility_adds_measurement_columns_to_existing_attempt_table():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE coaching_attempts (
                id INTEGER PRIMARY KEY,
                session_id VARCHAR,
                attempt_number INTEGER,
                transcript VARCHAR,
                duration_seconds FLOAT,
                wpm FLOAT,
                filler_words_count INTEGER,
                clarity FLOAT,
                structure FLOAT,
                conciseness FLOAT,
                audience_awareness FLOAT,
                strengths JSON,
                weaknesses JSON,
                focus_area VARCHAR
            )
        """))
    ensure_attempt_measurement_columns(engine)
    with engine.connect() as connection:
        columns = {row[1] for row in connection.execute(text("PRAGMA table_info(coaching_attempts)"))}
    assert {"word_count", "duration_source", "filler_words_list"}.issubset(columns)
