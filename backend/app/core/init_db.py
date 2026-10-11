import os
from backend.app.core.database import Base, engine, check_db_connectivity
from backend.app.core.logging import app_logger
import backend.app.models  # Ensure all models are imported


def init_db():
    """Initializes the database schema by creating all tables if they do not exist."""
    app_logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        app_logger.info("Database tables initialized successfully.")
        return True
    except Exception as exc:
        app_logger.error(f"Failed to initialize database tables: {exc}")
        raise exc


if __name__ == "__main__":
    if check_db_connectivity():
        init_db()
        print("Database schema successfully generated!")
    else:
        print("Database connectivity check failed.")
