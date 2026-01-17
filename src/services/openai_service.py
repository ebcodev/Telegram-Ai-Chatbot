import asyncio
import logging
from typing import List, Dict, Any, Optional

from openai import OpenAI

from src.config import config

# Initialize OpenAI client
client = OpenAI(api_key=config.openai.api_key)

class OpenAIService:
    @staticmethod
    async def chat_completion(
        model: str,
        messages: List[Dict[str, str]],
        system_message: Optional[str] = None
    ) -> str:
        
        # Prepare messages
        final_messages = []
        if system_message and model in ["gpt-4o-mini", "gpt-4o"]:
             final_messages.append({"role": "system", "content": system_message})
        
        final_messages.extend(messages)
        
        try:
            chat_completion = await asyncio.to_thread(
                lambda: client.chat.completions.create(
                    model=model, messages=final_messages
                )
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI Chat Completion Error: {e}")
            raise e

    @staticmethod
    async def generate_image(
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1
    ) -> str:
        try:
            response = await asyncio.to_thread(
                lambda: client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    n=n,
                    size=size,
                    quality=quality,
                )
            )
            return response.data[0].url
        except Exception as e:
            logging.error(f"OpenAI Image Generation Error: {e}")
            raise e
            
    @staticmethod
    async def vision_chat_completion(
        text: str,
        base64_image: str,
        model: str = "gpt-4o",
        max_tokens: int = 4000
    ) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": base64_image}},
                ],
            }
        ]
        try:
            chat_completion = await asyncio.to_thread(
                lambda: client.chat.completions.create(
                    model=model, messages=messages, max_tokens=max_tokens
                )
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI Vision Error: {e}")
            raise e

    @staticmethod
    async def speech_to_text(file_path: str) -> str:
        try:
            with open(file_path, "rb") as audio_file:
                transcription = await asyncio.to_thread(
                    lambda: client.audio.transcriptions.create(
                        model="whisper-1", file=audio_file
                    )
                )
                return transcription.text
        except Exception as e:
            logging.error(f"OpenAI Speech to Text Error: {e}")
            raise e

    @staticmethod
    async def text_to_speech(text: str, file_path: str) -> None:
        try:
            response_voice = await asyncio.to_thread(
                lambda: client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=text,
                )
            )
            await asyncio.to_thread(
                lambda: response_voice.stream_to_file(file_path)
            )
        except Exception as e:
            logging.error(f"OpenAI Text to Speech Error: {e}")
            raise e
