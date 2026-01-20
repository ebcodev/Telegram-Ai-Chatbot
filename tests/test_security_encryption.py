import asyncio
import os
import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.database.storage import init_db, save_user_data, get_or_create_user_data
from src.config import config
import aiosqlite

async def test_security_encryption():
    print("Initalizing DB...")
    await init_db()
    
    user_id = 888888
    
    # Ensure we have a key
    if not config.security.encryption_key:
        from cryptography.fernet import Fernet
        config.security.encryption_key = Fernet.generate_key().decode()
    
    # 1. Save User Data
    user_data = await get_or_create_user_data(user_id)
    secret_text = "Highly private message"
    user_data.messages = [{"role": "user", "content": secret_text}]
    await save_user_data(user_id)
    
    # 2. Verify DB content is encrypted
    db_file = project_root / "data/users_data.db"
    async with aiosqlite.connect(db_file) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT messages FROM UsersData WHERE user_id = ?", (str(user_id),)) as cursor:
            row = await cursor.fetchone()
            raw_msg = row["messages"]
            
            if not raw_msg.startswith("ENC:"):
                print("❌ FAILED: Message is stored as plain text!")
                return False
            
            if secret_text in raw_msg:
                 print("❌ FAILED: Secret text found in raw encrypted blob!")
                 return False
                 
            print("✅ PASSED: Messages are encrypted in DB and not readable as plain text.")

    # 3. Verify internal decryption STILL WORKS (for context)
    # Clear cache
    from src.database.storage import users_data_cache
    if user_id in users_data_cache:
        del users_data_cache[user_id]
        
    loaded_user = await get_or_create_user_data(user_id)
    if loaded_user.messages[0]["content"] == secret_text:
        print("✅ PASSED: Internal decryption works (context preserved).")
    else:
        print("❌ FAILED: Internal decryption failed. Context lost.")
        return False
    
    return True

if __name__ == "__main__":
    if asyncio.run(test_security_encryption()):
        sys.exit(0)
    else:
        sys.exit(1)
