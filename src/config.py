import configparser
from pathlib import Path
from dataclasses import dataclass

@dataclass
class TelegramConfig:
    token: str
    owner_id: int
    admin_id: int

@dataclass
class OpenAIConfig:
    api_key: str

@dataclass
class Config:
    telegram: TelegramConfig
    openai: OpenAIConfig

def load_config(path: Path = None) -> Config:
    if path is None:
        path = Path(__file__).parent.parent / "config.ini"
    
    config_parser = configparser.ConfigParser()
    config_parser.read(path)
    
    return Config(
        telegram=TelegramConfig(
            token=config_parser.get("Telegram", "token"),
            owner_id=int(config_parser.get("Telegram", "owner_id")),
            admin_id=int(config_parser.get("Telegram", "admin_id")),
        ),
        openai=OpenAIConfig(
            api_key=config_parser.get("OpenAI", "api_key"),
        )
    )

# Singleton instance to be used across the app
config = load_config()
