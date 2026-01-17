import asyncio
import logging
import base64
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.client.session import aiohttp

from src.database.storage import get_or_create_user_data, save_user_data
from src.utils.access_control import checkAccess
from src.services.openai_service import OpenAIService

router = Router()

@router.message(F.photo)
async def chatgpt_photo_vision_handler(message: Message, state: FSMContext):
    if not await checkAccess(message):
        return

    if state is not None:
        await state.clear()

    try:
        user_data = await get_or_create_user_data(message.from_user.id)
        temp_message = await message.answer("⏳ Hold on, your request is being processed!")

        text = message.caption or "What's in the picture?"
        photo = message.photo[-1]
        file_info = await message.bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_info.file_path}"

        base64_image = await download_and_encode_image(file_url)

        ai_response = await OpenAIService.vision_chat_completion(
            text=text,
            base64_image=base64_image
        )

        user_data.count_messages += 1
        await save_user_data(message.from_user.id)

        await message.bot.delete_message(message.chat.id, temp_message.message_id)
        await message.answer(ai_response)

    except Exception as e:
        logging.exception(e)
        await message.reply(f"An error occurred: {e}")


async def download_and_encode_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                image_content = await resp.read()
                base64_image = base64.b64encode(image_content).decode("utf-8")
                return f"data:image/jpeg;base64,{base64_image}"
    raise ValueError("Failed to download image")
