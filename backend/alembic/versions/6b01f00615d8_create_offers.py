"""create offers

Revision ID: 6b01f00615d8
Revises: 
Create Date: 2025-12-18 20:46:37.675513

"""
from alembic import op
import sqlalchemy as sa

revision = "6b01f00615d8"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "offers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="DRAFT"),
        sa.Column("deleted", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_offers_id", "offers", ["id"])

def downgrade():
    op.drop_index("ix_offers_id", table_name="offers")
    op.drop_table("offers")
