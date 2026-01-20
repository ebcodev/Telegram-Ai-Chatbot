from dataclasses import dataclass, field
import json
from typing import List, Dict, Optional

@dataclass
class UserData:
    user_id: int
    messages: List[Dict] = field(default_factory=list)
    count_messages: int = 0
    model: str = "gpt-5-nano"
    model_message_info: str = "5 nano"
    model_message_chat: str = "5 nano:\n\n"
    max_out: int = 128000
    voice_answer: bool = False
    system_message: str = ""
    pic_grade: str = "standard"
    pic_size: str = "1024x1024"
    username: str = "Unknown"

    def to_db_row(self):
        # Encryption
        from src.config import config
        from cryptography.fernet import Fernet
        
        messages_json = json.dumps(self.messages)
        
        # If encryption key is set, encrypt the messages
        if config.security.encryption_key:
            f = Fernet(config.security.encryption_key.encode())
            encrypted_messages = f.encrypt(messages_json.encode()).decode()
            stored_messages = f"ENC:{encrypted_messages}"
        else:
            # Enforce encryption: do not save in plain text.
            stored_messages = "ENC:ERROR_NO_KEY"

        return (
            str(self.user_id),
            self.model,
            self.model_message_info,
            self.model_message_chat,
            stored_messages,
            self.count_messages,
            self.max_out,
            self.voice_answer,
            self.system_message,
            self.pic_grade,
            self.pic_size,
            self.username,
        )

    @classmethod
    def from_db_row(cls, row):
        # Decryption
        from src.config import config
        from cryptography.fernet import Fernet
        
        raw_messages = row["messages"]
        messages = []
        
        if raw_messages:
            try:
                if raw_messages.startswith("ENC:") and config.security.encryption_key:
                    f = Fernet(config.security.encryption_key.encode())
                    encrypted_data = raw_messages.split("ENC:", 1)[1]
                    decrypted_json = f.decrypt(encrypted_data.encode()).decode()
                    messages = json.loads(decrypted_json)
                elif raw_messages.startswith("ENC:") and not config.security.encryption_key:
                     # Key missing but data is encrypted
                     messages = [{"role": "system", "content": "Error: Data is encrypted but key is missing."}]
                else:
                    messages = json.loads(raw_messages)
            except Exception as e:
                messages = [{"role": "system", "content": f"Error loading messages: {e}"}]

        # Handle simplified backward compatibility if username missing in row (though query should return it if updated)
        # We'll assume row has it or we handle it in storage.py SQL
        username = row["username"] if "username" in row.keys() else "Unknown"

        return cls(
            user_id=int(row["user_id"]),
            model=row["model"],
            model_message_info=row["model_message_info"],
            model_message_chat=row["model_message_chat"],
            messages=messages,
            count_messages=row["count_messages"],
            max_out=row["max_out"],
            voice_answer=bool(row["voice_answer"]),
            system_message=row["system_message"],
            pic_grade=row["pic_grade"],
            pic_size=row["pic_size"],
            username=username,
        )
