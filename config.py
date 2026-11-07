import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    """Датакласс для хранения конфигурации приложения.
    
    Использование @dataclass обеспечивает строгость типов и удобный
    доступ к атрибутам через точку (config.bot_token), а также предотвращает
    случайную перезапись настроек в процессе работы.
    """
    bot_token: str
    db_name: str


def load_config() -> Config:
    """Загружает переменные окружения из .env и возвращает объект Config.
    
    Если BOT_TOKEN отсутствует в .env, выбрасывается исключение ValueError,
    предотвращающее запуск бота с невалидными данными.
    """
    # Считываем файл .env в окружение процесса
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError(
            "Критическая ошибка: Переменная BOT_TOKEN не найдена в файле .env!"
        )

    # Если DB_NAME не задан в .env, по умолчанию используется 'expenses.db'
    db_name = os.getenv("DB_NAME", "expenses.db")

    return Config(
        bot_token=bot_token,
        db_name=db_name
    )