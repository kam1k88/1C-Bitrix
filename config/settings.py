import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Bitrix24
    BITRIX24_WEBHOOK_URL = os.getenv("BITRIX24_WEBHOOK_URL")
    
    # AI Services
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # 1C
    ONEC_BASE_URL = os.getenv("ONEC_BASE_URL")
    ONEC_USERNAME = os.getenv("ONEC_USERNAME")
    ONEC_PASSWORD = os.getenv("ONEC_PASSWORD")
    
    # Настройки AI
    DEFAULT_AI_MODEL = "gpt-4"
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7

settings = Settings()
