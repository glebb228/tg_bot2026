from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.bot.database.models import User
from src.bot.services.learning import LEVEL_ORDER, SUPPORTED_LANGUAGES


@dataclass(slots=True)
class UserSettingsView:
    current_language: str
    level: str
    reminders_enabled: bool
    reminder_time: str | None


def get_user_settings(session: Session, telegram_id: int) -> UserSettingsView | None:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return None

    return UserSettingsView(
        current_language=user.current_language,
        level=user.level,
        reminders_enabled=user.reminders_enabled,
        reminder_time=user.reminder_time,
    )


def update_user_language(session: Session, telegram_id: int, language: str) -> bool:
    if language not in SUPPORTED_LANGUAGES:
        return False

    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return False
    user.current_language = language
    session.flush()
    return True


def update_user_level(session: Session, telegram_id: int, level: str) -> bool:
    if level not in LEVEL_ORDER:
        return False

    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return False
    user.level = level
    session.flush()
    return True


def update_user_reminders(
    session: Session,
    telegram_id: int,
    enabled: bool,
    reminder_time: str | None,
) -> bool:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        return False

    user.reminders_enabled = enabled
    user.reminder_time = reminder_time if enabled else None
    if not enabled:
        user.reminder_last_sent_date = None
    session.flush()
    return True
