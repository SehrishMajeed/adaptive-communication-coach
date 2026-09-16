"""evaluation quality metadata

Revision ID: 20260916_0003
Revises: 20260916_0002
Create Date: 2026-09-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260916_0003"
down_revision: Union[str, Sequence[str], None] = "20260916_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("practice_evaluations", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("input_quality", sa.String(), nullable=False, server_default="usable"))
        batch_op.add_column(sa.Column("evidence_status", sa.String(), nullable=False, server_default="quote_verified"))
        batch_op.add_column(sa.Column("feedback_status", sa.String(), nullable=False, server_default="actionable"))
        batch_op.create_check_constraint(
            "ck_practice_evaluations_input_quality",
            "input_quality IN ('usable', 'limited', 'unusable')",
        )
        batch_op.create_check_constraint(
            "ck_practice_evaluations_evidence_status",
            "evidence_status IN ('quote_verified', 'insufficient_evidence', 'unavailable')",
        )
        batch_op.create_check_constraint(
            "ck_practice_evaluations_feedback_status",
            "feedback_status IN ('actionable', 'needs_retry', 'abstained')",
        )


def downgrade() -> None:
    with op.batch_alter_table("practice_evaluations", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_practice_evaluations_feedback_status", type_="check")
        batch_op.drop_constraint("ck_practice_evaluations_evidence_status", type_="check")
        batch_op.drop_constraint("ck_practice_evaluations_input_quality", type_="check")
        batch_op.drop_column("feedback_status")
        batch_op.drop_column("evidence_status")
        batch_op.drop_column("input_quality")
