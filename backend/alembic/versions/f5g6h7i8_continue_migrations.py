"""Transition migration to continue after final merge

Revision ID: f5g6h7i8
Revises: e3f4g5h6
Create Date: 2026-01-11 09:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5g6h7i8'
down_revision: Union[str, Sequence[str], None] = 'e3f4g5h6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
