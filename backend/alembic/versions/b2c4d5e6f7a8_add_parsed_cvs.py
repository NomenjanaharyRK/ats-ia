"""Add parsed_cvs table for Sprint 5

Revision ID: b2c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-01-03 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2c4d5e6f7a8'
down_revision = 'a1b2c3d4e5f6'  # Update this with the latest migration ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create parsed_cvs table
    op.create_table(
        'parsed_cvs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        
        # Contact information
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        
        # Extracted data (JSON arrays)
        sa.Column('skills', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('education', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('languages', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        
        # Experience
        sa.Column('experience_years', sa.Integer(), nullable=True),
        
        # Scoring fields
        sa.Column('matching_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('skills_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('experience_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('education_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('language_score', sa.Float(), nullable=True, server_default='0.0'),
        
        # Scoring details (JSON object)
        sa.Column('scoring_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('application_id', name='uq_parsed_cvs_application_id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_parsed_cvs_id', 'parsed_cvs', ['id'])
    op.create_index('ix_parsed_cvs_application_id', 'parsed_cvs', ['application_id'])
    op.create_index('ix_parsed_cvs_full_name', 'parsed_cvs', ['full_name'])
    op.create_index('ix_parsed_cvs_matching_score', 'parsed_cvs', ['matching_score'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_parsed_cvs_matching_score', table_name='parsed_cvs')
    op.drop_index('ix_parsed_cvs_full_name', table_name='parsed_cvs')
    op.drop_index('ix_parsed_cvs_application_id', table_name='parsed_cvs')
    op.drop_index('ix_parsed_cvs_id', table_name='parsed_cvs')
    
    # Drop table
    op.drop_table('parsed_cvs')
