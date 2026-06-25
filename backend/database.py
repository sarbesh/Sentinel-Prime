from sqlmodel import SQLModel, create_engine, Session, Session as SessionLocal
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////data/sentinel_prime.db")

connect_args = {"check_same_thread": False}
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=StaticPool,
)


def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for getting database session."""
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    """Context manager for database session."""
    with Session(engine) as session:
        yield session


SessionLocal = Session
