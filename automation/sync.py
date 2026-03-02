from bitrix24.client import Bitrix24Client
from onec.client import OneCClient
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class DataSync:
    """Синхронизация данных между Bitrix24 и 1С"""
    
    def __init__(self):
        self.bitrix = Bitrix24Client()
        self.onec = OneCClient()
    
    def sync_client_to_1c(self, bitrix_client_id: int) -> Dict:
        """Синхронизация клиента из Bitrix24 в 1С"""
        try:
            # Получаем данные из Bitrix24
            client = self.bitrix._call("crm.company.get", {"id": bitrix_client_id})
            client_data = client.get("result", {})
            
            # Синхронизируем в 1С
            result = self.onec.sync_client_from_bitrix(client_data)
            
            logger.info(f"Client {bitrix_client_id} synced to 1C")
            return result
            
        except Exception as e:
            logger.error(f"Error syncing client {bitrix_client_id}: {str(e)}")
            raise
    
    def sync_deal_to_1c_order(self, deal_id: int) -> Dict:
        """Создание заказа в 1С на основе сделки Bitrix24"""
        try:
            # Получаем сделку
            deal = self.bitrix._call("crm.deal.get", {"id": deal_id})
            deal_data = deal.get("result", {})
            
            # Получаем товары сделки
            products = self.bitrix._call("crm.deal.productrows.get", {"id": deal_id})
            products_data = products.get("result", [])
            
            # Формируем заказ для 1С
            order_data = {
                "client_id": deal_data.get("COMPANY_ID"),
                "external_id": deal_id,
                "products": [
                    {
                        "product_id": p.get("PRODUCT_ID"),
                        "quantity": p.get("QUANTITY"),
                        "price": p.get("PRICE")
                    }
                    for p in products_data
                ]
            }
            
            # Создаем заказ в 1С
            result = self.onec.create_order(order_data)
            
            # Обновляем сделку в Bitrix24 с номером заказа 1С
            if result.get("order_id"):
                self.bitrix.update_deal(deal_id, {
                    "UF_CRM_1C_ORDER_ID": result["order_id"]
                })
            
            logger.info(f"Deal {deal_id} synced to 1C as order {result.get('order_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error syncing deal {deal_id}: {str(e)}")
            raise
    
    def sync_prices_from_1c(self) -> List[Dict]:
        """Синхронизация цен из 1С в Bitrix24"""
        try:
            # Получаем товары из 1С
            products_1c = self.onec.get_products()
            
            # Получаем цены
            product_ids = [p["id"] for p in products_1c]
            prices = self.onec.get_prices(product_ids)
            
            # Обновляем цены в Bitrix24
            updated = []
            for product in products_1c:
                product_id = product["id"]
                price = prices.get(product_id, {}).get("price", 0)
                
                # Находим товар в Bitrix24 по внешнему ID
                bitrix_products = self.bitrix._call("crm.product.list", {
                    "filter": {"PROPERTY_1C_ID": product_id}
                })
                
                if bitrix_products.get("result"):
                    bitrix_product = bitrix_products["result"][0]
                    # Обновляем цену
                    self.bitrix._call("crm.product.update", {
                        "id": bitrix_product["ID"],
                        "fields": {"PRICE": price}
                    })
                    updated.append({"product_id": product_id, "price": price})
            
            logger.info(f"Synced {len(updated)} prices from 1C")
            return updated
            
        except Exception as e:
            logger.error(f"Error syncing prices: {str(e)}")
            raise

# Вспомогательные функции для быстрого использования
def sync_client_to_1c(bitrix_client_id: int) -> Dict:
    """Быстрая синхронизация клиента"""
    sync = DataSync()
    return sync.sync_client_to_1c(bitrix_client_id)

def sync_deal_to_order(deal_id: int) -> Dict:
    """Быстрая синхронизация сделки в заказ"""
    sync = DataSync()
    return sync.sync_deal_to_1c_order(deal_id)
