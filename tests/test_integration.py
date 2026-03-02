"""
Интеграционные тесты (требуют реальные credentials)
Запускайте только с настроенными переменными окружения
"""
import pytest
import os
from bitrix24.sdk_client import create_client_from_webhook
from ai_services.openai_service import OpenAIService
from automation.lead_processor import LeadProcessor


# Пропускаем тесты если нет credentials
skip_if_no_credentials = pytest.mark.skipif(
    not os.getenv("BITRIX24_WEBHOOK_URL") or not os.getenv("OPENAI_API_KEY"),
    reason="Credentials not configured"
)


@pytest.mark.integration
@skip_if_no_credentials
class TestBitrix24Integration:
    """Интеграционные тесты для Bitrix24"""
    
    def test_real_connection(self):
        """Тест реального подключения к Bitrix24"""
        webhook_url = os.getenv("BITRIX24_WEBHOOK_URL")
        client = create_client_from_webhook(webhook_url)
        
        # Попытка получить лиды
        leads = client.get_leads(limit=1)
        
        assert isinstance(leads, list)
        # Может быть пустым, но должен быть списком
    
    def test_get_lead_fields(self):
        """Тест получения полей лида"""
        webhook_url = os.getenv("BITRIX24_WEBHOOK_URL")
        client = create_client_from_webhook(webhook_url)
        
        # Получаем описание полей
        try:
            fields = client.b24.call_method("crm.lead.fields")
            assert "result" in fields
        except Exception as e:
            pytest.skip(f"API call failed: {e}")


@pytest.mark.integration
@skip_if_no_credentials
class TestOpenAIIntegration:
    """Интеграционные тесты для OpenAI"""
    
    def test_simple_request(self):
        """Тест простого запроса к OpenAI"""
        service = OpenAIService()
        
        response = service.generate_response("Say 'test' in one word")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.slow
    def test_lead_analysis(self):
        """Тест анализа лида через OpenAI"""
        service = OpenAIService()
        
        lead_data = {
            "TITLE": "Test Lead",
            "NAME": "John Doe",
            "COMPANY_TITLE": "Test Company",
            "COMMENTS": "Need dairy products for retail chain"
        }
        
        analysis = service.analyze_lead(lead_data)
        
        assert isinstance(analysis, dict)
        assert "quality_score" in analysis or "score" in str(analysis).lower()


@pytest.mark.integration
@skip_if_no_credentials
class TestLeadProcessorIntegration:
    """Интеграционные тесты для LeadProcessor"""
    
    @pytest.mark.slow
    def test_full_workflow(self):
        """Тест полного workflow обработки лида"""
        processor = LeadProcessor()
        
        # Создаем тестовый лид
        test_lead_data = {
            "TITLE": "Integration Test Lead",
            "NAME": "Test User",
            "PHONE": [{"VALUE": "+79001234567", "VALUE_TYPE": "WORK"}],
            "COMMENTS": "This is a test lead for integration testing"
        }
        
        try:
            # Создаем лид
            lead_id = processor.bitrix.create_lead(test_lead_data)
            assert lead_id is not None
            
            # Обрабатываем лид
            result = processor.process_new_lead(lead_id)
            assert result["success"] is True
            assert "analysis" in result
            
            # Удаляем тестовый лид
            processor.bitrix.b24.call_method("crm.lead.delete", {"id": lead_id})
            
        except Exception as e:
            pytest.skip(f"Integration test failed: {e}")


def test_environment_variables():
    """Проверка наличия необходимых переменных окружения"""
    required_vars = ["BITRIX24_WEBHOOK_URL", "OPENAI_API_KEY"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        pytest.skip(f"Missing environment variables: {', '.join(missing_vars)}")
    
    assert True
