"""
Массовые операции с использованием Bitrix24 JS SDK
"""

from typing import List, Dict, Callable
from bitrix24.client import Bitrix24Client
from ai_services.openai_service import OpenAIService
from ai_services.claude_service import ClaudeService
import logging

logger = logging.getLogger(__name__)

class MassOperations:
    """Массовые операции над данными CRM"""
    
    def __init__(self):
        self.bitrix = Bitrix24Client()
        self.openai = OpenAIService()
        self.claude = ClaudeService()
    
    def analyze_all_new_leads(self) -> Dict:
        """
        Массовый анализ всех новых лидов через AI
        Использует batch запросы для оптимизации
        """
        try:
            # Получаем все новые лиды
            leads = self.bitrix.get_leads({"STATUS_ID": "NEW"})
            
            logger.info(f"Found {len(leads)} new leads to analyze")
            
            # Анализируем каждый лид
            analyses = []
            for lead in leads:
                try:
                    analysis = self.openai.analyze_lead(lead)
                    analyses.append({
                        "lead_id": lead["ID"],
                        "analysis": analysis
                    })
                except Exception as e:
                    logger.error(f"Error analyzing lead {lead['ID']}: {str(e)}")
            
            # Формируем batch запрос для обновления всех лидов
            batch_commands = []
            for item in analyses:
                comment = f"""🤖 AI-Анализ:
{item['analysis']['analysis']}

Оценка: {item['analysis'].get('score', 'N/A')}/10
Вероятность конверсии: {item['analysis'].get('probability', 'N/A')}%
"""
                
                # Добавляем комментарий
                batch_commands.append({
                    "method": "crm.timeline.comment.add",
                    "params": {
                        "fields": {
                            "ENTITY_ID": item["lead_id"],
                            "ENTITY_TYPE": "lead",
                            "COMMENT": comment
                        }
                    }
                })
            
            # Выполняем batch запрос (до 50 команд за раз)
            results = []
            for i in range(0, len(batch_commands), 50):
                chunk = batch_commands[i:i+50]
                result = self.bitrix._call("batch", {"cmd": chunk})
                results.append(result)
            
            logger.info(f"Successfully analyzed {len(analyses)} leads")
            
            return {
                "total_leads": len(leads),
                "analyzed": len(analyses),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in mass lead analysis: {str(e)}")
            raise
    
    def generate_offers_for_deals(self, stage_id: str, products: List[str]) -> Dict:
        """
        Генерация КП для всех сделок на определенной стадии
        """
        try:
            # Получаем сделки на нужной стадии
            deals = self.bitrix.get_deals({"STAGE_ID": stage_id})
            
            logger.info(f"Found {len(deals)} deals in stage {stage_id}")
            
            generated = []
            for deal in deals:
                try:
                    # Получаем информацию о клиенте
                    company_id = deal.get("COMPANY_ID")
                    if not company_id:
                        continue
                    
                    company = self.bitrix._call("crm.company.get", {"id": company_id})
                    company_data = company.get("result", {})
                    
                    client_info = {
                        "name": deal.get("TITLE"),
                        "company": company_data.get("TITLE")
                    }
                    
                    # Генерируем КП
                    offer = self.openai.generate_commercial_offer(client_info, products)
                    
                    # Добавляем комментарий со сгенерированным КП
                    self.bitrix._call("crm.timeline.comment.add", {
                        "fields": {
                            "ENTITY_ID": deal["ID"],
                            "ENTITY_TYPE": "deal",
                            "COMMENT": f"📄 Сгенерированное КП:\n\n{offer}"
                        }
                    })
                    
                    generated.append({
                        "deal_id": deal["ID"],
                        "offer_length": len(offer)
                    })
                    
                except Exception as e:
                    logger.error(f"Error generating offer for deal {deal['ID']}: {str(e)}")
            
            logger.info(f"Generated {len(generated)} offers")
            
            return {
                "total_deals": len(deals),
                "generated": len(generated),
                "details": generated
            }
            
        except Exception as e:
            logger.error(f"Error in mass offer generation: {str(e)}")
            raise
    
    def categorize_all_requests(self) -> Dict:
        """
        Категоризация всех необработанных запросов через AI
        """
        try:
            # Получаем все лиды без категории
            leads = self.bitrix.get_leads({
                "UF_CATEGORY": None  # Предполагаем, что есть поле категории
            })
            
            logger.info(f"Found {len(leads)} uncategorized leads")
            
            categorized = []
            for lead in leads:
                try:
                    # Анализируем запрос через Claude
                    request_text = lead.get("COMMENTS", "") or lead.get("TITLE", "")
                    
                    if not request_text:
                        continue
                    
                    analysis = self.claude.analyze_customer_request(request_text)
                    
                    # Извлекаем категорию из анализа
                    # (в реальности нужно парсить JSON ответ)
                    category = self._extract_category(analysis["analysis"])
                    
                    # Обновляем лид
                    self.bitrix.update_lead(lead["ID"], {
                        "UF_CATEGORY": category
                    })
                    
                    categorized.append({
                        "lead_id": lead["ID"],
                        "category": category
                    })
                    
                except Exception as e:
                    logger.error(f"Error categorizing lead {lead['ID']}: {str(e)}")
            
            logger.info(f"Categorized {len(categorized)} leads")
            
            return {
                "total_leads": len(leads),
                "categorized": len(categorized),
                "details": categorized
            }
            
        except Exception as e:
            logger.error(f"Error in mass categorization: {str(e)}")
            raise
    
    def _extract_category(self, analysis_text: str) -> str:
        """Извлечение категории из текста анализа"""
        # Упрощенная логика, в реальности нужно парсить JSON
        categories = ["new_order", "question", "complaint", "document_request", "other"]
        
        for category in categories:
            if category in analysis_text.lower():
                return category
        
        return "other"
    
    def enrich_leads_with_1c_data(self) -> Dict:
        """
        Обогащение лидов данными из 1С
        Проверяет наличие клиента в 1С и добавляет информацию
        """
        from onec.client import OneCClient
        
        try:
            onec = OneCClient()
            
            # Получаем все лиды
            leads = self.bitrix.get_leads()
            
            logger.info(f"Enriching {len(leads)} leads with 1C data")
            
            enriched = []
            batch_updates = []
            
            for lead in leads:
                try:
                    # Получаем телефон лида
                    phone = lead.get("PHONE", [{}])[0].get("VALUE", "")
                    
                    if not phone:
                        continue
                    
                    # Ищем клиента в 1С
                    clients_1c = onec.get_counterparties({"phone": phone})
                    
                    if clients_1c:
                        client_1c = clients_1c[0]
                        
                        # Подготавливаем обновление
                        batch_updates.append({
                            "method": "crm.lead.update",
                            "params": {
                                "id": lead["ID"],
                                "fields": {
                                    "UF_CLIENT_IN_1C": "Y",
                                    "UF_1C_CLIENT_ID": client_1c.get("id"),
                                    "COMMENTS": f"Клиент найден в 1С: {client_1c.get('name')}"
                                }
                            }
                        })
                        
                        enriched.append({
                            "lead_id": lead["ID"],
                            "client_1c_id": client_1c.get("id")
                        })
                
                except Exception as e:
                    logger.error(f"Error enriching lead {lead['ID']}: {str(e)}")
            
            # Выполняем batch обновление
            if batch_updates:
                for i in range(0, len(batch_updates), 50):
                    chunk = batch_updates[i:i+50]
                    self.bitrix._call("batch", {"cmd": chunk})
            
            logger.info(f"Enriched {len(enriched)} leads")
            
            return {
                "total_leads": len(leads),
                "enriched": len(enriched),
                "details": enriched
            }
            
        except Exception as e:
            logger.error(f"Error in lead enrichment: {str(e)}")
            raise

# Вспомогательные функции
def analyze_all_leads():
    """Быстрый запуск анализа всех лидов"""
    ops = MassOperations()
    return ops.analyze_all_new_leads()

def generate_all_offers(stage_id: str, products: List[str]):
    """Быстрый запуск генерации КП"""
    ops = MassOperations()
    return ops.generate_offers_for_deals(stage_id, products)
