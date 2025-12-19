import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# IMPORTANT: importer Base + modèles pour que Base.metadata connaisse toutes les tables
from app.db.base import Base
from app.models.offer import Offer  # noqa: F401
from app.models.application import Application  # noqa: F401
from app.models.candidate import Candidate  # noqa: F401
from app.models.cv_text import CVText  # noqa: F401

# Alembic Config
config = context.config

# Charger l'URL DB depuis l'env
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL is not set")

config.set_main_option("sqlalchemy.url", db_url)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Autogenerate: donner la metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
