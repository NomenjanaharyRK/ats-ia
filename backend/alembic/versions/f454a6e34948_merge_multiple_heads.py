"""merge multiple heads

Revision ID: f454a6e34948
Revises: aa96496def30, e511178ce7b0
Create Date: 2026-01-10 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f454a6e34948'
down_revision: Union[str, Sequence[str], None] = ('aa96496def30', 'e511178ce7b0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
