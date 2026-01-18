import configparser
from pathlib import Path
from dataclasses import dataclass

@dataclass
class TelegramConfig:
    token: str
    owner_id: int

@dataclass
class OpenAIConfig:
    api_key: str

@dataclass
class SecurityConfig:
    encryption_key: str

@dataclass
class Config:
    telegram: TelegramConfig
    openai: OpenAIConfig
    security: SecurityConfig

def load_config(path: Path = None) -> Config:
    if path is None:
        path = Path(__file__).parent.parent / "config.ini"
    
    config_parser = configparser.ConfigParser()
    config_parser.read(path)
    
    try:
        owner_id = int(config_parser.get("Telegram", "owner_id"))
    except (ValueError, configparser.NoOptionError):
        owner_id = 0
        


    return Config(
        telegram=TelegramConfig(
            token=config_parser.get("Telegram", "token", fallback=""),
            owner_id=owner_id,
        ),
        openai=OpenAIConfig(
            api_key=config_parser.get("OpenAI", "api_key"),
        ),
        security=SecurityConfig(
            encryption_key=config_parser.get("Security", "encryption_key", fallback=""),
        )
    )

# Singleton instance to be used across the app
config = load_config()
