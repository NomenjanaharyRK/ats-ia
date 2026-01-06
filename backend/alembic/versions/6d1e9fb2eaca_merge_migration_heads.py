"""Merge migration heads

Revision ID: 6d1e9fb2eaca
Revises: 630f341f8e5f, b2c4d5e6f7a8
Create Date: 2026-01-03 22:42:51.373400

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d1e9fb2eaca'
down_revision: Union[str, Sequence[str], None] = ('630f341f8e5f', 'b2c4d5e6f7a8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
