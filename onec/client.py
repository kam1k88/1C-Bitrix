import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List
from config.settings import settings

class OneCClient:
    """Клиент для работы с 1С через HTTP-сервисы"""
    
    def __init__(self):
        self.base_url = settings.ONEC_BASE_URL
        self.auth = HTTPBasicAuth(settings.ONEC_USERNAME, settings.ONEC_PASSWORD)
    
    def _call(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Базовый метод для вызова 1С API"""
        url = f"{self.base_url}/hs/{endpoint}"
        
        if method == "GET":
            response = requests.get(url, auth=self.auth, params=data)
        else:
            response = requests.post(url, auth=self.auth, json=data)
        
        response.raise_for_status()
        return response.json()
    
    def get_counterparties(self, filter_params: Dict = None) -> List[Dict]:
        """Получить список контрагентов из 1С"""
        return self._call("counterparties", data=filter_params)
    
    def get_products(self, filter_params: Dict = None) -> List[Dict]:
        """Получить список товаров из 1С"""
        return self._call("products", data=filter_params)
    
    def create_order(self, order_data: Dict) -> Dict:
        """Создать заказ в 1С"""
        return self._call("orders", method="POST", data=order_data)
    
    def get_prices(self, product_ids: List[str]) -> Dict:
        """Получить цены на товары"""
        return self._call("prices", data={"products": product_ids})
    
    def sync_client_from_bitrix(self, bitrix_client: Dict) -> Dict:
        """Синхронизация клиента из Bitrix24 в 1С"""
        client_data = {
            "name": bitrix_client.get("TITLE"),
            "inn": bitrix_client.get("UF_CRM_INN"),
            "phone": bitrix_client.get("PHONE"),
            "email": bitrix_client.get("EMAIL"),
            "external_id": bitrix_client.get("ID")
        }
        return self._call("counterparties/sync", method="POST", data=client_data)
