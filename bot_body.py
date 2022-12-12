import asyncio
import logging

from aiogram import Bot

from config_reader import config
from handlers import dp
from utils import update_status


log_format = ('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')

logging.basicConfig(
    level=logging.INFO,
    filename='ping_bot.log',
    filemode='w',
    format=log_format
)

bot = Bot(token=config.bot_token.get_secret_value())


async def main():
    logging.info('START_BOT')
    asyncio.ensure_future(update_status(bot))
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
