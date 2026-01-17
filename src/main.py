import asyncio
import logging
import sys
from pathlib import Path

# Add project root to sys.path to allow imports from src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.handlers import router
from src.config import config
from src.database.storage import init_db
from src.middlewares.throttling import ThrottlingMiddleware

async def set_commands(bot: Bot):
    commands = {
        types.BotCommandScopeAllPrivateChats(): [
            types.BotCommand(command="/start", description="🔄 Start"),
            types.BotCommand(command="/menu", description="➡️ Menu"),
            types.BotCommand(command="/help", description="ℹ️ Help"),
        ],
        types.BotCommandScopeAllGroupChats(): []
    }

    for scope, command_list in commands.items():
        await bot.set_my_commands(commands=command_list, scope=scope)


async def start_bot():
    await init_db()
    
    bot = Bot(token=config.telegram.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    
    # Global middleware
    dp.message.middleware(ThrottlingMiddleware(spin=1.5))
    
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    return bot, dp


async def main():
    bot = None
    try:
        bot, dp = await start_bot()
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logging.exception(f"An error occurred: {e}")
    finally:
        if bot is not None:
            await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
    asyncio.run(main())
