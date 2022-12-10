import asyncio
import logging
from config_reader import config
from aiogram import Bot
from utils import update_status
from handlers import dp


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())


async def main():
    await update_status()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
