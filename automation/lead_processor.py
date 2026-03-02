from bitrix24.sdk_client import Bitrix24SDKClient, create_client_from_webhook
from ai_services.openai_service import OpenAIService
from ai_services.claude_service import ClaudeService
from onec.client import OneCClient
from config.settings import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LeadProcessor:
    """Автоматическая обработка лидов с использованием AI"""
    
    def __init__(self, bitrix_client: Optional[Bitrix24SDKClient] = None):
        """
        Инициализация процессора лидов
        
        Args:
            bitrix_client: Опциональный клиент Bitrix24 (для тестирования)
        """
        # Создаем клиент Bitrix24 на основе конфигурации
        if bitrix_client:
            self.bitrix = bitrix_client
        elif settings.BITRIX24_WEBHOOK_URL:
            self.bitrix = create_client_from_webhook(
                settings.BITRIX24_WEBHOOK_URL,
                prefer_api_version=settings.BITRIX24_API_VERSION
            )
        elif settings.BITRIX24_ACCESS_TOKEN:
            self.bitrix = Bitrix24SDKClient(
                domain=settings.BITRIX24_DOMAIN,
                auth_token=settings.BITRIX24_ACCESS_TOKEN,
                auth_type="oauth",
                client_id=settings.BITRIX24_CLIENT_ID,
                client_secret=settings.BITRIX24_CLIENT_SECRET,
                refresh_token=settings.BITRIX24_REFRESH_TOKEN,
                prefer_api_version=settings.BITRIX24_API_VERSION
            )
        else:
            raise ValueError("Bitrix24 credentials not configured")
        
        self.openai = OpenAIService()
        self.claude = ClaudeService()
        self.onec = OneCClient()
        
        logger.info("LeadProcessor initialized with b24pysdk")
    
    def process_new_lead(self, lead_id: int) -> Dict:
        """
        Обработка нового лида с AI-анализом
        
        Args:
            lead_id: ID лида в Bitrix24
            
        Returns:
            Результат обработки с анализом и статусом
        """
        try:
            # Получаем данные лида через SDK
            lead = self.bitrix.get_lead(lead_id)
            
            # Анализируем лид через AI
            analysis = self.openai.analyze_lead(lead)
            
            # Добавляем комментарий с анализом в Bitrix24
            self.bitrix.add_comment(
                entity_type="lead",
                entity_id=lead_id, 
                comment=f"🤖 AI-Анализ:\n{analysis['analysis']}"
            )
            
            # Проверяем наличие клиента в 1С
            client_in_1c = self._check_client_in_1c(lead)
            
            logger.info(f"Lead {lead_id} processed successfully")
            
            return {
                "lead_id": lead_id,
                "analysis": analysis,
                "client_in_1c": client_in_1c,
                "status": "processed"
            }
            
        except Exception as e:
            logger.error(f"Error processing lead {lead_id}: {e}")
            raise
    
    def _check_client_in_1c(self, lead: Dict) -> bool:
        """Проверка наличия клиента в 1С"""
        try:
            phone = lead.get("PHONE", [{}])[0].get("VALUE", "")
            if phone:
                clients = self.onec.get_counterparties({"phone": phone})
                return len(clients) > 0
        except Exception:
            pass
        return False
    
    def generate_offer_for_lead(self, lead_id: int, products: list) -> str:
        """
        Генерация коммерческого предложения для лида
        
        Args:
            lead_id: ID лида в Bitrix24
            products: Список продуктов для КП
            
        Returns:
            Текст сгенерированного КП
        """
        try:
            lead = self.bitrix.get_lead(lead_id)
            
            client_info = {
                "name": lead.get("NAME"),
                "company": lead.get("COMPANY_TITLE")
            }
            
            offer = self.openai.generate_commercial_offer(client_info, products)
            
            # Сохраняем КП в комментарии
            self.bitrix.add_comment(
                entity_type="lead",
                entity_id=lead_id,
                comment=f"📄 Сгенерированное коммерческое предложение:\n\n{offer}"
            )
            
            logger.info(f"Offer generated for lead {lead_id}")
            
            return offer
            
        except Exception as e:
            logger.error(f"Error generating offer for lead {lead_id}: {e}")
            raise
