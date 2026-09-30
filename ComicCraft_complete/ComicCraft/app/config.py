from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    gemini_api_key: str = ""
    hf_api_key: str = ""

    # These are intentionally configurable because provider model names change.
    # The original project documentation used Gemini 1.5 Flash/Pro.
    gemini_outline_model: str = "gemini-2.5-flash"
    gemini_story_model: str = "gemini-2.5-pro"

    # Hugging Face model used through its inference API.
    hf_image_model: str = "runwayml/stable-diffusion-v1-5"

    app_name: str = "ComicCraft"
    panel_count: int = 5
    image_width: int = 768
    image_height: int = 768

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
