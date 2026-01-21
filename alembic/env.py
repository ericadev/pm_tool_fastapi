import os
from logging.config import fileConfig
from urllib.parse import quote

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv

from alembic import context

# Load environment variables from .env file
load_dotenv()


def get_database_url():
    """Build database URL from environment variables."""
    # First try DATABASE_URL if it exists
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        if "@" in db_url:
            # Extract parts before the @ symbol (user:password)
            auth_part, host_part = db_url.rsplit("@", 1)
            scheme_auth = auth_part.split("://", 1)

            if len(scheme_auth) == 2:
                scheme, auth = scheme_auth
                # Extract username and password
                if ":" in auth:
                    user, password = auth.split(":", 1)
                    # URL encode the password to handle special characters
                    encoded_password = quote(password, safe="")
                    return f"{scheme}://{user}:{encoded_password}@{host_part}"
        return db_url

    # Otherwise build from individual variables
    db_user = os.getenv("DATABASE_USER", "pm_tool_user")
    db_password = os.getenv("DATABASE_PASSWORD", "your_secure_password")
    db_host = os.getenv("DATABASE_HOST", "localhost")
    db_port = os.getenv("DATABASE_PORT", "5432")
    db_name = os.getenv("DATABASE_NAME", "pm_tool")

    # URL encode the password to handle special characters
    encoded_password = quote(db_password, safe="")
    return f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.database import Base
from app.models import *  # noqa

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = get_database_url()
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
