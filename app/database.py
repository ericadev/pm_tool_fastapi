import os
from urllib.parse import quote
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables (only works outside Docker; Docker uses env_file)
# This is a no-op in Docker but necessary for local development
load_dotenv()

def get_database_url():
    """Build database URL from environment variables."""
    db_user = os.getenv("DATABASE_USER", "pm_tool_user")
    db_password = os.getenv("DATABASE_PASSWORD", "your_secure_password")
    db_host = os.getenv("DATABASE_HOST", "localhost")
    db_port = os.getenv("DATABASE_PORT", "5432")
    db_name = os.getenv("DATABASE_NAME", "pm_tool")

    # URL encode the password to handle special characters
    encoded_password = quote(db_password, safe="")
    return f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
