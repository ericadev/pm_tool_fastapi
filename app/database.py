import os
import logging
from urllib.parse import quote
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables (only works outside Docker; Docker uses env_file)
# This is a no-op in Docker but necessary for local development
load_dotenv()

def _format_host_for_url(host: str | None) -> str | None:
    """Format host for use in PostgreSQL URL, handling IPv6 addresses."""
    if host is None:
        return None
    # IPv6 addresses need to be wrapped in brackets
    if ":" in host and not host.startswith("["):
        return f"[{host}]"
    return host


def get_database_url():
    """Build database URL from environment variables."""
    # Try DATABASE_URL first (Railway, other platforms)
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print(f"DEBUG: Using DATABASE_URL from environment")
        return db_url

    # Try PGHOST (Railway PostgreSQL plugin format)
    if os.getenv("PGHOST"):
        print(f"DEBUG: Using PGHOST/PGPORT format")
        db_user = os.getenv("PGUSER", "postgres")
        db_password = os.getenv("PGPASSWORD", "")
        db_host = os.getenv("PGHOST")
        db_port = os.getenv("PGPORT", "5432")
        db_name = os.getenv("PGDATABASE", "postgres")
        encoded_password = quote(db_password, safe="")
        formatted_host = _format_host_for_url(db_host)
        # Railway requires SSL for remote connections
        return f"postgresql://{db_user}:{encoded_password}@{formatted_host}:{db_port}/{db_name}?sslmode=require"

    # Fall back to custom variables (local development)
    print(f"DEBUG: Using custom DATABASE_* variables")
    db_user = os.getenv("DATABASE_USER", "pm_tool_user")
    db_password = os.getenv("DATABASE_PASSWORD", "your_secure_password")
    db_host = os.getenv("DATABASE_HOST", "localhost")
    db_port = os.getenv("DATABASE_PORT", "5432")
    db_name = os.getenv("DATABASE_NAME", "pm_tool")

    # URL encode the password to handle special characters
    encoded_password = quote(db_password, safe="")
    formatted_host = _format_host_for_url(db_host)
    return f"postgresql://{db_user}:{encoded_password}@{formatted_host}:{db_port}/{db_name}"

DATABASE_URL = get_database_url()
if DATABASE_URL:
    logger.info(f"Database URL configured: {DATABASE_URL[:60]}...")
else:
    logger.warning("No DATABASE_URL configured!")

try:
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
