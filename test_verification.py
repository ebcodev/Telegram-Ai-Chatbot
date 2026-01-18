import asyncio
import os
import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.database.storage import init_db, save_user_data, get_or_create_user_data, get_all_users
from src.database.entities import UserData
from src.config import config
import aiosqlite

async def test_encryption():
    print("Initalizing DB...")
    await init_db()
    
    user_id = 999999
    username = "TestUser"
    
    # 1. Create and Save User
    print(f"Creating user {user_id}...")
    user_data = await get_or_create_user_data(user_id)
    user_data.username = username
    user_data.messages = [{"role": "user", "content": "Secret Message 123"}]
    
    # Enable encryption key for test if not set (though config should load it or fallback empty)
    # We need a key to test encryption.
    if not config.security.encryption_key:
        print("Generating temporary encryption key for test...")
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()
        config.security.encryption_key = key
    
    await save_user_data(user_id)
    print("User saved.")
    
    # 2. Check Raw DB (Verify Encryption)
    print("Checking raw DB content...")
    db_file = Path(__file__).parent / "data/users_data.db"
    async with aiosqlite.connect(db_file) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT messages FROM UsersData WHERE user_id = ?", (str(user_id),)) as cursor:
            row = await cursor.fetchone()
            raw_msg = row["messages"]
            if raw_msg.startswith("ENC:"):
                print("✅ PASSED: Messages are encrypted in DB.")
            else:
                print(f"❌ FAILED: Messages are NOT encrypted. Raw: {raw_msg}")

    # 3. Load User (Verify Decryption)
    print("Loading user...")
    # Clear cache to force DB reload
    from src.database.storage import users_data_cache
    if user_id in users_data_cache:
        del users_data_cache[user_id]
        
    loaded_user = await get_or_create_user_data(user_id)
    if loaded_user.messages[0]["content"] == "Secret Message 123":
        print("✅ PASSED: Messages decrypted correctly.")
    else:
        print(f"❌ FAILED: Messages content mismatch. Got: {loaded_user.messages}")

if __name__ == "__main__":
    try:
        asyncio.run(test_encryption())
    except Exception as e:
        print(f"Error: {e}")
