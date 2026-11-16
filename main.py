import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import load_config
from database import init_db
from handlers import router


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logging.info("Запуск бота...")

    config = load_config()

    await init_db(config.db_name)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("Бот успешно запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")