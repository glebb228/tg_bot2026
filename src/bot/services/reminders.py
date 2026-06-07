import asyncio
from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.bot.database.models import User


MOSCOW_TZ = ZoneInfo("Europe/Moscow")
REMINDER_TEXT = (
    "Напоминание о тренировке\n\n"
    "Пора повторить слова на выбранном языке. Открой раздел «Тренировка» и пройди короткий тест."
)


def get_users_for_reminder(session: Session, current_time: str, current_date: str) -> list[User]:
    return list(
        session.scalars(
            select(User).where(
                User.reminders_enabled.is_(True),
                User.reminder_time == current_time,
                (User.reminder_last_sent_date.is_(None) | (User.reminder_last_sent_date != current_date)),
            )
        )
    )


def mark_reminder_sent(session: Session, user_id: int, current_date: str) -> None:
    user = session.get(User, user_id)
    if user is not None:
        user.reminder_last_sent_date = current_date
        session.flush()


async def run_reminder_scheduler(
    bot: Bot,
    session_manager: Callable[[], object],
    check_interval_seconds: int = 60,
) -> None:
    while True:
        now = datetime.now(MOSCOW_TZ)
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")

        with session_manager() as session:
            users = get_users_for_reminder(session, current_time, current_date)

        for user in users:
            try:
                await bot.send_message(user.telegram_id, REMINDER_TEXT)
            except Exception as error:
                print(f"Failed to send reminder to {user.telegram_id}: {error}")
                continue

            with session_manager() as session:
                mark_reminder_sent(session, user.id, current_date)

        await asyncio.sleep(check_interval_seconds)
