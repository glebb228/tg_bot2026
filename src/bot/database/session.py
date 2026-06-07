from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from src.bot.database.base import Base
from src.bot.services.learning import seed_learning_content

engine = None
SessionLocal = None


def create_db(database_url: str) -> None:
    global engine, SessionLocal
    engine = create_engine(database_url, echo=False, pool_pre_ping=True)
    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)
    migrate_schema()
    with session_manager() as session:
        seed_learning_content(session)


def migrate_schema() -> None:
    if engine is None:
        return

    inspector = inspect(engine)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    word_set_columns = {column["name"] for column in inspector.get_columns("word_sets")}
    alter_statements = []

    if "current_language" not in user_columns:
        alter_statements.append(
            "ALTER TABLE users ADD COLUMN current_language VARCHAR(50) DEFAULT 'English'"
        )
    if "level" not in user_columns:
        alter_statements.append(
            "ALTER TABLE users ADD COLUMN level VARCHAR(20) DEFAULT 'A1'"
        )
    if "reminders_enabled" not in user_columns:
        alter_statements.append(
            "ALTER TABLE users ADD COLUMN reminders_enabled BOOLEAN DEFAULT FALSE"
        )
    if "reminder_time" not in user_columns:
        alter_statements.append(
            "ALTER TABLE users ADD COLUMN reminder_time VARCHAR(10)"
        )
    if "reminder_last_sent_date" not in user_columns:
        alter_statements.append(
            "ALTER TABLE users ADD COLUMN reminder_last_sent_date VARCHAR(10)"
        )
    if "level" not in word_set_columns:
        alter_statements.append(
            "ALTER TABLE word_sets ADD COLUMN level VARCHAR(20) DEFAULT 'A1'"
        )
    if "language" not in word_set_columns:
        alter_statements.append(
            "ALTER TABLE word_sets ADD COLUMN language VARCHAR(50) DEFAULT 'English'"
        )
    if "is_system" not in word_set_columns:
        alter_statements.append(
            "ALTER TABLE word_sets ADD COLUMN is_system BOOLEAN DEFAULT TRUE"
        )

    if not alter_statements:
        return

    with engine.begin() as connection:
        for statement in alter_statements:
            connection.execute(text(statement))


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
