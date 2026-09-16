from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError


ROOT = Path(__file__).resolve().parents[1]


def alembic_config(database_url: str) -> Config:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "backend" / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


@pytest.fixture
def migrated_engine(tmp_path, monkeypatch):
    database_url = f"sqlite:///{tmp_path / 'phase2.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("DB_AUTO_CREATE", "false")
    command.upgrade(alembic_config(database_url), "head")
    engine = create_engine(database_url)
    try:
        yield engine
    finally:
        engine.dispose()


def test_phase2_migration_creates_durable_practice_tables(migrated_engine):
    inspector = inspect(migrated_engine)
    tables = set(inspector.get_table_names())
    assert {
        "practice_users",
        "practice_sessions",
        "practice_attempts",
        "practice_evaluations",
        "practice_measurements",
        "practice_interventions",
        "attempt_comparisons",
        "alembic_version",
    }.issubset(tables)
    evaluation_columns = {column["name"] for column in inspector.get_columns("practice_evaluations")}
    attempt_columns = {column["name"] for column in inspector.get_columns("practice_attempts")}
    assert {"workflow_route", "workflow_reason"}.issubset(attempt_columns)
    assert {
        "evidence_json",
        "abstention_reason",
        "input_quality",
        "evidence_status",
        "feedback_status",
    }.issubset(evaluation_columns)


def test_phase2_attempt_sequence_and_idempotency_are_unique(migrated_engine):
    with migrated_engine.begin() as connection:
        connection.execute(text("INSERT INTO practice_users (id, anonymous_device_id_hash) VALUES (1, 'device-hash')"))
        connection.execute(text("""
            INSERT INTO practice_sessions (id, owner_id, scenario, audience, goal, requested_duration_seconds, status)
            VALUES (1, 1, 'Explain a technical project', 'recruiter', 'be clear', 60, 'active')
        """))
        connection.execute(text("""
            INSERT INTO practice_attempts (session_id, sequence_number, idempotency_key, status, capture_duration_seconds)
            VALUES (1, 1, 'idem-1', 'pending', 60)
        """))

    with pytest.raises(IntegrityError):
        with migrated_engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO practice_attempts (session_id, sequence_number, idempotency_key, status, capture_duration_seconds)
                VALUES (1, 1, 'idem-2', 'pending', 60)
            """))

    with pytest.raises(IntegrityError):
        with migrated_engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO practice_attempts (session_id, sequence_number, idempotency_key, status, capture_duration_seconds)
                VALUES (1, 2, 'idem-1', 'pending', 60)
            """))


def test_phase2_constraints_reject_invalid_status_and_scores(migrated_engine):
    with migrated_engine.begin() as connection:
        connection.execute(text("INSERT INTO practice_users (id, anonymous_device_id_hash) VALUES (1, 'device-hash')"))

    with pytest.raises(IntegrityError):
        with migrated_engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO practice_sessions (owner_id, scenario, audience, goal, requested_duration_seconds, status)
                VALUES (1, 'Explain a technical project', 'recruiter', 'be clear', 60, 'unknown')
            """))

    with migrated_engine.begin() as connection:
        connection.execute(text("""
            INSERT INTO practice_sessions (id, owner_id, scenario, audience, goal, requested_duration_seconds, status)
            VALUES (1, 1, 'Explain a technical project', 'recruiter', 'be clear', 60, 'active')
        """))
        connection.execute(text("""
            INSERT INTO practice_attempts (id, session_id, sequence_number, idempotency_key, status, capture_duration_seconds)
            VALUES (1, 1, 1, 'idem-1', 'completed', 60)
        """))

    with pytest.raises(IntegrityError):
        with migrated_engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO practice_evaluations (
                    attempt_id, prompt_version, model_id, schema_version, rubric_version,
                    evaluator_status, input_quality, evidence_status, feedback_status,
                    clarity, structure, conciseness, audience_awareness,
                    strengths_json, weaknesses_json
                )
                VALUES (
                    1, 'evaluation-audio-v1', 'gemini-2.5-flash', 'attempt-response-v1',
                    'technical-explanation-v1', 'completed', 'usable', 'quote_verified',
                    'actionable', 11, 5, 5, 5, '[]', '[]'
                )
            """))

    with pytest.raises(IntegrityError):
        with migrated_engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO practice_attempts (
                    session_id, sequence_number, idempotency_key, status, capture_duration_seconds,
                    workflow_route, workflow_reason
                )
                VALUES (1, 2, 'idem-2', 'completed', 60, 'unknown_route', 'first_eligible_attempt')
            """))
