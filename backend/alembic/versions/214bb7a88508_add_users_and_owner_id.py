"""add users and owner_id

Revision ID: 214bb7a88508
Revises: 6b01f00615d8
Create Date: 2025-12-18 21:02:41.912867

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "214bb7a88508"
down_revision = "6b01f00615d8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="RECRUITER"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.add_column("offers", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_offers_owner", "offers", "users", ["owner_id"], ["id"])

def downgrade():
    op.drop_constraint("fk_offers_owner", "offers", type_="foreignkey")
    op.drop_column("offers", "owner_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
