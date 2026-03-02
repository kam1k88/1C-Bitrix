"""
Сценарий 3: Синхронизация сделки в 1С
Триггер: Сделка переходит на стадию "Счет выставлен"
"""

from bitrix24.mcp_client import Bitrix24MCPClient
from onec.client import OneCClient
import logging

logger = logging.getLogger(__name__)

def sync_deal_to_1c(deal_id: int):
    """
    Синхронизация сделки в заказ 1С
    
    Что делает:
    1. Получает сделку из Bitrix24
    2. Проверяет/создает клиента в 1С
    3. Создает заказ в 1С
    4. Обновляет сделку номером заказа
    """
    
    logger.info(f"Синхронизация сделки {deal_id} в 1С")
    
    bitrix = Bitrix24MCPClient()
    onec = OneCClient()
    
    # Получаем сделку
    deal = bitrix.get_deal(deal_id)
    
    # Получаем компанию
    company_id = deal.get("COMPANY_ID")
    if not company_id:
        raise ValueError("У сделки нет привязанной компании")
    
    companies = bitrix.get_companies({"ID": company_id})
    company = companies[0] if companies else {}
    
    # Проверяем клиента в 1С
    phone = company.get("PHONE", [{}])[0].get("VALUE", "")
    clients_1c = onec.get_counterparties({"phone": phone})
    
    if not clients_1c:
        # Создаем клиента в 1С
        client_1c = onec.sync_client_from_bitrix(company)
        client_1c_id = client_1c.get("id")
    else:
        client_1c_id = clients_1c[0]["id"]
    
    # Формируем заказ
    order_data = {
        "client_id": client_1c_id,
        "external_id": deal_id,
        "products": [
            # Здесь должны быть реальные товары из сделки
            {"product_id": "uuid-1", "quantity": 10, "price": 100}
        ]
    }
    
    # Создаем заказ в 1С
    order_result = onec.create_order(order_data)
    
    # Обновляем сделку
    bitrix.update_deal(deal_id, {
        "UF_CRM_1C_ORDER_ID": order_result.get("order_id"),
        "UF_CRM_1C_ORDER_NUMBER": order_result.get("number")
    })
    
    # Добавляем комментарий
    bitrix.add_comment(
        "deal",
        deal_id,
        f"✅ Заказ создан в 1С\nНомер: {order_result.get('number')}"
    )
    
    logger.info(f"Заказ {order_result.get('number')} создан в 1С")
    
    return order_result

if __name__ == "__main__":
    result = sync_deal_to_1c(456)
    print(f"✅ Заказ создан: {result}")
