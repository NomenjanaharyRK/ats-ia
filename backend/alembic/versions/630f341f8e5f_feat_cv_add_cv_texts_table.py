"""feat(cv): add cv_texts table

Revision ID: 630f341f8e5f
Revises: 70a7163e0023
Create Date: 2025-12-19 11:31:04.571857
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "630f341f8e5f"
down_revision: Union[str, Sequence[str], None] = "70a7163e0023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

USERROLE_ENUM = postgresql.ENUM("ADMIN", "RECRUITER", name="userrole")


def upgrade() -> None:
    """Upgrade schema."""

    # 1) Enum type postgres (obligatoire avant alter column)
    USERROLE_ENUM.create(op.get_bind(), checkfirst=True)

    # 2) Table cv_texts
    op.create_table(
        "cv_texts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column("quality_score", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cv_texts_application_id"), "cv_texts", ["application_id"], unique=True)
    op.create_index(op.f("ix_cv_texts_id"), "cv_texts", ["id"], unique=False)

    # 3) users.role : DROP DEFAULT -> ALTER TYPE -> SET DEFAULT
    #    (sinon: "default for column cannot be cast automatically to type userrole")
    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(length=20),
        server_default=None,
        existing_nullable=False,
    )

    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(length=20),
        type_=USERROLE_ENUM,
        existing_nullable=False,
        postgresql_using="role::userrole",
    )

    op.alter_column(
        "users",
        "role",
        existing_type=USERROLE_ENUM,
        server_default=sa.text("'RECRUITER'::userrole"),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Revenir de enum -> varchar: DROP DEFAULT -> ALTER TYPE -> SET DEFAULT
    op.alter_column(
        "users",
        "role",
        existing_type=USERROLE_ENUM,
        server_default=None,
        existing_nullable=False,
    )

    op.alter_column(
        "users",
        "role",
        existing_type=USERROLE_ENUM,
        type_=sa.VARCHAR(length=20),
        existing_nullable=False,
        postgresql_using="role::text",
    )

    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(length=20),
        server_default=sa.text("'RECRUITER'::character varying"),
        existing_nullable=False,
    )

    op.drop_index(op.f("ix_cv_texts_id"), table_name="cv_texts")
    op.drop_index(op.f("ix_cv_texts_application_id"), table_name="cv_texts")
    op.drop_table("cv_texts")

    USERROLE_ENUM.drop(op.get_bind(), checkfirst=True)
