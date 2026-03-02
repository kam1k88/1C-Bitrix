from bitrix24.client import Bitrix24Client
from ai_services.openai_service import OpenAIService
from ai_services.claude_service import ClaudeService
from onec.client import OneCClient
from typing import Dict

class LeadProcessor:
    """Автоматическая обработка лидов с использованием AI"""
    
    def __init__(self):
        self.bitrix = Bitrix24Client()
        self.openai = OpenAIService()
        self.claude = ClaudeService()
        self.onec = OneCClient()
    
    def process_new_lead(self, lead_id: int) -> Dict:
        """Обработка нового лида"""
        # Получаем данные лида
        lead = self.bitrix.get_lead(lead_id)
        
        # Анализируем лид через AI
        analysis = self.openai.analyze_lead(lead)
        
        # Добавляем комментарий с анализом в Bitrix24
        self.bitrix.add_comment(
            lead_id, 
            f"🤖 AI-Анализ:\n{analysis['analysis']}"
        )
        
        # Проверяем наличие клиента в 1С
        client_in_1c = self._check_client_in_1c(lead)
        
        return {
            "lead_id": lead_id,
            "analysis": analysis,
            "client_in_1c": client_in_1c,
            "status": "processed"
        }
    
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
        """Генерация КП для лида"""
        lead = self.bitrix.get_lead(lead_id)
        
        client_info = {
            "name": lead.get("NAME"),
            "company": lead.get("COMPANY_TITLE")
        }
        
        offer = self.openai.generate_commercial_offer(client_info, products)
        
        # Сохраняем КП в комментарии
        self.bitrix.add_comment(
            lead_id,
            f"📄 Сгенерированное коммерческое предложение:\n\n{offer}"
        )
        
        return offer
