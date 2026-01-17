import asyncio
from datetime import datetime
import pytz

from aiogram import Router, F, flags, types, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.state import StateFilter

from src.database.storage import get_or_create_user_data, save_user_data
from src.utils.access_control import checkAccess
from src.utils.functions import info_menu_func, process_voice_message
from src.utils.texts import system_message_text
from src.keyboards.buttons import (
    keyboard,
    keyboard_model,
    keyboard_pic,
    keyboard_context,
    keyboard_voice,
    keyboard_value_work,
)

# Set the timezone
timezone = pytz.timezone("Europe/Madrid")

router = Router()

# Creating a class for the state machine
class ChangeValueState(StatesGroup):
    waiting_for_new_value = State()


@router.message(F.text == "/menu")
@flags.throttling_key("spin")
async def process_key_button(message: Message, state: FSMContext):
    if not await checkAccess(message):
        return

    if state is not None:
        await state.clear()

    info_menu = await info_menu_func(message.from_user.id)

    await message.answer(text=f"{info_menu}", reply_markup=keyboard)


@router.callback_query(F.data == "back_menu")
async def process_callback_menu_back(callback_query: CallbackQuery, state: FSMContext):
    if not await checkAccess(callback_query.message):
        return

    if state is not None:
        await state.clear()

    info_menu = await info_menu_func(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text=f"{info_menu}", reply_markup=keyboard
    )


@router.callback_query(F.data == "info")
async def process_callback_info(callback_query: CallbackQuery, state: FSMContext):
    if not await checkAccess(callback_query.message):
        return

    if state is not None:
        await state.clear()

    # Retrieve or create user data objects
    user_data = await get_or_create_user_data(callback_query.from_user.id)

    info_voice_answer = "on" if user_data.voice_answer else "off"
    info_system_message = user_data.system_message if user_data.system_message else "Undefined"

    # Getting the current date and time
    current_datetime = datetime.now(timezone)
    formatted_datetime = current_datetime.strftime("%d.%m.%Y %H:%M:%S")

    info_messages = (
        f"<i>Date:</i> <b>{formatted_datetime}</b>\n"
        f"<i>User ID:</i> <b>{callback_query.from_user.id}</b>\n"
        f"<i>Model:</i> <b>{user_data.model_message_info}</b>\n"
        f"<i>Image</i>\n"
        f"<i>Quality:</i> <b>{user_data.pic_grade}</b>\n"
        f"<i>Size:</i> <b>{user_data.pic_size}</b>\n"
        f"<i>Messages:</i> <b>{user_data.count_messages}</b>\n"
        f"<i>Audios:</i> <b>{info_voice_answer}</b>\n"
        f"<i>Role:</i> <b>{info_system_message}</b>"
    )

    await callback_query.message.edit_text(
        text=info_messages,
        reply_markup=None,
    )
    await callback_query.answer()


# --- Model Choice Handlers ---

@router.callback_query(F.data == "model_choice")
async def process_callback_model_choice(
        callback_query: CallbackQuery, state: FSMContext
):
    if not await checkAccess(callback_query.message):
        return

    if state is not None:
        await state.clear()

    user_data = await get_or_create_user_data(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text=f"<i>Model:</i> {user_data.model_message_info} ",
        reply_markup=keyboard_model,
    )
    await callback_query.answer()


async def set_model(callback_query, model_id, model_info, model_chat_prefix):
    if not await checkAccess(callback_query.message):
        return

    user_data = await get_or_create_user_data(callback_query.from_user.id)

    if user_data.model == model_id:
        await callback_query.answer()
        return

    user_data.model = model_id
    user_data.max_out = 128000
    user_data.model_message_info = model_info
    user_data.model_message_chat = model_chat_prefix

    await save_user_data(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text=f"<i>Model:</i> {user_data.model_message_info} ",
        reply_markup=keyboard_model,
    )
    await callback_query.answer()


@router.callback_query(F.data == "gpt_4o_mini")
async def process_callback_gpt_4o_mini(callback_query: CallbackQuery):
    await set_model(callback_query, "gpt-4o-mini", "4o mini", "4o mini:\n\n")

@router.callback_query(F.data == "gpt_4_o")
async def process_callback_gpt_4o(callback_query: CallbackQuery):
    await set_model(callback_query, "gpt-4o", "4o", "4o:\n\n")

@router.callback_query(F.data == "gpt_o1_mini")
async def process_callback_o1_mini(callback_query: CallbackQuery):
    await set_model(callback_query, "o1-mini", "o1 mini", "o1 mini:\n\n")

@router.callback_query(F.data == "gpt_o1_preview")
async def process_callback_o1_preview(callback_query: CallbackQuery):
    await set_model(callback_query, "o1-preview", "o1", "o1:\n\n")

@router.callback_query(F.data == "dall_e_3")
async def process_callback_dall_e_3(callback_query: CallbackQuery):
    # DALL-E 3 handling logic is slightly different as it sets model for later use but not chat prefix in same way
    if not await checkAccess(callback_query.message):
        return

    user_data = await get_or_create_user_data(callback_query.from_user.id)

    if user_data.model == "dall-e-3":
        await callback_query.answer()
        return

    user_data.model = "dall-e-3"
    user_data.model_message_info = "DALL·E 3"
    user_data.model_message_chat = "DALL·E 3:\n\n"

    await save_user_data(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text=f"<i>Model:</i> {user_data.model_message_info} ",
        reply_markup=keyboard_model,
    )
    await callback_query.answer()


# --- Pic Settings Handlers ---

@router.callback_query(F.data == "pic_setup")
async def process_callback_menu_pic_setup(
        callback_query: CallbackQuery, state: FSMContext
):
    if not await checkAccess(callback_query.message):
        return

    if state is not None:
        await state.clear()

    user_data = await get_or_create_user_data(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text=f"{user_data.pic_grade} : {user_data.pic_size} ",
        reply_markup=keyboard_pic,
    )
    await callback_query.answer()


@router.callback_query(F.data.in_({"set_sd", "set_hd"}))
async def process_callback_set_quality(callback_query: CallbackQuery):
    if not await checkAccess(callback_query.message):
        return

    user_data = await get_or_create_user_data(callback_query.from_user.id)
    quality = "standard" if callback_query.data == "set_sd" else "hd"

    if user_data.pic_grade == quality:
        await callback_query.answer()
        return

    user_data.pic_grade = quality
    await save_user_data(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text=f"{user_data.pic_grade} : {user_data.pic_size} ",
        reply_markup=keyboard_pic,
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("set_") & F.data.contains("x"))
async def process_callback_set_size(callback_query: CallbackQuery):
    if not await checkAccess(callback_query.message):
        return

    size = callback_query.data.replace("set_", "")
    user_data = await get_or_create_user_data(callback_query.from_user.id)

    if user_data.pic_size == size:
        await callback_query.answer()
        return

    user_data.pic_size = size
    await save_user_data(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text=f"{user_data.pic_grade} : {user_data.pic_size} ",
        reply_markup=keyboard_pic,
    )
    await callback_query.answer()


# --- Context Handlers ---

@router.callback_query(F.data == "context_work")
async def process_callback_context_work(
        callback_query: CallbackQuery, state: FSMContext
):
    if not await checkAccess(callback_query.message):
        return

    if state is not None:
        await state.clear()

    user_data = await get_or_create_user_data(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text=f"<i>Messages:</i> {user_data.count_messages} ",
        reply_markup=keyboard_context,
    )
    await callback_query.answer()


@router.callback_query(F.data == "context")
async def process_callback_context(callback_query: CallbackQuery):
    if not await checkAccess(callback_query.message):
        return

    user_data = await get_or_create_user_data(callback_query.from_user.id)
    history = "\n\n".join(f"{msg['role']}:\n{msg['content']}" for msg in user_data.messages)

    if callback_query.message.text == "Context is empty":
        await callback_query.answer()
        return

    if not history:
        await callback_query.message.edit_text(
            text="Context is empty", reply_markup=keyboard_context
        )
        await callback_query.answer()
        return

    # Send history in chunks
    max_length = 4096
    lines = history.split("\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        line_length = len(line) + 1
        if current_length + line_length > max_length:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    for chunk in chunks:
         await callback_query.message.answer(chunk, disable_web_page_preview=True)

    await callback_query.message.answer(
        text=f"Actions with context:",
        reply_markup=keyboard_context,
    )

    await callback_query.message.edit_text(text="Context:", reply_markup=None)
    await callback_query.answer()


@router.callback_query(F.data == "clear")
async def process_callback_clear(callback_query: CallbackQuery):
    if not await checkAccess(callback_query.message):
        return

    user_data = await get_or_create_user_data(callback_query.from_user.id)
    user_data.messages = []
    user_data.count_messages = 0
    await save_user_data(callback_query.from_user.id)

    if callback_query.message.text == "Context cleared":
        await callback_query.answer()
        return

    await callback_query.message.edit_text(
        text="Context cleared", reply_markup=keyboard_context
    )
    await callback_query.answer()


# --- Voice Settings Handlers ---

@router.callback_query(F.data == "voice_answer_work")
async def process_callback_voice_answer_work(
        callback_query: CallbackQuery, state: FSMContext
):
    if not await checkAccess(callback_query.message):
        return

    if state is not None:
        await state.clear()

    user_data = await get_or_create_user_data(callback_query.from_user.id)
    info_voice_answer = "on" if user_data.voice_answer else "off"

    await callback_query.message.edit_text(
        text=f"<i>Audio:</i> {info_voice_answer}",
        reply_markup=keyboard_voice,
    )
    await callback_query.answer()


@router.callback_query(F.data.in_({"voice_answer_add", "voice_answer_del"}))
async def process_callback_voice_answer_toggle(callback_query: CallbackQuery):
    if not await checkAccess(callback_query.message):
        return

    user_data = await get_or_create_user_data(callback_query.from_user.id)
    should_enable = callback_query.data == "voice_answer_add"

    if user_data.voice_answer == should_enable:
        await callback_query.answer()
        return

    user_data.voice_answer = should_enable
    await save_user_data(callback_query.from_user.id)

    info_voice_answer = "enabled" if user_data.voice_answer else "off"
    # "enabled" if on, "off" if off? original code was inconsistent "enabled" vs "on" vs "off"
    # Keeping consistent with original logic if possible, or simplifying.
    # Original: add -> "enabled", del -> "on" (Wait, really? Let's check original code)
    # Original add: info_voice_answer = "enabled"
    # Original del: info_voice_answer = "on" if user_data.voice_answer else "off" (so "off")
    # I'll stick to on/off for consistency in display

    display_status = "enabled" if user_data.voice_answer else "off"

    await callback_query.message.edit_text(
        text=f"<i>Audio:</i> {display_status}", reply_markup=keyboard_voice
    )
    await callback_query.answer()


# --- System Role Handlers ---

@router.callback_query(F.data == "system_value_work")
async def process_callback_system_value_work(
        callback_query: CallbackQuery, state: FSMContext
):
    if not await checkAccess(callback_query.message):
        return

    if state is not None:
        await state.clear()

    user_data = await get_or_create_user_data(callback_query.from_user.id)
    info_system_message = user_data.system_message if user_data.system_message else "Undefined"

    await callback_query.message.edit_text(
        text=f"<i>Role:</i> {info_system_message}",
        reply_markup=keyboard_value_work,
    )
    await callback_query.answer()


@router.callback_query(F.data == "change_value")
async def process_callback_change_value(
        callback_query: CallbackQuery, state: FSMContext
):
    if not await checkAccess(callback_query.message):
        return

    await state.set_state(ChangeValueState.waiting_for_new_value)

    await callback_query.message.edit_text(
        text=system_message_text,
        reply_markup=None,
    )
    await callback_query.answer()


@router.callback_query(F.data == "delete_value")
async def process_callback_delete_value(callback_query: CallbackQuery, state: FSMContext):
    if not await checkAccess(callback_query.message):
        return

    if state is not None:
        await state.clear()

    user_data = await get_or_create_user_data(callback_query.from_user.id)

    if not user_data.system_message:
        await callback_query.answer()
        return

    user_data.system_message = ""
    await save_user_data(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text=f"<i>Role:</i> Undefined",
        reply_markup=keyboard_value_work,
    )
    await callback_query.answer()


@router.message(StateFilter(ChangeValueState.waiting_for_new_value))
async def process_new_value(message: Message, state: FSMContext, bot: Bot):
    if not await checkAccess(message):
        return

    sys_message = ""
    if message.voice:
        sys_message = await process_voice_message(bot, message, message.from_user.id)
    elif message.text:
        sys_message = message.text

    user_data = await get_or_create_user_data(message.from_user.id)
    user_data.system_message = sys_message
    await save_user_data(message.from_user.id)

    await state.clear()

    info_system_message = user_data.system_message if user_data.system_message else "Undefined"

    await message.answer(
        text=f"<i>Role:</i> {info_system_message}",
        reply_markup=keyboard_value_work,
    )
