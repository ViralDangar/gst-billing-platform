from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import sys
import os

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "app")))

from app.core.database import Base
from app.core.config import settings

# Import ALL models so Alembic can detect them
from app.identity_service import models as identity_models
from app.master_data_service import models as master_models
from app.billing_service import models as billing_models
from app.tax_engine_service import models as tax_models
from app.accounting_service import models as accounting_models

# Alembic Config
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        {
            "sqlalchemy.url": settings.database_url
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
