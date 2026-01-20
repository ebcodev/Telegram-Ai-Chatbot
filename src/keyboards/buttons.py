from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Main Menu
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Model", callback_data="model_choice"),
     InlineKeyboardButton(text="Pic Setup", callback_data="pic_setup")],
    [InlineKeyboardButton(text="Context", callback_data="context_work"),
     InlineKeyboardButton(text="Voice", callback_data="voice_answer_work")],
    [InlineKeyboardButton(text="System Role", callback_data="system_value_work")]
])

# Model Choice
keyboard_model = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="GPT-5 Nano", callback_data="gpt_5_nano"),
     InlineKeyboardButton(text="GPT-4o Mini", callback_data="gpt_4o_mini")],
    [InlineKeyboardButton(text="GPT-5 Mini", callback_data="gpt_5_mini"),
     InlineKeyboardButton(text="GPT-4o", callback_data="gpt_4o")],
    [InlineKeyboardButton(text="GPT-5", callback_data="gpt_5")],
    [InlineKeyboardButton(text="Image 1 Mini", callback_data="gpt_image_1_mini"),
     InlineKeyboardButton(text="Image 1", callback_data="gpt_image_1"),
     InlineKeyboardButton(text="Image 1.5", callback_data="gpt_image_1_5")],
    [InlineKeyboardButton(text="Back", callback_data="back_menu")]
])

# Pic Setup
keyboard_pic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="SD", callback_data="set_sd"),
     InlineKeyboardButton(text="HD", callback_data="set_hd")],
    [InlineKeyboardButton(text="1024x1024", callback_data="set_1024x1024"),
     InlineKeyboardButton(text="1024x1792", callback_data="set_1024x1792")],
    [InlineKeyboardButton(text="Back", callback_data="back_menu")]
])

# Context
keyboard_context = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Show Context", callback_data="context"),
     InlineKeyboardButton(text="Clear Context", callback_data="clear")],
    [InlineKeyboardButton(text="Back", callback_data="back_menu")]
])

# Voice
keyboard_voice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Enable", callback_data="voice_answer_add"),
     InlineKeyboardButton(text="Disable", callback_data="voice_answer_del")],
    [InlineKeyboardButton(text="Back", callback_data="back_menu")]
])

# System Role
keyboard_value_work = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Change Role", callback_data="change_value"),
     InlineKeyboardButton(text="Delete Role", callback_data="delete_value")],
    [InlineKeyboardButton(text="Back", callback_data="back_menu")]
])
