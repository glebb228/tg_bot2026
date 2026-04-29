from aiogram.types import User as TelegramUser
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.bot.database.models import User


def get_or_create_user(session: Session, telegram_user: TelegramUser) -> tuple[User, bool]:
    existing_user = session.scalar(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    if existing_user is not None:
        return existing_user, False

    user = User(
        telegram_id=telegram_user.id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
    )
    session.add(user)
    session.flush()
    return user, True
