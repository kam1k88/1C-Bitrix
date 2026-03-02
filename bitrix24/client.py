import requests
from typing import Dict, List, Optional
from config.settings import settings

class Bitrix24Client:
    """Клиент для работы с Bitrix24 API"""
    
    def __init__(self):
        self.webhook_url = settings.BITRIX24_WEBHOOK_URL
    
    def _call(self, method: str, params: Dict = None) -> Dict:
        """Базовый метод для вызова API Bitrix24"""
        url = f"{self.webhook_url}{method}"
        response = requests.post(url, json=params or {})
        response.raise_for_status()
        return response.json()
    
    def get_leads(self, filter_params: Dict = None) -> List[Dict]:
        """Получить список лидов"""
        params = {"filter": filter_params or {}, "select": ["*", "UF_*"]}
        result = self._call("crm.lead.list", params)
        return result.get("result", [])
    
    def get_lead(self, lead_id: int) -> Dict:
        """Получить информацию о лиде"""
        result = self._call("crm.lead.get", {"id": lead_id})
        return result.get("result", {})
    
    def update_lead(self, lead_id: int, fields: Dict) -> bool:
        """Обновить лид"""
        params = {"id": lead_id, "fields": fields}
        result = self._call("crm.lead.update", params)
        return result.get("result", False)
    
    def add_comment(self, lead_id: int, comment: str) -> int:
        """Добавить комментарий к лиду"""
        params = {
            "fields": {
                "ENTITY_ID": lead_id,
                "ENTITY_TYPE": "lead",
                "COMMENT": comment
            }
        }
        result = self._call("crm.timeline.comment.add", params)
        return result.get("result", 0)
    
    def get_deals(self, filter_params: Dict = None) -> List[Dict]:
        """Получить список сделок"""
        params = {"filter": filter_params or {}, "select": ["*"]}
        result = self._call("crm.deal.list", params)
        return result.get("result", [])
