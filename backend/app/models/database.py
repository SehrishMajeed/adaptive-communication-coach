import os
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import CreateColumn

raw_db_url = os.environ.get("DATABASE_URL", "").strip()

if not raw_db_url:
    # Fallback to local SQLite if no DATABASE_URL is provided
    SQLALCHEMY_DATABASE_URL = "sqlite:///./adaptive_coach.db"
else:
    # Normalize legacy Render/Heroku postgres:// to postgresql://
    if raw_db_url.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)
    else:
        SQLALCHEMY_DATABASE_URL = raw_db_url

    # Fail fast on obviously invalid configurations
    if not SQLALCHEMY_DATABASE_URL.startswith(("postgresql://", "sqlite:///")):
        raise ValueError("Invalid DATABASE_URL. Must start with postgres://, postgresql://, or sqlite:///")

# Configure engine arguments based on dialect
engine_kwargs = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # For robust hosted connections
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    
    # Rolling averages
    avg_clarity = Column(Float, default=0.0)
    avg_structure = Column(Float, default=0.0)
    avg_conciseness = Column(Float, default=0.0)
    avg_audience_awareness = Column(Float, default=0.0)
    
    # JSON lists of strings
    recurring_strengths = Column(JSON, default=list)
    recurring_weaknesses = Column(JSON, default=list)
    current_focus_area = Column(String, nullable=True)
    
    total_sessions = Column(Integer, default=0)
    
class CoachingSession(Base):
    __tablename__ = "coaching_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    scenario = Column(String)

class CoachingAttempt(Base):
    __tablename__ = "coaching_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    attempt_number = Column(Integer)
    transcript = Column(String)
    duration_seconds = Column(Float)
    
    # Metrics
    word_count = Column(Integer, nullable=True)
    duration_source = Column(String, default="pcm_samples")
    wpm = Column(Float, nullable=True)
    filler_words_count = Column(Integer, default=0)
    filler_words_list = Column(JSON, default=list)
    
    # Evaluation
    clarity = Column(Float, nullable=True)
    structure = Column(Float, nullable=True)
    conciseness = Column(Float, nullable=True)
    audience_awareness = Column(Float, nullable=True)
    
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    focus_area = Column(String, nullable=True)


class PracticeUser(Base):
    __tablename__ = "practice_users"

    id = Column(Integer, primary_key=True, index=True)
    anonymous_device_id_hash = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("practice_users.id"), nullable=False, index=True)
    scenario = Column(String, nullable=False)
    audience = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    requested_duration_seconds = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("requested_duration_seconds BETWEEN 1 AND 300", name="ck_practice_sessions_duration_bounds"),
        CheckConstraint("status IN ('active', 'completed', 'abandoned')", name="ck_practice_sessions_status"),
    )


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id"), nullable=False, index=True)
    sequence_number = Column(Integer, nullable=False)
    idempotency_key = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    capture_duration_seconds = Column(Float, nullable=False)
    media_duration_seconds = Column(Float, nullable=True)
    transcript = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    failure_code = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("session_id", "sequence_number", name="uq_practice_attempts_session_sequence"),
        UniqueConstraint("session_id", "idempotency_key", name="uq_practice_attempts_session_idempotency"),
        CheckConstraint("sequence_number >= 1", name="ck_practice_attempts_sequence_positive"),
        CheckConstraint("capture_duration_seconds BETWEEN 1 AND 300", name="ck_practice_attempts_capture_duration_bounds"),
        CheckConstraint("media_duration_seconds IS NULL OR media_duration_seconds BETWEEN 1 AND 305", name="ck_practice_attempts_media_duration_bounds"),
        CheckConstraint("status IN ('pending', 'processing', 'completed', 'abstained', 'invalid', 'failed')", name="ck_practice_attempts_status"),
    )


class PracticeEvaluation(Base):
    __tablename__ = "practice_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("practice_attempts.id"), nullable=False, unique=True, index=True)
    prompt_version = Column(String, nullable=False)
    model_id = Column(String, nullable=False)
    schema_version = Column(String, nullable=False)
    rubric_version = Column(String, nullable=False)
    evaluator_status = Column(String, nullable=False)
    input_quality = Column(String, nullable=False)
    evidence_status = Column(String, nullable=False)
    feedback_status = Column(String, nullable=False)
    clarity = Column(Float, nullable=True)
    structure = Column(Float, nullable=True)
    conciseness = Column(Float, nullable=True)
    audience_awareness = Column(Float, nullable=True)
    strengths_json = Column(JSON, nullable=False, default=list)
    weaknesses_json = Column(JSON, nullable=False, default=list)
    recommended_focus = Column(String, nullable=True)
    evidence_json = Column(JSON, nullable=False, default=list)
    abstention_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("evaluator_status IN ('completed', 'abstained', 'invalid')", name="ck_practice_evaluations_status"),
        CheckConstraint("input_quality IN ('usable', 'limited', 'unusable')", name="ck_practice_evaluations_input_quality"),
        CheckConstraint("evidence_status IN ('quote_verified', 'insufficient_evidence', 'unavailable')", name="ck_practice_evaluations_evidence_status"),
        CheckConstraint("feedback_status IN ('actionable', 'needs_retry', 'abstained')", name="ck_practice_evaluations_feedback_status"),
        CheckConstraint("clarity IS NULL OR clarity BETWEEN 0 AND 10", name="ck_practice_evaluations_clarity_bounds"),
        CheckConstraint("structure IS NULL OR structure BETWEEN 0 AND 10", name="ck_practice_evaluations_structure_bounds"),
        CheckConstraint("conciseness IS NULL OR conciseness BETWEEN 0 AND 10", name="ck_practice_evaluations_conciseness_bounds"),
        CheckConstraint("audience_awareness IS NULL OR audience_awareness BETWEEN 0 AND 10", name="ck_practice_evaluations_audience_bounds"),
        CheckConstraint("recommended_focus IS NULL OR recommended_focus IN ('clarity', 'structure', 'conciseness', 'audience_awareness')", name="ck_practice_evaluations_focus"),
    )


class PracticeMeasurement(Base):
    __tablename__ = "practice_measurements"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("practice_attempts.id"), nullable=False, unique=True, index=True)
    metric_version = Column(String, nullable=False)
    duration_source = Column(String, nullable=False)
    word_count = Column(Integer, nullable=False)
    wpm = Column(Float, nullable=False)
    total_fillers = Column(Integer, nullable=False)
    filler_words_json = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("word_count >= 0", name="ck_practice_measurements_word_count"),
        CheckConstraint("wpm >= 0", name="ck_practice_measurements_wpm"),
        CheckConstraint("total_fillers >= 0", name="ck_practice_measurements_total_fillers"),
        CheckConstraint("duration_source IN ('pcm_samples')", name="ck_practice_measurements_duration_source"),
    )


class PracticeIntervention(Base):
    __tablename__ = "practice_interventions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id"), nullable=False, index=True)
    source_attempt_id = Column(Integer, ForeignKey("practice_attempts.id"), nullable=False, index=True)
    target_skill = Column(String, nullable=False)
    drill_version = Column(String, nullable=False)
    drill_text = Column(String, nullable=False)
    status = Column(String, nullable=False, default="assigned")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("target_skill IN ('clarity', 'structure', 'conciseness', 'audience_awareness')", name="ck_practice_interventions_target_skill"),
        CheckConstraint("status IN ('assigned', 'completed', 'abandoned')", name="ck_practice_interventions_status"),
    )


class AttemptComparison(Base):
    __tablename__ = "attempt_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id"), nullable=False, index=True)
    baseline_attempt_id = Column(Integer, ForeignKey("practice_attempts.id"), nullable=False, index=True)
    retry_attempt_id = Column(Integer, ForeignKey("practice_attempts.id"), nullable=False, unique=True, index=True)
    intervention_id = Column(Integer, ForeignKey("practice_interventions.id"), nullable=False, index=True)
    target_skill = Column(String, nullable=False)
    comparability_status = Column(String, nullable=False)
    verdict = Column(String, nullable=False)
    deltas_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("baseline_attempt_id != retry_attempt_id", name="ck_attempt_comparisons_distinct_attempts"),
        CheckConstraint("target_skill IN ('clarity', 'structure', 'conciseness', 'audience_awareness')", name="ck_attempt_comparisons_target_skill"),
        CheckConstraint("comparability_status IN ('comparable', 'insufficient_evidence', 'context_mismatch', 'rubric_mismatch')", name="ck_attempt_comparisons_status"),
        CheckConstraint("verdict IN ('improved', 'no_clear_change', 'regressed', 'insufficient_evidence')", name="ck_attempt_comparisons_verdict"),
    )


def ensure_attempt_measurement_columns(bind):
    try:
        inspector = inspect(bind)
    except NoInspectionAvailable:
        return

    existing = {column["name"] for column in inspector.get_columns("coaching_attempts")}
    required = [
        Column("word_count", Integer, nullable=True),
        Column("duration_source", String, nullable=True),
        Column("filler_words_list", JSON, nullable=True),
    ]
    missing = [column for column in required if column.name not in existing]
    if not missing:
        return

    with bind.begin() as connection:
        for column in missing:
            compiled = CreateColumn(column).compile(dialect=bind.dialect)
            connection.execute(text(f"ALTER TABLE coaching_attempts ADD COLUMN {compiled}"))


if os.getenv("DB_AUTO_CREATE", "true").lower() not in {"0", "false", "no"}:
    # Create tables safely for the local prototype path. Alembic owns release migrations.
    Base.metadata.create_all(bind=engine)
    ensure_attempt_measurement_columns(engine)
