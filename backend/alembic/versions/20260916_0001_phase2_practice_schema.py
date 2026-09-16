"""phase2 practice schema

Revision ID: 20260916_0001
Revises:
Create Date: 2026-09-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260916_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "practice_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anonymous_device_id_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("anonymous_device_id_hash"),
    )
    op.create_index(op.f("ix_practice_users_id"), "practice_users", ["id"], unique=False)
    op.create_index(op.f("ix_practice_users_anonymous_device_id_hash"), "practice_users", ["anonymous_device_id_hash"], unique=False)

    op.create_table(
        "practice_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("scenario", sa.String(), nullable=False),
        sa.Column("audience", sa.String(), nullable=False),
        sa.Column("goal", sa.String(), nullable=False),
        sa.Column("requested_duration_seconds", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("requested_duration_seconds BETWEEN 1 AND 300", name="ck_practice_sessions_duration_bounds"),
        sa.CheckConstraint("status IN ('active', 'completed', 'abandoned')", name="ck_practice_sessions_status"),
        sa.ForeignKeyConstraint(["owner_id"], ["practice_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_practice_sessions_id"), "practice_sessions", ["id"], unique=False)
    op.create_index(op.f("ix_practice_sessions_owner_id"), "practice_sessions", ["owner_id"], unique=False)

    op.create_table(
        "practice_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("capture_duration_seconds", sa.Float(), nullable=False),
        sa.Column("media_duration_seconds", sa.Float(), nullable=True),
        sa.Column("transcript", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_code", sa.String(), nullable=True),
        sa.CheckConstraint("capture_duration_seconds BETWEEN 1 AND 300", name="ck_practice_attempts_capture_duration_bounds"),
        sa.CheckConstraint("media_duration_seconds IS NULL OR media_duration_seconds BETWEEN 1 AND 305", name="ck_practice_attempts_media_duration_bounds"),
        sa.CheckConstraint("sequence_number >= 1", name="ck_practice_attempts_sequence_positive"),
        sa.CheckConstraint("status IN ('pending', 'processing', 'completed', 'abstained', 'invalid', 'failed')", name="ck_practice_attempts_status"),
        sa.ForeignKeyConstraint(["session_id"], ["practice_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "idempotency_key", name="uq_practice_attempts_session_idempotency"),
        sa.UniqueConstraint("session_id", "sequence_number", name="uq_practice_attempts_session_sequence"),
    )
    op.create_index(op.f("ix_practice_attempts_id"), "practice_attempts", ["id"], unique=False)
    op.create_index(op.f("ix_practice_attempts_session_id"), "practice_attempts", ["session_id"], unique=False)

    op.create_table(
        "practice_evaluations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("prompt_version", sa.String(), nullable=False),
        sa.Column("model_id", sa.String(), nullable=False),
        sa.Column("schema_version", sa.String(), nullable=False),
        sa.Column("rubric_version", sa.String(), nullable=False),
        sa.Column("evaluator_status", sa.String(), nullable=False),
        sa.Column("clarity", sa.Float(), nullable=True),
        sa.Column("structure", sa.Float(), nullable=True),
        sa.Column("conciseness", sa.Float(), nullable=True),
        sa.Column("audience_awareness", sa.Float(), nullable=True),
        sa.Column("strengths_json", sa.JSON(), nullable=False),
        sa.Column("weaknesses_json", sa.JSON(), nullable=False),
        sa.Column("recommended_focus", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("audience_awareness IS NULL OR audience_awareness BETWEEN 0 AND 10", name="ck_practice_evaluations_audience_bounds"),
        sa.CheckConstraint("clarity IS NULL OR clarity BETWEEN 0 AND 10", name="ck_practice_evaluations_clarity_bounds"),
        sa.CheckConstraint("conciseness IS NULL OR conciseness BETWEEN 0 AND 10", name="ck_practice_evaluations_conciseness_bounds"),
        sa.CheckConstraint("evaluator_status IN ('completed', 'abstained', 'invalid')", name="ck_practice_evaluations_status"),
        sa.CheckConstraint("recommended_focus IS NULL OR recommended_focus IN ('clarity', 'structure', 'conciseness', 'audience_awareness')", name="ck_practice_evaluations_focus"),
        sa.CheckConstraint("structure IS NULL OR structure BETWEEN 0 AND 10", name="ck_practice_evaluations_structure_bounds"),
        sa.ForeignKeyConstraint(["attempt_id"], ["practice_attempts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attempt_id"),
    )
    op.create_index(op.f("ix_practice_evaluations_attempt_id"), "practice_evaluations", ["attempt_id"], unique=False)
    op.create_index(op.f("ix_practice_evaluations_id"), "practice_evaluations", ["id"], unique=False)

    op.create_table(
        "practice_measurements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("metric_version", sa.String(), nullable=False),
        sa.Column("duration_source", sa.String(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("wpm", sa.Float(), nullable=False),
        sa.Column("total_fillers", sa.Integer(), nullable=False),
        sa.Column("filler_words_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("duration_source IN ('pcm_samples')", name="ck_practice_measurements_duration_source"),
        sa.CheckConstraint("total_fillers >= 0", name="ck_practice_measurements_total_fillers"),
        sa.CheckConstraint("word_count >= 0", name="ck_practice_measurements_word_count"),
        sa.CheckConstraint("wpm >= 0", name="ck_practice_measurements_wpm"),
        sa.ForeignKeyConstraint(["attempt_id"], ["practice_attempts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attempt_id"),
    )
    op.create_index(op.f("ix_practice_measurements_attempt_id"), "practice_measurements", ["attempt_id"], unique=False)
    op.create_index(op.f("ix_practice_measurements_id"), "practice_measurements", ["id"], unique=False)

    op.create_table(
        "practice_interventions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("source_attempt_id", sa.Integer(), nullable=False),
        sa.Column("target_skill", sa.String(), nullable=False),
        sa.Column("drill_version", sa.String(), nullable=False),
        sa.Column("drill_text", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("status IN ('assigned', 'completed', 'abandoned')", name="ck_practice_interventions_status"),
        sa.CheckConstraint("target_skill IN ('clarity', 'structure', 'conciseness', 'audience_awareness')", name="ck_practice_interventions_target_skill"),
        sa.ForeignKeyConstraint(["session_id"], ["practice_sessions.id"]),
        sa.ForeignKeyConstraint(["source_attempt_id"], ["practice_attempts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_practice_interventions_id"), "practice_interventions", ["id"], unique=False)
    op.create_index(op.f("ix_practice_interventions_session_id"), "practice_interventions", ["session_id"], unique=False)
    op.create_index(op.f("ix_practice_interventions_source_attempt_id"), "practice_interventions", ["source_attempt_id"], unique=False)

    op.create_table(
        "attempt_comparisons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("baseline_attempt_id", sa.Integer(), nullable=False),
        sa.Column("retry_attempt_id", sa.Integer(), nullable=False),
        sa.Column("intervention_id", sa.Integer(), nullable=False),
        sa.Column("target_skill", sa.String(), nullable=False),
        sa.Column("comparability_status", sa.String(), nullable=False),
        sa.Column("verdict", sa.String(), nullable=False),
        sa.Column("deltas_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("baseline_attempt_id != retry_attempt_id", name="ck_attempt_comparisons_distinct_attempts"),
        sa.CheckConstraint("comparability_status IN ('comparable', 'insufficient_evidence', 'context_mismatch', 'rubric_mismatch')", name="ck_attempt_comparisons_status"),
        sa.CheckConstraint("target_skill IN ('clarity', 'structure', 'conciseness', 'audience_awareness')", name="ck_attempt_comparisons_target_skill"),
        sa.CheckConstraint("verdict IN ('improved', 'no_clear_change', 'regressed', 'insufficient_evidence')", name="ck_attempt_comparisons_verdict"),
        sa.ForeignKeyConstraint(["baseline_attempt_id"], ["practice_attempts.id"]),
        sa.ForeignKeyConstraint(["intervention_id"], ["practice_interventions.id"]),
        sa.ForeignKeyConstraint(["retry_attempt_id"], ["practice_attempts.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["practice_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("retry_attempt_id"),
    )
    op.create_index(op.f("ix_attempt_comparisons_baseline_attempt_id"), "attempt_comparisons", ["baseline_attempt_id"], unique=False)
    op.create_index(op.f("ix_attempt_comparisons_id"), "attempt_comparisons", ["id"], unique=False)
    op.create_index(op.f("ix_attempt_comparisons_intervention_id"), "attempt_comparisons", ["intervention_id"], unique=False)
    op.create_index(op.f("ix_attempt_comparisons_retry_attempt_id"), "attempt_comparisons", ["retry_attempt_id"], unique=False)
    op.create_index(op.f("ix_attempt_comparisons_session_id"), "attempt_comparisons", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_attempt_comparisons_session_id"), table_name="attempt_comparisons")
    op.drop_index(op.f("ix_attempt_comparisons_retry_attempt_id"), table_name="attempt_comparisons")
    op.drop_index(op.f("ix_attempt_comparisons_intervention_id"), table_name="attempt_comparisons")
    op.drop_index(op.f("ix_attempt_comparisons_id"), table_name="attempt_comparisons")
    op.drop_index(op.f("ix_attempt_comparisons_baseline_attempt_id"), table_name="attempt_comparisons")
    op.drop_table("attempt_comparisons")
    op.drop_index(op.f("ix_practice_interventions_source_attempt_id"), table_name="practice_interventions")
    op.drop_index(op.f("ix_practice_interventions_session_id"), table_name="practice_interventions")
    op.drop_index(op.f("ix_practice_interventions_id"), table_name="practice_interventions")
    op.drop_table("practice_interventions")
    op.drop_index(op.f("ix_practice_measurements_id"), table_name="practice_measurements")
    op.drop_index(op.f("ix_practice_measurements_attempt_id"), table_name="practice_measurements")
    op.drop_table("practice_measurements")
    op.drop_index(op.f("ix_practice_evaluations_id"), table_name="practice_evaluations")
    op.drop_index(op.f("ix_practice_evaluations_attempt_id"), table_name="practice_evaluations")
    op.drop_table("practice_evaluations")
    op.drop_index(op.f("ix_practice_attempts_session_id"), table_name="practice_attempts")
    op.drop_index(op.f("ix_practice_attempts_id"), table_name="practice_attempts")
    op.drop_table("practice_attempts")
    op.drop_index(op.f("ix_practice_sessions_owner_id"), table_name="practice_sessions")
    op.drop_index(op.f("ix_practice_sessions_id"), table_name="practice_sessions")
    op.drop_table("practice_sessions")
    op.drop_index(op.f("ix_practice_users_anonymous_device_id_hash"), table_name="practice_users")
    op.drop_index(op.f("ix_practice_users_id"), table_name="practice_users")
    op.drop_table("practice_users")
