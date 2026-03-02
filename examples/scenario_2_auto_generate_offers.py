"""
Сценарий 2: Автоматическая генерация КП
Триггер: Сделка переходит на стадию "Подготовка КП"
"""

from bitrix24.mcp_client import Bitrix24MCPClient
from ai_services.openai_service import OpenAIService
import logging

logger = logging.getLogger(__name__)

def auto_generate_offer(deal_id: int):
    """
    Автоматическая генерация КП для сделки
    
    Что делает:
    1. Получает информацию о сделке и клиенте
    2. Получает список товаров из сделки
    3. Генерирует персонализированное КП через AI
    4. Добавляет КП в комментарии
    5. Переводит сделку на следующую стадию
    """
    
    logger.info(f"Генерация КП для сделки {deal_id}")
    
    bitrix = Bitrix24MCPClient()
    ai = OpenAIService()
    
    # Получаем сделку
    deal = bitrix.get_deal(deal_id)
    
    # Получаем информацию о клиенте
    company_id = deal.get("COMPANY_ID")
    if company_id:
        companies = bitrix.get_companies({"ID": company_id})
        company = companies[0] if companies else {}
    else:
        company = {}
    
    # Формируем информацию о клиенте
    client_info = {
        "name": deal.get("TITLE"),
        "company": company.get("TITLE", ""),
        "contact": deal.get("CONTACT_ID")
    }
    
    # Получаем товары (упрощенный пример)
    products = [
        "Молоко 3.2%",
        "Кефир 2.5%",
        "Творог 9%"
    ]
    
    # Генерируем КП
    offer = ai.generate_commercial_offer(client_info, products)
    
    # Добавляем КП в комментарии
    comment = f"""📄 Коммерческое предложение
Сгенерировано: {datetime.now().strftime("%d.%m.%Y %H:%M")}

{offer}

---
Автоматически создано AI Integration Platform
"""
    
    bitrix.add_comment("deal", deal_id, comment)
    
    # Переводим на следующую стадию
    bitrix.update_deal(deal_id, {
        "STAGE_ID": "C1:PREPAYMENT_INVOICE"  # КП отправлено
    })
    
    logger.info(f"КП для сделки {deal_id} создано")
    
    return {"deal_id": deal_id, "offer_length": len(offer)}

if __name__ == "__main__":
    # Пример использования
    result = auto_generate_offer(123)
    print(f"✅ КП создано: {result}")
