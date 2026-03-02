"""
Тесты для конфигурации
"""
import pytest
import os
from unittest.mock import patch
from config.settings import Settings


class TestSettings:
    """Тесты для Settings"""
    
    def test_settings_defaults(self):
        """Тест значений по умолчанию"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            assert settings.DEBUG is False
            assert settings.LOG_LEVEL == "INFO"
            assert settings.DEFAULT_AI_MODEL == "gpt-4"
            assert settings.MAX_TOKENS == 2000
            assert settings.TEMPERATURE == 0.7
    
    def test_settings_from_env(self):
        """Тест загрузки из переменных окружения"""
        env_vars = {
            "BITRIX24_WEBHOOK_URL": "https://test.bitrix24.ru/rest/1/xxxxx/",
            "OPENAI_API_KEY": "sk-test-key",
            "DEBUG": "True",
            "LOG_LEVEL": "DEBUG"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            assert settings.BITRIX24_WEBHOOK_URL == "https://test.bitrix24.ru/rest/1/xxxxx/"
            assert settings.OPENAI_API_KEY == "sk-test-key"
            assert settings.DEBUG is True
            assert settings.LOG_LEVEL == "DEBUG"
    
    def test_bitrix24_oauth_settings(self):
        """Тест OAuth настроек Bitrix24"""
        env_vars = {
            "BITRIX24_DOMAIN": "test.bitrix24.ru",
            "BITRIX24_CLIENT_ID": "test_client_id",
            "BITRIX24_CLIENT_SECRET": "test_secret",
            "BITRIX24_ACCESS_TOKEN": "test_token"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            assert settings.BITRIX24_DOMAIN == "test.bitrix24.ru"
            assert settings.BITRIX24_CLIENT_ID == "test_client_id"
            assert settings.BITRIX24_CLIENT_SECRET == "test_secret"
            assert settings.BITRIX24_ACCESS_TOKEN == "test_token"
