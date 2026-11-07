import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import load_config
from database import init_db
from handlers import router


async def main() -> None:
    # 1. Настраиваем логирование, чтобы видеть статус работы бота в консоли
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logging.info("Запуск бота...")

    # 2. Загружаем параметры конфигурации из .env
    config = load_config()

    # 3. Инициализируем базу данных (создаём таблицу, если её нет)
    await init_db(config.db_name)

    # 4. Создаём объекты бота и диспетчера
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    # 5. Регистрируем роутер с обработчиками сообщений
    dp.include_router(router)

    # 6. Пропускаем накопленные сообщения, пока бот был оффлайн
    await bot.delete_webhook(drop_pending_updates=True)

    # 7. Запускаем бесконечный цикл опроса серверов Telegram (Long Polling)
    logging.info("Бот успешно запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")