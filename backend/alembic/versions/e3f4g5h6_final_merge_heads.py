"""Merge migration to consolidate two Alembic heads

Revision ID: e3f4g5h6
Revises: d1e2f3a4, 6d1e9fb2eaca
Create Date: 2026-01-11 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3f4g5h6'
down_revision: Union[str, Sequence[str], None] = ('d1e2f3a4', '6d1e9fb2eaca')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
