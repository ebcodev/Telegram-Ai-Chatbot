from aiogram.types import Message
from src.config import config

async def checkAccess(message: Message) -> bool:
    """
    Check if the user has access to the bot.
    
    Args:
        message (Message): The incoming Telegram message
    
    Returns:
        bool: True if the user has access, False otherwise
    """
    user_id = message.from_user.id
    
    # Always allow owner and admin
    if user_id == config.telegram.owner_id or user_id == config.telegram.admin_id:
        return True
    
    # Check if all users are allowed
    from src.handlers import common_state # Avoid circular import if state is needed, or just keep state separate
    if common_state.ALL_USERS_ACCESS:
        return True
    
    # Deny access with a message
    await message.answer(
        f"<i>Sorry, you do not have access to this bot.\n"
        f"User ID:</i> <b>{user_id}</b>"
    )
    return False
