"""add indexes applications offer candidate

Revision ID: a1b2c3d4e5f6
Revises: 70a7163e0023
Create Date: 2026-01-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '70a7163e0023'
branch_labels = None
depends_on = None


def upgrade():
    # Indexes pour améliorer performances des requêtes
    op.create_index('idx_applications_offer_id', 'applications', ['offer_id'])
    op.create_index('idx_applications_candidate_id', 'applications', ['candidate_id'])
    op.create_index('idx_cv_texts_application_id', 'cv_texts', ['application_id'])


def downgrade():
    op.drop_index('idx_cv_texts_application_id', 'cv_texts')
    op.drop_index('idx_applications_candidate_id', 'applications')
    op.drop_index('idx_applications_offer_id', 'applications')
