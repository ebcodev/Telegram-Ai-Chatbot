from aiogram import Router
from src.handlers import commands, menu, chat, image

router = Router()

router.include_router(commands.router)
router.include_router(menu.router)
router.include_router(image.router)
# Chat router should be last because it captures all text messages
router.include_router(chat.router)
