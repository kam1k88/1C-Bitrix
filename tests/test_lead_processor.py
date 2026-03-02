"""
Тесты для LeadProcessor
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from automation.lead_processor import LeadProcessor


class TestLeadProcessor:
    """Тесты для LeadProcessor"""
    
    @patch('automation.lead_processor.Bitrix24SDKClient')
    @patch('automation.lead_processor.OpenAIService')
    @patch('automation.lead_processor.ClaudeService')
    @patch('automation.lead_processor.OneCClient')
    def test_init(self, mock_onec, mock_claude, mock_openai, mock_bitrix):
        """Тест инициализации LeadProcessor"""
        processor = LeadProcessor()
        
        assert processor.bitrix is not None
        assert processor.openai is not None
        assert processor.claude is not None
        assert processor.onec is not None
    
    @patch('automation.lead_processor.Bitrix24SDKClient')
    @patch('automation.lead_processor.OpenAIService')
    @patch('automation.lead_processor.ClaudeService')
    @patch('automation.lead_processor.OneCClient')
    def test_process_new_lead_success(self, mock_onec, mock_claude, mock_openai, mock_bitrix):
        """Тест успешной обработки нового лида"""
        # Настройка моков
        mock_bitrix_instance = MagicMock()
        mock_bitrix.return_value = mock_bitrix_instance
        
        mock_bitrix_instance.get_lead.return_value = {
            "ID": "123",
            "TITLE": "Test Lead",
            "NAME": "John Doe",
            "PHONE": [{"VALUE": "+79001234567"}],
            "COMMENTS": "Need dairy products"
        }
        
        mock_openai_instance = MagicMock()
        mock_openai.return_value = mock_openai_instance
        
        mock_openai_instance.analyze_lead.return_value = {
            "quality_score": 8,
            "probability": 75,
            "recommendations": "Contact within 2 hours"
        }
        
        mock_bitrix_instance.add_comment_to_lead.return_value = True
        
        # Выполнение теста
        processor = LeadProcessor()
        result = processor.process_new_lead(123)
        
        # Проверки
        assert result["success"] is True
        assert "analysis" in result
        assert result["analysis"]["quality_score"] == 8
        mock_bitrix_instance.get_lead.assert_called_once_with(123)
        mock_openai_instance.analyze_lead.assert_called_once()
    
    @patch('automation.lead_processor.Bitrix24SDKClient')
    @patch('automation.lead_processor.OpenAIService')
    @patch('automation.lead_processor.ClaudeService')
    @patch('automation.lead_processor.OneCClient')
    def test_process_new_lead_not_found(self, mock_onec, mock_claude, mock_openai, mock_bitrix):
        """Тест обработки несуществующего лида"""
        mock_bitrix_instance = MagicMock()
        mock_bitrix.return_value = mock_bitrix_instance
        
        mock_bitrix_instance.get_lead.return_value = None
        
        processor = LeadProcessor()
        result = processor.process_new_lead(999)
        
        assert result["success"] is False
        assert "error" in result
    
    @patch('automation.lead_processor.Bitrix24SDKClient')
    @patch('automation.lead_processor.OpenAIService')
    @patch('automation.lead_processor.ClaudeService')
    @patch('automation.lead_processor.OneCClient')
    def test_generate_offer_for_lead(self, mock_onec, mock_claude, mock_openai, mock_bitrix):
        """Тест генерации КП для лида"""
        mock_bitrix_instance = MagicMock()
        mock_bitrix.return_value = mock_bitrix_instance
        
        mock_bitrix_instance.get_lead.return_value = {
            "ID": "123",
            "TITLE": "Test Lead",
            "NAME": "John Doe",
            "COMPANY_TITLE": "Test Company"
        }
        
        mock_openai_instance = MagicMock()
        mock_openai.return_value = mock_openai_instance
        
        mock_openai_instance.generate_offer.return_value = "Commercial offer text..."
        
        processor = LeadProcessor()
        result = processor.generate_offer_for_lead(
            123,
            products=["Milk 3.2%", "Kefir 2.5%"]
        )
        
        assert result["success"] is True
        assert "offer" in result
        assert result["offer"] == "Commercial offer text..."
