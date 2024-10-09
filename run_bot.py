import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from foundation import TOKEN, storage
from middlewares.db import DataBaseSession
from handlers.client import client_router
from handlers.select_category import category_router
from handlers.buy import buy_router
from handlers.order import order_router
from handlers.update_order import update_order_router
from data_base.engine import create_db, session_maker


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher(storage=storage)

dp.include_router(client_router)
dp.include_router(category_router)
dp.include_router(buy_router)
dp.include_router(order_router)
dp.include_router(update_order_router)

async def on_startup(bot):
    await create_db()


async def on_shutdown(bot):
    print('бот лег')


async def main() -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())