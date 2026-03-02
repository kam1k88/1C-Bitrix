"""
Тесты для Bitrix24 SDK Client
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from bitrix24.sdk_client import Bitrix24SDKClient, create_client_from_webhook


class TestBitrix24SDKClient:
    """Тесты для Bitrix24SDKClient"""
    
    @patch('bitrix24.sdk_client.Bitrix24')
    def test_init_with_webhook(self, mock_bitrix):
        """Тест инициализации с webhook"""
        webhook_url = "https://test.bitrix24.ru/rest/1/xxxxx/"
        
        client = Bitrix24SDKClient(webhook_url=webhook_url)
        
        assert client.webhook_url == webhook_url
        assert client.b24 is not None
        mock_bitrix.assert_called_once()
    
    @patch('bitrix24.sdk_client.Bitrix24')
    def test_init_with_oauth(self, mock_bitrix):
        """Тест инициализации с OAuth"""
        client = Bitrix24SDKClient(
            domain="test.bitrix24.ru",
            client_id="test_id",
            client_secret="test_secret",
            access_token="test_token"
        )
        
        assert client.domain == "test.bitrix24.ru"
        assert client.b24 is not None
    
    def test_init_without_credentials(self):
        """Тест инициализации без учетных данных"""
        with pytest.raises(ValueError, match="Either webhook_url or OAuth credentials must be provided"):
            Bitrix24SDKClient()
    
    @patch('bitrix24.sdk_client.Bitrix24')
    def test_get_leads(self, mock_bitrix):
        """Тест получения лидов"""
        mock_b24_instance = MagicMock()
        mock_bitrix.return_value = mock_b24_instance
        
        # Мокаем метод get_all
        mock_b24_instance.get_all.return_value = [
            {"ID": "1", "TITLE": "Test Lead 1"},
            {"ID": "2", "TITLE": "Test Lead 2"}
        ]
        
        client = Bitrix24SDKClient(webhook_url="https://test.bitrix24.ru/rest/1/xxxxx/")
        leads = client.get_leads(filter_params={"STATUS_ID": "NEW"})
        
        assert len(leads) == 2
        assert leads[0]["ID"] == "1"
        mock_b24_instance.get_all.assert_called_once()
    
    @patch('bitrix24.sdk_client.Bitrix24')
    def test_get_lead(self, mock_bitrix):
        """Тест получения одного лида"""
        mock_b24_instance = MagicMock()
        mock_bitrix.return_value = mock_b24_instance
        
        mock_b24_instance.call_method.return_value = {
            "result": {"ID": "123", "TITLE": "Test Lead"}
        }
        
        client = Bitrix24SDKClient(webhook_url="https://test.bitrix24.ru/rest/1/xxxxx/")
        lead = client.get_lead(123)
        
        assert lead["ID"] == "123"
        assert lead["TITLE"] == "Test Lead"
    
    @patch('bitrix24.sdk_client.Bitrix24')
    def test_update_lead(self, mock_bitrix):
        """Тест обновления лида"""
        mock_b24_instance = MagicMock()
        mock_bitrix.return_value = mock_b24_instance
        
        mock_b24_instance.call_method.return_value = {"result": True}
        
        client = Bitrix24SDKClient(webhook_url="https://test.bitrix24.ru/rest/1/xxxxx/")
        result = client.update_lead(123, {"TITLE": "Updated Title"})
        
        assert result is True
    
    @patch('bitrix24.sdk_client.Bitrix24')
    def test_create_lead(self, mock_bitrix):
        """Тест создания лида"""
        mock_b24_instance = MagicMock()
        mock_bitrix.return_value = mock_b24_instance
        
        mock_b24_instance.call_method.return_value = {"result": 456}
        
        client = Bitrix24SDKClient(webhook_url="https://test.bitrix24.ru/rest/1/xxxxx/")
        lead_id = client.create_lead({"TITLE": "New Lead", "NAME": "John"})
        
        assert lead_id == 456
    
    @patch('bitrix24.sdk_client.Bitrix24')
    def test_batch_update_leads(self, mock_bitrix):
        """Тест массового обновления лидов"""
        mock_b24_instance = MagicMock()
        mock_bitrix.return_value = mock_b24_instance
        
        mock_b24_instance.call_batch.return_value = {
            "result": {
                "result": [True, True, True]
            }
        }
        
        client = Bitrix24SDKClient(webhook_url="https://test.bitrix24.ru/rest/1/xxxxx/")
        updates = [
            (1, {"STATUS_ID": "CONVERTED"}),
            (2, {"STATUS_ID": "CONVERTED"}),
            (3, {"STATUS_ID": "CONVERTED"})
        ]
        
        results = client.batch_update_leads(updates)
        
        assert len(results) == 3
        assert all(results)


class TestCreateClientFromWebhook:
    """Тесты для фабричной функции"""
    
    @patch('bitrix24.sdk_client.Bitrix24SDKClient')
    def test_create_client_from_webhook(self, mock_client):
        """Тест создания клиента из webhook URL"""
        webhook_url = "https://test.bitrix24.ru/rest/1/xxxxx/"
        
        client = create_client_from_webhook(webhook_url)
        
        mock_client.assert_called_once_with(webhook_url=webhook_url)
