"""Initial schema placeholder.

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-18

Domain tables (models, runtimes, metrics, …) are added in Phase 1.
This revision exists so `alembic upgrade head` is a no-op that still
proves the migration pipeline on SQLite and PostgreSQL.
"""

from typing import Sequence, Union

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
