from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.bot.database.base import Base

engine = None
SessionLocal = None


def create_db(database_url: str) -> None:
    global engine, SessionLocal
    engine = create_engine(database_url, echo=False)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_manager() -> Iterator[Session]:
    if SessionLocal is None:
        raise RuntimeError("Database is not initialized. Call create_db() before using sessions.")

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
