from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, spin: float = 1.0):
        self.spin = spin
        self.cache = TTLCache(maxsize=10_000, ttl=spin)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
             return await handler(event, data)
        
        user_id = event.from_user.id if event.from_user else event.chat.id
        
        if user_id in self.cache:
            return
            
        self.cache[user_id] = True
        return await handler(event, data)
