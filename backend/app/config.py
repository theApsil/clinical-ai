import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    LLM_API_URL: str = os.environ["LLM_API_URL"]
    LLM_AUTH_TOKEN: str = os.environ["LLM_AUTH_TOKEN"]

    YANDEX_API_URL: str = os.environ["YANDEX_API_URL"]
    YANDEX_AUTH_TOKEN: str = os.environ["YANDEX_AUTH_TOKEN"]
    YANDEX_MODEL_PACKAGE: str = os.environ["YANDEX_MODEL_PACKAGE"]

    LLM_MODEL_FAST: str = os.getenv("LLM_MODEL_FAST", "qwen_3_4b")
    LLM_MODEL_REASONING: str = os.getenv("LLM_MODEL_REASONING", "gemma_3_27b")

    APP_NAME: str = os.getenv("APP_NAME", "clinical-ai")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # TODO: STORAGE + SERVER


settings = Settings()
