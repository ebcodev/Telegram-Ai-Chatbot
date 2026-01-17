from dataclasses import dataclass, field
import json
from typing import List, Dict, Optional

@dataclass
class UserData:
    user_id: int
    messages: List[Dict] = field(default_factory=list)
    count_messages: int = 0
    model: str = "gpt-4o-mini"
    model_message_info: str = "4o mini"
    model_message_chat: str = "4o mini:\n\n"
    max_out: int = 128000
    voice_answer: bool = False
    system_message: str = ""
    pic_grade: str = "standard"
    pic_size: str = "1024x1024"

    def to_db_row(self):
        return (
            str(self.user_id),
            self.model,
            self.model_message_info,
            self.model_message_chat,
            json.dumps(self.messages),
            self.count_messages,
            self.max_out,
            self.voice_answer,
            self.system_message,
            self.pic_grade,
            self.pic_size,
        )

    @classmethod
    def from_db_row(cls, row):
        return cls(
            user_id=int(row["user_id"]),
            model=row["model"],
            model_message_info=row["model_message_info"],
            model_message_chat=row["model_message_chat"],
            messages=json.loads(row["messages"]) if row["messages"] else [],
            count_messages=row["count_messages"],
            max_out=row["max_out"],
            voice_answer=bool(row["voice_answer"]),
            system_message=row["system_message"],
            pic_grade=row["pic_grade"],
            pic_size=row["pic_size"],
        )
