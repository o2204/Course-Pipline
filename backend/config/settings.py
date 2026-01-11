from pydantic_settings import BaseSettings
from typing import Set, Optional


class Settings(BaseSettings):

    # Database
    DATABASE_URL: Optional[str] = None

    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Higgsfield
    HIGGSFIELD_API_KEY: Optional[str] = None
    HIGGSFIELD_API_SECRET: Optional[str] = None
    HIGGSFIELD_API_URL: str = "https://platform.higgsfield.ai"
    HIGGSFIELD_VIDEO_MODEL_ID: str = "kling-video/v2.5-turbo/pro/image-to-video"
    HIGGSFIELD_DOP_MODEL_ID: str = "kling-video/v2.5-turbo/pro/image-to-video"
    HIGGSFIELD_IMAGE_MODEL_ID: str = "bytedance/seedream/v4/text-to-image"


    # Files
    ALLOWED_FILE_EXTENSIONS: Set[str] = {
        ".docx",
        ".doc",
        ".pdf",
        ".txt",
        ".md",
    }

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
