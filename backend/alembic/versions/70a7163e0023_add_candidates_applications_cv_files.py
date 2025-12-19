"""add candidates applications cv_files

Revision ID: 70a7163e0023
Revises: 214bb7a88508
Create Date: 2025-12-18 23:58:38.508177

"""
from alembic import op
import sqlalchemy as sa

# récupère l'ID généré par Alembic
revision = "70a7163e0023"
down_revision = "214bb7a88508"  # ou la dernière révision appliquée
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_candidates_id", "candidates", ["id"])

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("offer_id", sa.Integer, sa.ForeignKey("offers.id"), nullable=False),
        sa.Column("candidate_id", sa.Integer, sa.ForeignKey("candidates.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_applications_id", "applications", ["id"])

    op.create_table(
        "cv_files",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("application_id", sa.Integer, sa.ForeignKey("applications.id"), nullable=False),
        sa.Column("storage_path", sa.String, nullable=False),
        sa.Column("original_filename", sa.String, nullable=False),
        sa.Column("mime_type", sa.String, nullable=False),
        sa.Column("size_bytes", sa.Integer, nullable=False),
        sa.Column("sha256", sa.String, nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="UPLOADED"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_cv_files_id", "cv_files", ["id"])
    op.create_index("ix_cv_files_sha256", "cv_files", ["sha256"])


def downgrade():
    op.drop_index("ix_cv_files_sha256", table_name="cv_files")
    op.drop_index("ix_cv_files_id", table_name="cv_files")
    op.drop_table("cv_files")

    op.drop_index("ix_applications_id", table_name="applications")
    op.drop_table("applications")

    op.drop_index("ix_candidates_id", table_name="candidates")
    op.drop_table("candidates")
