"""persist attempt workflow route

Revision ID: 20260916_0004
Revises: 20260916_0003
Create Date: 2026-09-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260916_0004"
down_revision: Union[str, Sequence[str], None] = "20260916_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("practice_attempts", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("workflow_route", sa.String(), nullable=False, server_default="baseline_blocked"))
        batch_op.add_column(sa.Column("workflow_reason", sa.String(), nullable=False, server_default="first_attempt_not_eligible"))
        batch_op.create_check_constraint(
            "ck_practice_attempts_workflow_route",
            "workflow_route IN ('abstained', 'baseline', 'baseline_blocked', 'retry_comparable', 'retry_blocked', 'retry_without_baseline')",
        )
        batch_op.create_check_constraint(
            "ck_practice_attempts_workflow_reason",
            "workflow_reason IN ('abstained_evaluation', 'first_eligible_attempt', 'first_attempt_not_eligible', 'retry_eligible_with_baseline', 'retry_not_eligible', 'missing_prior_intervention', 'baseline_not_eligible')",
        )


def downgrade() -> None:
    with op.batch_alter_table("practice_attempts", recreate="always") as batch_op:
        batch_op.drop_constraint("ck_practice_attempts_workflow_reason", type_="check")
        batch_op.drop_constraint("ck_practice_attempts_workflow_route", type_="check")
        batch_op.drop_column("workflow_reason")
        batch_op.drop_column("workflow_route")
