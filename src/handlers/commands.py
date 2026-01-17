from aiogram import Router, F, flags
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.database.storage import get_or_create_user_data, save_user_data
from src.utils.access_control import checkAccess
from src.utils.texts import start_message, help_message
from src.config import config
from src.handlers import common_state

router = Router()

@router.message(F.text == "/start")
@flags.throttling_key("spin")
async def command_start_handler(message: Message, state: FSMContext):
    if not await checkAccess(message):
        return

    if state is not None:
        await state.clear()

    # Retrieving or creating user data objects
    user_data = await get_or_create_user_data(message.from_user.id)

    user_data.model = "gpt-4o-mini"
    user_data.model_message_info = "4o mini"
    user_data.model_message_chat = "4o mini:\n\n"
    user_data.messages = []
    user_data.count_messages = 0
    user_data.max_out = 128000
    user_data.voice_answer = False
    user_data.system_message = ""
    user_data.pic_grade = "standard"
    user_data.pic_size = "1024x1024"

    # Saving updated data to the database
    await save_user_data(message.from_user.id)

    await message.answer(start_message)


@router.message(F.text == "/help")
@flags.throttling_key("spin")
async def help_handler(message: Message, state: FSMContext):
    if not await checkAccess(message):
        return

    if state is not None:
        await state.clear()

    # Retrieve or create user data objects
    await get_or_create_user_data(message.from_user.id)

    await message.answer(help_message)


@router.message(F.text == "/enable_all")
async def enable_all_access(message: Message):
    """
    Command to enable bot access for all users.
    Only users in OWNER_ID can use this command.
    """
    user_id = message.from_user.id

    # Ensure who can use this command
    if user_id != config.telegram.owner_id and user_id != config.telegram.admin_id:
        await message.answer("You do not have permission to use this command.")
        return

    common_state.ALL_USERS_ACCESS = True
    await message.answer("Bot access has been enabled for all users.")


@router.message(F.text == "/disable_all")
async def disable_all_access(message: Message):
    """
    Command to disable bot access for non-owner users.
    Only users in OWNER_ID can use this command.
    """
    user_id = message.from_user.id

    # Ensure who can use this command
    if user_id != config.telegram.owner_id and user_id != config.telegram.admin_id:
        await message.answer("You do not have permission to use this command.")
        return

    common_state.ALL_USERS_ACCESS = False
    await message.answer("Bot access has been disabled for all non-owner users. Owner access remains unaffected.")
