"""initialize offer JSON fields

Revision ID: e511178ce7b0
Revises: 1d71ee57ab12
Create Date: 2026-01-10 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e511178ce7b0'
down_revision: Union[str, Sequence[str], None] = '1d71ee57ab12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Initialize NULL JSON columns with empty arrays."""
    # Update NULL values to empty JSON arrays
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
