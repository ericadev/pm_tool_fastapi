import os
from urllib.parse import quote
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get raw DATABASE_URL and parse it to handle special characters in password
_db_url = os.getenv("DATABASE_URL")
if _db_url and "@" in _db_url:
    # Extract parts before the @ symbol (user:password)
    auth_part, host_part = _db_url.rsplit("@", 1)
    scheme_auth = auth_part.split("://", 1)

    if len(scheme_auth) == 2:
        scheme, auth = scheme_auth
        # Extract username and password
        if ":" in auth:
            user, password = auth.split(":", 1)
            # URL encode the password to handle special characters
            encoded_password = quote(password, safe="")
            DATABASE_URL = f"{scheme}://{user}:{encoded_password}@{host_part}"
        else:
            DATABASE_URL = _db_url
    else:
        DATABASE_URL = _db_url
else:
    DATABASE_URL = _db_url

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
