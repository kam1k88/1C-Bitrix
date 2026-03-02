"""
Клиент для работы с Bitrix24 через MCP (Model Context Protocol)
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime
import jwt

class Bitrix24MCPClient:
    """
    Клиент для работы с Bitrix24 MCP API
    Использует JWT токен для аутентификации
    """
    
    def __init__(self, mcp_url: str = None, token: str = None):
        self.mcp_url = mcp_url or os.getenv("BITRIX24_MCP_URL", "https://mcp-dev.bitrix24.tech/mcp")
        self.token = token or os.getenv("BITRIX24_MCP_TOKEN")
        self.domain = os.getenv("BITRIX24_DOMAIN", "b24-z373vc.bitrix24.ru")
        
        if not self.token:
            raise ValueError("BITRIX24_MCP_TOKEN is required")
    
    def _get_headers(self) -> Dict[str, str]:
        """Получить заголовки для запроса"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _call(self, method: str, params: Dict = None) -> Dict:
        """Базовый метод для вызова MCP API"""
        url = f"{self.mcp_url}/{method}"
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=params or {}
        )
        
        response.raise_for_status()
        return response.json()
    
    def check_token_expiry(self) -> Dict:
        """Проверить срок действия токена"""
        try:
            decoded = jwt.decode(self.token, options={"verify_signature": False})
            exp_timestamp = decoded.get("exp")
            iat_timestamp = decoded.get("iat")
            
            exp_date = datetime.fromtimestamp(exp_timestamp) if exp_timestamp else None
            iat_date = datetime.fromtimestamp(iat_timestamp) if iat_timestamp else None
            
            is_expired = exp_date < datetime.now() if exp_date else True
            days_until_expiry = (exp_date - datetime.now()).days if exp_date else 0
            
            return {
                "is_expired": is_expired,
                "issued_at": iat_date.isoformat() if iat_date else None,
                "expires_at": exp_date.isoformat() if exp_date else None,
                "days_until_expiry": days_until_expiry,
                "user_id": decoded.get("puid"),
                "domain": decoded.get("aud")
            }
        except Exception as e:
            return {"error": str(e), "is_expired": True}
    
    # CRM - Лиды
    def get_leads(self, filter_params: Dict = None, select: List[str] = None) -> List[Dict]:
        """Получить список лидов"""
        params = {
            "filter": filter_params or {},
            "select": select or ["*", "UF_*"]
        }
        result = self._call("crm.lead.list", params)
        return result.get("result", [])
    
    def get_lead(self, lead_id: int) -> Dict:
        """Получить конкретный лид"""
        result = self._call("crm.lead.get", {"id": lead_id})
        return result.get("result", {})
    
    def create_lead(self, fields: Dict) -> int:
        """Создать новый лид"""
        result = self._call("crm.lead.add", {"fields": fields})
        return result.get("result", 0)
    
    def update_lead(self, lead_id: int, fields: Dict) -> bool:
        """Обновить лид"""
        result = self._call("crm.lead.update", {"id": lead_id, "fields": fields})
        return result.get("result", False)
    
    # CRM - Сделки
    def get_deals(self, filter_params: Dict = None, select: List[str] = None) -> List[Dict]:
        """Получить список сделок"""
        params = {
            "filter": filter_params or {},
            "select": select or ["*"]
        }
        result = self._call("crm.deal.list", params)
        return result.get("result", [])
    
    def get_deal(self, deal_id: int) -> Dict:
        """Получить конкретную сделку"""
        result = self._call("crm.deal.get", {"id": deal_id})
        return result.get("result", {})
    
    def create_deal(self, fields: Dict) -> int:
        """Создать новую сделку"""
        result = self._call("crm.deal.add", {"fields": fields})
        return result.get("result", 0)
    
    def update_deal(self, deal_id: int, fields: Dict) -> bool:
        """Обновить сделку"""
        result = self._call("crm.deal.update", {"id": deal_id, "fields": fields})
        return result.get("result", False)
    
    # CRM - Контакты
    def get_contacts(self, filter_params: Dict = None) -> List[Dict]:
        """Получить список контактов"""
        params = {"filter": filter_params or {}}
        result = self._call("crm.contact.list", params)
        return result.get("result", [])
    
    def create_contact(self, fields: Dict) -> int:
        """Создать новый контакт"""
        result = self._call("crm.contact.add", {"fields": fields})
        return result.get("result", 0)
    
    # CRM - Компании
    def get_companies(self, filter_params: Dict = None) -> List[Dict]:
        """Получить список компаний"""
        params = {"filter": filter_params or {}}
        result = self._call("crm.company.list", params)
        return result.get("result", [])
    
    def create_company(self, fields: Dict) -> int:
        """Создать новую компанию"""
        result = self._call("crm.company.add", {"fields": fields})
        return result.get("result", 0)
    
    # Комментарии
    def add_comment(self, entity_type: str, entity_id: int, comment: str) -> int:
        """Добавить комментарий к сущности"""
        params = {
            "fields": {
                "ENTITY_ID": entity_id,
                "ENTITY_TYPE": entity_type,
                "COMMENT": comment
            }
        }
        result = self._call("crm.timeline.comment.add", params)
        return result.get("result", 0)
    
    # Задачи
    def get_tasks(self, filter_params: Dict = None) -> List[Dict]:
        """Получить список задач"""
        params = {"filter": filter_params or {}}
        result = self._call("tasks.task.list", params)
        return result.get("result", {}).get("tasks", [])
    
    def create_task(self, fields: Dict) -> int:
        """Создать новую задачу"""
        result = self._call("tasks.task.add", {"fields": fields})
        return result.get("result", {}).get("task", {}).get("id", 0)
    
    # Пользователи
    def get_users(self, filter_params: Dict = None) -> List[Dict]:
        """Получить список пользователей"""
        params = {"filter": filter_params or {}}
        result = self._call("user.get", params)
        return result.get("result", [])
    
    def get_current_user(self) -> Dict:
        """Получить текущего пользователя"""
        result = self._call("user.current", {})
        return result.get("result", {})

# Пример использования
if __name__ == "__main__":
    client = Bitrix24MCPClient()
    
    # Проверка токена
    token_info = client.check_token_expiry()
    print("Token Info:", token_info)
    
    if not token_info.get("is_expired"):
        # Получение лидов
        leads = client.get_leads({"STATUS_ID": "NEW"})
        print(f"Found {len(leads)} new leads")
        
        # Получение текущего пользователя
        user = client.get_current_user()
        print(f"Current user: {user.get('NAME')} {user.get('LAST_NAME')}")
    else:
        print("Token expired! Please get a new token from Bitrix24")
