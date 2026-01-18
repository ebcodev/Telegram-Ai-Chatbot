from pathlib import Path
from typing import List, Dict, Optional
import aiosqlite
import logging

from src.database.entities import UserData

DB_FILE = Path(__file__).parent.parent.parent / "data/users_data.db"

# Dictionary for storing user data (Cache)
users_data_cache: Dict[int, UserData] = {}

async def init_db():
    """Initialize the database table."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS UsersData (
                user_id TEXT PRIMARY KEY,
                model TEXT,
                model_message_info TEXT,
                model_message_chat TEXT,
                messages TEXT,
                count_messages INTEGER,
                max_out INTEGER,
                voice_answer BOOLEAN,
                system_message TEXT,
                pic_grade TEXT,
                pic_size TEXT,
                username TEXT
            )
        """
        )
        # Migration: Check if username column exists, if not add it
        try:
             await db.execute("SELECT username FROM UsersData LIMIT 1")
        except aiosqlite.OperationalError:
             await db.execute("ALTER TABLE UsersData ADD COLUMN username TEXT")
             
        await db.commit()

async def get_or_create_user_data(user_id: int) -> UserData:
    """Get user data from cache or DB, or create new."""
    if user_id in users_data_cache:
        return users_data_cache[user_id]

    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM UsersData WHERE user_id = ?", (str(user_id),)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                user_data = UserData.from_db_row(row)
            else:
                user_data = UserData(user_id=user_id)

    users_data_cache[user_id] = user_data
    return user_data

async def save_user_data(user_id: int) -> None:
    """Save user data from cache to DB."""
    user_data = users_data_cache.get(user_id)
    if not user_data:
        logging.warning(f"Attempted to save non-existent user data for {user_id}")
        return

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            """
            INSERT INTO UsersData (user_id, model, model_message_info, model_message_chat, messages,
            count_messages, max_out, voice_answer, system_message, pic_grade, pic_size, username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET
                model = excluded.model,
                model_message_info = excluded.model_message_info,
                model_message_chat = excluded.model_message_chat,
                messages = excluded.messages,
                count_messages = excluded.count_messages,
                max_out = excluded.max_out,
                voice_answer = excluded.voice_answer,
                system_message = excluded.system_message,
                pic_grade = excluded.pic_grade,
                pic_size = excluded.pic_size,
                username = excluded.username
            """,
            user_data.to_db_row(),
        )
        await db.commit()

async def get_all_users() -> List[Dict[str, str]]:
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT user_id, username FROM UsersData") as cursor:
            users = []
            for row in await cursor.fetchall():
                username = row["username"] if "username" in row.keys() and row["username"] else "Unknown"
                users.append({"user_id": str(row["user_id"]), "username": username})
            return users
