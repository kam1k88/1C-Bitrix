"""
Ozon Marketplace Connector
Синхронизация товаров, заказов и остатков с Ozon
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OzonConnector:
    """Коннектор для интеграции с Ozon Seller API"""
    
    def __init__(self, client_id: str, api_key: str):
        self.client_id = client_id
        self.api_key = api_key
        self.base_url = "https://api-seller.ozon.ru"
        self.headers = {
            "Client-Id": client_id,
            "Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def _call(self, endpoint: str, method: str = "POST", data: Dict = None) -> Dict:
        """Базовый метод для вызова API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "POST":
                response = requests.post(url, headers=self.headers, json=data or {})
            else:
                response = requests.get(url, headers=self.headers, params=data or {})
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ozon API error: {str(e)}")
            raise
    
    # === Товары ===
    
    def get_products(self, limit: int = 100) -> List[Dict]:
        """Получить список товаров"""
        data = {
            "filter": {},
            "limit": limit,
            "last_id": ""
        }
        result = self._call("/v2/product/list", data=data)
        return result.get("result", {}).get("items", [])
    
    def get_product_info(self, product_id: int) -> Dict:
        """Получить информацию о товаре"""
        data = {"product_id": product_id}
        result = self._call("/v2/product/info", data=data)
        return result.get("result", {})
    
    def update_product_stocks(self, stocks: List[Dict]) -> Dict:
        """
        Обновить остатки товаров
        
        stocks = [
            {"offer_id": "SKU123", "stock": 10, "warehouse_id": 123},
            ...
        ]
        """
        data = {"stocks": stocks}
        return self._call("/v1/product/import/stocks", data=data)
    
    def update_product_prices(self, prices: List[Dict]) -> Dict:
        """
        Обновить цены товаров
        
        prices = [
            {
                "offer_id": "SKU123",
                "price": "1000",
                "old_price": "1200",
                "currency_code": "RUB"
            },
            ...
        ]
        """
        data = {"prices": prices}
        return self._call("/v1/product/import/prices", data=data)
    
    def create_product(self, product_data: Dict) -> Dict:
        """
        Создать новый товар
        
        product_data = {
            "name": "Название товара",
            "offer_id": "SKU123",
            "category_id": 123,
            "price": "1000",
            "old_price": "1200",
            "vat": "0.2",
            "images": ["https://..."],
            "attributes": [...]
        }
        """
        data = {"items": [product_data]}
        return self._call("/v2/product/import", data=data)
    
    # === Заказы ===
    
    def get_orders(self, status: str = None, since: datetime = None) -> List[Dict]:
        """
        Получить список заказов
        
        status: awaiting_packaging, awaiting_deliver, delivered, cancelled
        """
        data = {
            "dir": "ASC",
            "filter": {},
            "limit": 100,
            "offset": 0,
            "with": {
                "analytics_data": True,
                "financial_data": True
            }
        }
        
        if status:
            data["filter"]["status"] = status
        
        if since:
            data["filter"]["since"] = since.isoformat()
        
        result = self._call("/v3/posting/fbs/list", data=data)
        return result.get("result", {}).get("postings", [])
    
    def get_order_details(self, posting_number: str) -> Dict:
        """Получить детали заказа"""
        data = {
            "posting_number": posting_number,
            "with": {
                "analytics_data": True,
                "financial_data": True
            }
        }
        result = self._call("/v3/posting/fbs/get", data=data)
        return result.get("result", {})
    
    def ship_order(self, posting_number: str, packages: List[Dict]) -> Dict:
        """
        Отгрузить заказ
        
        packages = [
            {
                "products": [
                    {"product_id": 123, "quantity": 1}
                ]
            }
        ]
        """
        data = {
            "posting_number": posting_number,
            "packages": packages
        }
        return self._call("/v3/posting/fbs/ship", data=data)
    
    def cancel_order(self, posting_number: str, cancel_reason_id: int) -> Dict:
        """Отменить заказ"""
        data = {
            "posting_number": posting_number,
            "cancel_reason_id": cancel_reason_id
        }
        return self._call("/v2/posting/fbs/cancel", data=data)
    
    # === Аналитика ===
    
    def get_analytics_data(self, date_from: datetime, date_to: datetime) -> Dict:
        """Получить аналитику продаж"""
        data = {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "metrics": [
                "revenue",
                "ordered_units",
                "returns"
            ],
            "dimension": ["day"],
            "filters": [],
            "sort": [{"key": "date", "order": "ASC"}],
            "limit": 1000,
            "offset": 0
        }
        result = self._call("/v1/analytics/data", data=data)
        return result.get("result", {})
    
    def get_stock_on_warehouses(self) -> List[Dict]:
        """Получить остатки на складах"""
        data = {}
        result = self._call("/v3/product/info/stocks", data=data)
        return result.get("result", {}).get("items", [])
    
    # === Финансы ===
    
    def get_finance_transactions(self, date_from: datetime, date_to: datetime) -> List[Dict]:
        """Получить финансовые транзакции"""
        data = {
            "filter": {
                "date": {
                    "from": date_from.isoformat(),
                    "to": date_to.isoformat()
                }
            },
            "page": 1,
            "page_size": 1000
        }
        result = self._call("/v3/finance/transaction/list", data=data)
        return result.get("result", {}).get("operations", [])
    
    # === Интеграция с Bitrix24 ===
    
    def sync_to_bitrix24(self, bitrix_client) -> Dict:
        """
        Синхронизация с Bitrix24
        
        1. Получить новые заказы из Ozon
        2. Создать сделки в Bitrix24
        3. Обновить остатки
        """
        try:
            # Получаем новые заказы
            orders = self.get_orders(status="awaiting_packaging")
            
            synced = 0
            for order in orders:
                try:
                    # Создаем сделку в Bitrix24
                    deal_data = {
                        "TITLE": f"Заказ Ozon #{order['posting_number']}",
                        "STAGE_ID": "NEW",
                        "OPPORTUNITY": order.get("financial_data", {}).get("products_price", 0),
                        "CURRENCY_ID": "RUB",
                        "SOURCE_ID": "OZON",
                        "COMMENTS": f"Заказ с Ozon. Номер: {order['posting_number']}"
                    }
                    
                    # Создаем сделку
                    deal_result = bitrix_client._call("crm.deal.add", {"fields": deal_data})
                    
                    if deal_result.get("result"):
                        synced += 1
                        logger.info(f"Order {order['posting_number']} synced to Bitrix24")
                
                except Exception as e:
                    logger.error(f"Error syncing order {order.get('posting_number')}: {str(e)}")
            
            return {
                "success": True,
                "total_orders": len(orders),
                "synced": synced
            }
        
        except Exception as e:
            logger.error(f"Sync error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Пример использования
if __name__ == "__main__":
    # Инициализация
    ozon = OzonConnector(
        client_id="your_client_id",
        api_key="your_api_key"
    )
    
    # Получить товары
    products = ozon.get_products()
    print(f"Товаров на Ozon: {len(products)}")
    
    # Получить заказы
    orders = ozon.get_orders(status="awaiting_packaging")
    print(f"Заказов в обработке: {len(orders)}")
    
    # Обновить остатки
    stocks = [
        {"offer_id": "SKU123", "stock": 10, "warehouse_id": 123}
    ]
    result = ozon.update_product_stocks(stocks)
    print(f"Остатки обновлены: {result}")
