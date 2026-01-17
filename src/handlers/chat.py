import asyncio
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold
from aiogram.enums import ParseMode

from src.database.storage import get_or_create_user_data, save_user_data
from src.utils.access_control import checkAccess
from src.utils.functions import prune_messages, process_voice_message, simple_bot_responses
from src.services.openai_service import OpenAIService

router = Router()

@router.message(F.content_type.in_({"text", "voice"}))
async def chatgpt_text_handler(message: Message):
    if not await checkAccess(message):
        return

    # Check if command (handled by other routers)
    if message.text and message.text.startswith("/"):
        return

    user_data = await get_or_create_user_data(message.from_user.id)
    user_prompt = ""

    # Temporary message
    response = await message.answer(f"⏳ Hold on, your request is being processed!")
    last_message_id = response.message_id

    try:
        if message.voice:
            user_prompt = await process_voice_message(message.bot, message, message.from_user.id)
        elif message.text:
            user_prompt = message.text

        # First, check for simple bot responses
        simple_response = await simple_bot_responses(user_prompt)
        if simple_response:
            await message.bot.delete_message(message.chat.id, last_message_id)
            await message.reply(simple_response)
            return

        # DALL-E 3 Handling
        if user_data.model == "dall-e-3":
            await handle_dalle(message, user_data, user_prompt, last_message_id)
            return

        # Text Models Handling
        if user_data.model in ["gpt-4o-mini", "gpt-4o", "o1-mini", "o1-preview"]:
            await handle_text_model(message, user_data, user_prompt, last_message_id)
            return

    except Exception as e:
        logging.exception(e)
        await message.reply(f"An error occurred: {e}")


async def handle_dalle(message, user_data, prompt, loading_msg_id):
    try:
        image_url = await OpenAIService.generate_image(
            prompt=prompt,
            size=user_data.pic_size,
            quality=user_data.pic_grade
        )

        user_data.count_messages += 1
        await save_user_data(message.from_user.id)

        await message.bot.delete_message(message.chat.id, loading_msg_id)
        await message.bot.send_photo(
            message.chat.id,
            image_url,
            reply_to_message_id=message.message_id,
        )
    except Exception as e:
        logging.exception(e)
        await message.reply(f"An error occurred generating image: {e}")


async def handle_text_model(message, user_data, prompt, loading_msg_id):
    # Add the user's message to the chat history
    user_data.messages.append({"role": "user", "content": prompt})

    # Apply the trim function
    pruned_messages = await prune_messages(
        user_data.messages, max_chars=user_data.max_out
    )

    # Process system message
    system_msg = user_data.system_message if user_data.system_message else None

    # Bot is typing...
    await message.bot.send_chat_action(message.chat.id, action="typing")

    response_message = await OpenAIService.chat_completion(
        model=user_data.model,
        messages=pruned_messages,
        system_message=system_msg
    )

    # Adding the model's response to the chat history
    user_data.messages.append({"role": "assistant", "content": response_message})
    user_data.count_messages += 1
    await save_user_data(message.from_user.id)

    await message.bot.delete_message(message.chat.id, loading_msg_id)

    await send_response(message, user_data, response_message)


async def send_response(message, user_data, response_text):
    async def send_voice_if_enabled():
        if user_data.voice_answer:
            from pathlib import Path
            speech_file_path = Path(__file__).parent.parent.parent / f"data/voice/speech_{message.chat.id}.mp3"
            speech_file_path.parent.mkdir(parents=True, exist_ok=True)

            await OpenAIService.text_to_speech(response_text, str(speech_file_path))

            from aiogram.types import FSInputFile
            audio = FSInputFile(speech_file_path)
            await message.bot.send_audio(
                message.chat.id, audio, title="Audio answer option"
            )

    try:
        if "```" in response_text:
            # Code block present, use Markdown
            if len(response_text) > 4096:
                await send_long_message(message, user_data.model_message_chat, response_text, parse_mode=ParseMode.MARKDOWN)
            else:
                final_message = f"*{user_data.model_message_chat}*{response_text}"
                await message.reply(final_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        else:
            # Plain text
            if len(response_text) > 4096:
                await send_long_message(message, user_data.model_message_chat, response_text, parse_mode=None)
            else:
                content_kwargs = Text(Bold(user_data.model_message_chat), response_text)
                await message.reply(**content_kwargs.as_kwargs(), disable_web_page_preview=True)

        await send_voice_if_enabled()

    except Exception as e:
        logging.error(f"Error sending message: {e}")
        # Fallback to splitting plain text
        await send_long_message(message, user_data.model_message_chat, response_text, parse_mode=None)


async def send_long_message(message, prefix, text, parse_mode=None):
    if parse_mode == ParseMode.MARKDOWN:
        full_text = f"*{prefix}*\n{text}"
    else:
        full_text = f"{prefix}\n{text}"

    lines = full_text.split("\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        line_length = len(line) + 1
        if current_length + line_length > 4096:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    for chunk in chunks:
        if parse_mode:
            await message.answer(chunk, parse_mode=parse_mode, disable_web_page_preview=True)
        else:
            content_kwargs = Text(chunk)
            await message.answer(**content_kwargs.as_kwargs(), disable_web_page_preview=True)
