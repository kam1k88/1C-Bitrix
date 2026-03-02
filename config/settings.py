import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Централизованная конфигурация приложения"""
    
    # === Bitrix24 Configuration ===
    
    # Webhook аутентификация (рекомендуется для простых интеграций)
    BITRIX24_WEBHOOK_URL: Optional[str] = os.getenv("BITRIX24_WEBHOOK_URL")
    
    # OAuth аутентификация (для приложений)
    BITRIX24_DOMAIN: Optional[str] = os.getenv("BITRIX24_DOMAIN")
    BITRIX24_CLIENT_ID: Optional[str] = os.getenv("BITRIX24_CLIENT_ID")
    BITRIX24_CLIENT_SECRET: Optional[str] = os.getenv("BITRIX24_CLIENT_SECRET")
    BITRIX24_ACCESS_TOKEN: Optional[str] = os.getenv("BITRIX24_ACCESS_TOKEN")
    BITRIX24_REFRESH_TOKEN: Optional[str] = os.getenv("BITRIX24_REFRESH_TOKEN")
    
    # Настройки SDK
    BITRIX24_API_VERSION: int = int(os.getenv("BITRIX24_API_VERSION", "2"))
    BITRIX24_TIMEOUT: float = float(os.getenv("BITRIX24_TIMEOUT", "10"))
    BITRIX24_MAX_RETRIES: int = int(os.getenv("BITRIX24_MAX_RETRIES", "3"))
    
    # === AI Services ===
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # AI Settings
    DEFAULT_AI_MODEL: str = os.getenv("DEFAULT_AI_MODEL", "gpt-4")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # === 1C Integration ===
    ONEC_BASE_URL: Optional[str] = os.getenv("ONEC_BASE_URL")
    ONEC_USERNAME: Optional[str] = os.getenv("ONEC_USERNAME")
    ONEC_PASSWORD: Optional[str] = os.getenv("ONEC_PASSWORD")
    
    # === Application Settings ===
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_bitrix_auth_type(cls) -> str:
        """Определить тип аутентификации Bitrix24"""
        if cls.BITRIX24_WEBHOOK_URL:
            return "webhook"
        elif cls.BITRIX24_ACCESS_TOKEN and cls.BITRIX24_CLIENT_ID:
            return "oauth"
        else:
            raise ValueError(
                "Bitrix24 authentication not configured. "
                "Set BITRIX24_WEBHOOK_URL or OAuth credentials"
            )
    
    @classmethod
    def validate(cls) -> None:
        """Валидация обязательных настроек"""
        errors = []
        
        # Проверка Bitrix24
        if not cls.BITRIX24_WEBHOOK_URL and not cls.BITRIX24_ACCESS_TOKEN:
            errors.append("Bitrix24: Set BITRIX24_WEBHOOK_URL or OAuth credentials")
        
        # Проверка AI сервисов
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            errors.append("AI Services: Set at least OPENAI_API_KEY or ANTHROPIC_API_KEY")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"- {e}" for e in errors))


settings = Settings()

# Валидация при импорте (опционально, можно закомментировать)
# settings.validate()
