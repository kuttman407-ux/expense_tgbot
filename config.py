import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    bot_token: str
    db_name: str


def load_config() -> Config:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError(
            "Критическая ошибка: Переменная BOT_TOKEN не найдена в файле .env!"
        )

    db_name = os.getenv("DB_NAME", "expenses.db")

    return Config(
        bot_token=bot_token,
        db_name=db_name
    )