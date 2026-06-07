from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(slots=True)
class Config:
    bot_token: str
    database_url: str


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def load_config() -> Config:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    database_url = normalize_database_url(
        os.getenv("DATABASE_URL", "sqlite:///bot.sqlite3").strip()
    )

    if not bot_token:
        raise ValueError("BOT_TOKEN is not set. Fill it in .env before starting the bot.")

    return Config(bot_token=bot_token, database_url=database_url)
