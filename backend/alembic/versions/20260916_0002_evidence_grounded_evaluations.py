"""evidence grounded evaluations

Revision ID: 20260916_0002
Revises: 20260916_0001
Create Date: 2026-09-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260916_0002"
down_revision: Union[str, Sequence[str], None] = "20260916_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("practice_evaluations", sa.Column("evidence_json", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("practice_evaluations", sa.Column("abstention_reason", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("practice_evaluations", "abstention_reason")
    op.drop_column("practice_evaluations", "evidence_json")
