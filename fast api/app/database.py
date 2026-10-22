from typing import Generator
from sqlalchemy import event
from sqlmodel import SQLModel, Session, create_engine
from app.config import settings
import app.models  # Ensures all models are registered in SQLModel metadata

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints and WAL mode in SQLite for reliability and concurrency."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database sessions."""
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """Create all database tables and seed baseline data if needed."""
    SQLModel.metadata.create_all(engine)
    from app.services.seed_service import seed_initial_data
    with Session(engine) as session:
        seed_initial_data(session)
