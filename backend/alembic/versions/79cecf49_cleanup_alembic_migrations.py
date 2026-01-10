"""cleanup alembic migrations - merge heads and initialize JSON fields

Revision ID: 79cecf49
Revises: f454a6e34948, e511178ce7b0
Create Date: 2026-01-10 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79cecf49'
down_revision: Union[str, Sequence[str], None] = ('f454a6e34948', 'e511178ce7b0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Initialize NULL JSON columns with empty arrays."""
    # Initialize NULL values to empty JSON arrays to fix 422 error
    op.execute(
        """
        UPDATE offers
        SET required_skills = '[]'::json
        WHERE required_skills IS NULL;
        """
    )
    op.execute(
        """
        UPDATE offers
        SET nice_to_have_skills = '[]'::json
        WHERE nice_to_have_skills IS NULL;
        """
    )
    op.execute(
        """
        UPDATE offers
        SET required_education = '[]'::json
        WHERE required_education IS NULL;
        """
    )
    op.execute(
        """
        UPDATE offers
        SET required_languages = '[]'::json
        WHERE required_languages IS NULL;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
