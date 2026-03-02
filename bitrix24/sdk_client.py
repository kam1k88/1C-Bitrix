"""
Bitrix24 клиент на основе официального SDK b24pysdk
Поддерживает webhook и OAuth аутентификацию
"""

from typing import Dict, List, Optional, Union
from b24pysdk import Client, BitrixWebhook, BitrixToken, BitrixApp
from b24pysdk import Config
from b24pysdk.log import StreamLogger
from b24pysdk.error import BitrixAPIError, BitrixRequestTimeout, BitrixAPIExpiredToken
from b24pysdk.constants.crm import EntityTypeID
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class Bitrix24SDKClient:
    """
    Обертка над b24pysdk для упрощенной работы с Bitrix24 API
    """
    
    def __init__(
        self,
        domain: str,
        auth_token: str,
        auth_type: str = "webhook",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        prefer_api_version: int = 2
    ):
        """
        Инициализация клиента
        
        Args:
            domain: Домен портала (example.bitrix24.com)
            auth_token: Токен аутентификации (webhook или OAuth)
            auth_type: Тип аутентификации ("webhook" или "oauth")
            client_id: ID приложения (для OAuth)
            client_secret: Секрет приложения (для OAuth)
            refresh_token: Refresh token (для OAuth)
            prefer_api_version: Предпочитаемая версия API (2 или 3)
        """
        self.domain = domain
        self.auth_type = auth_type
        
        # Настройка конфигурации SDK
        cfg = Config()
        cfg.configure(
            default_timeout=(3.05, 10),
            default_max_retries=3,
            default_initial_retry_delay=1,
            default_retry_delay_increment=1,
            logger=StreamLogger()
        )
        
        # Создание аутентификатора
        if auth_type == "webhook":
            bitrix_auth = BitrixWebhook(domain=domain, auth_token=auth_token)
        elif auth_type == "oauth":
            if not client_id or not client_secret:
                raise ValueError("client_id and client_secret required for OAuth")
            
            bitrix_app = BitrixApp(client_id=client_id, client_secret=client_secret)
            bitrix_auth = BitrixToken(
                domain=domain,
                auth_token=auth_token,
                refresh_token=refresh_token,
                bitrix_app=bitrix_app,
                expires_in=3600
            )
        else:
            raise ValueError(f"Unknown auth_type: {auth_type}")
        
        # Создание клиента
        self.client = Client(bitrix_auth, prefer_version=prefer_api_version)
        logger.info(f"Bitrix24 SDK client initialized (auth={auth_type}, api_v{prefer_api_version})")
    
    # === CRM - Лиды ===
    
    def get_leads(
        self, 
        filter_params: Optional[Dict] = None,
        select: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Получить список лидов
        
        Args:
            filter_params: Параметры фильтрации
            select: Поля для выборки
            limit: Максимальное количество записей (None = все)
        """
        try:
            request = self.client.crm.lead.list(
                filter=filter_params or {},
                select=select or ["*", "UF_*"]
            )
            
            if limit:
                return request.result[:limit]
            
            # Получить все записи с автоматической пагинацией
            return request.as_list_fast().result
            
        except BitrixAPIError as e:
            logger.error(f"Bitrix API error getting leads: {e.error} - {e.error_description}")
            raise
        except BitrixRequestTimeout:
            logger.error("Request timeout getting leads")
            raise
    
    def get_lead(self, lead_id: int) -> Dict:
        """Получить информацию о лиде"""
        try:
            request = self.client.crm.lead.get(bitrix_id=lead_id)
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error getting lead {lead_id}: {e.error}")
            raise
    
    def create_lead(self, fields: Dict) -> int:
        """Создать новый лид"""
        try:
            request = self.client.crm.lead.add(fields=fields)
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error creating lead: {e.error}")
            raise
    
    def update_lead(self, lead_id: int, fields: Dict) -> bool:
        """Обновить лид"""
        try:
            request = self.client.crm.lead.update(bitrix_id=lead_id, fields=fields)
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error updating lead {lead_id}: {e.error}")
            raise
    
    def delete_lead(self, lead_id: int) -> bool:
        """Удалить лид"""
        try:
            request = self.client.crm.lead.delete(bitrix_id=lead_id)
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error deleting lead {lead_id}: {e.error}")
            raise
    
    # === CRM - Сделки ===
    
    def get_deals(
        self,
        filter_params: Optional[Dict] = None,
        select: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Получить список сделок"""
        try:
            request = self.client.crm.deal.list(
                filter=filter_params or {},
                select=select or ["*"]
            )
            
            if limit:
                return request.result[:limit]
            
            return request.as_list_fast().result
            
        except BitrixAPIError as e:
            logger.error(f"Error getting deals: {e.error}")
            raise
    
    def get_deal(self, deal_id: int) -> Dict:
        """Получить информацию о сделке"""
        try:
            request = self.client.crm.deal.get(bitrix_id=deal_id)
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error getting deal {deal_id}: {e.error}")
            raise
    
    def create_deal(self, fields: Dict) -> int:
        """Создать новую сделку"""
        try:
            request = self.client.crm.deal.add(fields=fields)
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error creating deal: {e.error}")
            raise
    
    def update_deal(self, deal_id: int, fields: Dict) -> bool:
        """Обновить сделку"""
        try:
            request = self.client.crm.deal.update(bitrix_id=deal_id, fields=fields)
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error updating deal {deal_id}: {e.error}")
            raise
    
    # === CRM - Контакты ===
    
    def get_contacts(
        self,
        filter_params: Optional[Dict] = None,
        select: Optional[List[str]] = None
    ) -> List[Dict]:
        """Получить список контактов"""
        try:
            request = self.client.crm.contact.list(
                filter=filter_params or {},
                select=select or ["*"]
            )
            return request.as_list_fast().result
        except BitrixAPIError as e:
            logger.error(f"Error getting contacts: {e.error}")
            raise
    
    def create_contact(self, fields: Dict) -> int:
        """Создать новый контакт"""
        try:
            request = self.client.crm.contact.add(fields=fields)
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error creating contact: {e.error}")
            raise
    
    # === CRM - Компании ===
    
    def get_companies(
        self,
        filter_params: Optional[Dict] = None,
        select: Optional[List[str]] = None
    ) -> List[Dict]:
        """Получить список компаний"""
        try:
            request = self.client.crm.company.list(
                filter=filter_params or {},
                select=select or ["*"]
            )
            return request.as_list_fast().result
        except BitrixAPIError as e:
            logger.error(f"Error getting companies: {e.error}")
            raise
    
    def create_company(self, fields: Dict) -> int:
        """Создать новую компанию"""
        try:
            request = self.client.crm.company.add(fields=fields)
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error creating company: {e.error}")
            raise
    
    # === Batch операции ===
    
    def batch_update_leads(self, updates: List[Dict[str, Union[int, Dict]]]) -> List[bool]:
        """
        Массовое обновление лидов
        
        Args:
            updates: Список словарей с ключами 'id' и 'fields'
        
        Returns:
            Список результатов обновления
        """
        try:
            requests_data = {
                f"lead_{update['id']}": self.client.crm.lead.update(
                    bitrix_id=update['id'],
                    fields=update['fields']
                )
                for update in updates
            }
            
            batch_request = self.client.call_batch(requests_data)
            return [result for result in batch_request.result.result.values()]
            
        except BitrixAPIError as e:
            logger.error(f"Error in batch update: {e.error}")
            raise
    
    def batch_create_deals(self, deals_data: List[Dict]) -> List[int]:
        """
        Массовое создание сделок
        
        Args:
            deals_data: Список словарей с полями сделок
        
        Returns:
            Список ID созданных сделок
        """
        try:
            requests = [
                self.client.crm.deal.add(fields=deal_fields)
                for deal_fields in deals_data
            ]
            
            batches_request = self.client.call_batches(requests)
            return list(batches_request.result.result)
            
        except BitrixAPIError as e:
            logger.error(f"Error in batch create: {e.error}")
            raise
    
    # === Комментарии ===
    
    def add_comment(self, entity_type: str, entity_id: int, comment: str) -> int:
        """
        Добавить комментарий к сущности CRM
        
        Args:
            entity_type: Тип сущности (lead, deal, contact, company)
            entity_id: ID сущности
            comment: Текст комментария
        """
        try:
            # Используем прямой вызов, т.к. timeline может не иметь обертки
            request = self.client.call(
                "crm.timeline.comment.add",
                fields={
                    "ENTITY_ID": entity_id,
                    "ENTITY_TYPE": entity_type,
                    "COMMENT": comment
                }
            )
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error adding comment: {e.error}")
            raise
    
    # === Пользователи ===
    
    def get_users(self, filter_params: Optional[Dict] = None) -> List[Dict]:
        """Получить список пользователей"""
        try:
            request = self.client.user.get(filter=filter_params or {})
            return request.as_list_fast().result
        except BitrixAPIError as e:
            logger.error(f"Error getting users: {e.error}")
            raise
    
    def get_current_user(self) -> Dict:
        """Получить текущего пользователя"""
        try:
            request = self.client.user.current()
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error getting current user: {e.error}")
            raise
    
    # === Утилиты ===
    
    def get_fields(self, entity_type: str) -> Dict:
        """
        Получить описание полей сущности
        
        Args:
            entity_type: Тип сущности (lead, deal, contact, company)
        """
        try:
            if entity_type == "lead":
                request = self.client.crm.lead.fields()
            elif entity_type == "deal":
                request = self.client.crm.deal.fields()
            elif entity_type == "contact":
                request = self.client.crm.contact.fields()
            elif entity_type == "company":
                request = self.client.crm.company.fields()
            else:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            return request.result
        except BitrixAPIError as e:
            logger.error(f"Error getting fields for {entity_type}: {e.error}")
            raise


def create_client_from_webhook(webhook_url: str, prefer_api_version: int = 2) -> Bitrix24SDKClient:
    """
    Фабрика для создания клиента из webhook URL
    
    Args:
        webhook_url: Полный URL вебхука (https://example.bitrix24.com/rest/1/xxx/)
        prefer_api_version: Версия API (2 или 3)
    
    Returns:
        Настроенный клиент
    """
    # Парсинг webhook URL
    # Формат: https://domain/rest/user_id/webhook_key/
    parts = webhook_url.rstrip('/').split('/')
    domain = parts[2]  # example.bitrix24.com
    user_id = parts[4]
    webhook_key = parts[5]
    auth_token = f"{user_id}/{webhook_key}"
    
    return Bitrix24SDKClient(
        domain=domain,
        auth_token=auth_token,
        auth_type="webhook",
        prefer_api_version=prefer_api_version
    )
