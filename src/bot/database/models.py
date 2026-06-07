from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.bot.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_language: Mapped[str] = mapped_column(String(50), default="English")
    level: Mapped[str] = mapped_column(String(20), default="A1")
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_time: Mapped[str | None] = mapped_column(String(10), nullable=True)
    reminder_last_sent_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    saved_words: Mapped[list["UserWord"]] = relationship(back_populates="user")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="user")


class WordSet(Base):
    __tablename__ = "word_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    language: Mapped[str] = mapped_column(String(50), default="English")
    title: Mapped[str] = mapped_column(String(255))
    level: Mapped[str] = mapped_column(String(20), default="A1")
    description: Mapped[str] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)
    cards: Mapped[list["WordCard"]] = relationship(back_populates="word_set")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="word_set")


class WordCard(Base):
    __tablename__ = "word_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_set_id: Mapped[int] = mapped_column(ForeignKey("word_sets.id"))
    position: Mapped[int] = mapped_column()
    foreign_word: Mapped[str] = mapped_column(String(255))
    translation: Mapped[str] = mapped_column(String(255))
    example: Mapped[str] = mapped_column(Text)

    word_set: Mapped["WordSet"] = relationship(back_populates="cards")
    saved_by_users: Mapped[list["UserWord"]] = relationship(back_populates="word_card")


class UserWord(Base):
    __tablename__ = "user_words"
    __table_args__ = (UniqueConstraint("user_id", "word_card_id", name="uq_user_word"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    word_card_id: Mapped[int] = mapped_column(ForeignKey("word_cards.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="saved_words")
    word_card: Mapped["WordCard"] = relationship(back_populates="saved_by_users")


class UserWordProgress(Base):
    __tablename__ = "user_word_progress"
    __table_args__ = (UniqueConstraint("user_id", "word_card_id", name="uq_user_word_progress"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    word_card_id: Mapped[int] = mapped_column(ForeignKey("word_cards.id"))
    attempts: Mapped[int] = mapped_column(default=0)
    correct_answers: Mapped[int] = mapped_column(default=0)
    last_result: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    word_set_id: Mapped[int] = mapped_column(ForeignKey("word_sets.id"))
    total_questions: Mapped[int] = mapped_column()
    correct_answers: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="quiz_attempts")
    word_set: Mapped["WordSet"] = relationship(back_populates="quiz_attempts")
