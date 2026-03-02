"""
Сценарий 1: Ежедневный анализ новых лидов
Автоматизация: Каждое утро в 9:00 система анализирует все новые лиды
"""

from bitrix24.mcp_client import Bitrix24MCPClient
from ai_services.openai_service import OpenAIService
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def daily_lead_analysis():
    """
    Ежедневный анализ новых лидов
    
    Что делает:
    1. Получает все лиды, созданные за последние 24 часа
    2. Анализирует каждый лид через AI
    3. Добавляет комментарий с оценкой и рекомендациями
    4. Создает задачи для приоритетных лидов
    """
    
    logger.info("Начало ежедневного анализа лидов")
    
    # Инициализация клиентов
    bitrix = Bitrix24MCPClient()
    ai = OpenAIService()
    
    # Получаем лиды за последние 24 часа
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    leads = bitrix.get_leads({
        ">=DATE_CREATE": yesterday,
        "STATUS_ID": "NEW"
    })
    
    logger.info(f"Найдено {len(leads)} новых лидов")
    
    processed = 0
    high_priority = 0
    
    for lead in leads:
        try:
            # AI анализ
            analysis = ai.analyze_lead(lead)
            score = extract_score(analysis.get("analysis", ""))
            
            # Добавляем комментарий
            comment = f"""🤖 AI-Анализ от {datetime.now().strftime("%d.%m.%Y")}
            
Оценка качества: {score}/10
{analysis.get("analysis", "")}

---
Автоматический анализ системы AI Integration Platform
"""
            
            bitrix.add_comment("lead", lead["ID"], comment)
            
            # Если высокая оценка - создаем задачу
            if score >= 8:
                bitrix.create_task({
                    "TITLE": f"🔥 Приоритетный лид: {lead.get('TITLE', 'Без названия')}",
                    "RESPONSIBLE_ID": lead.get("ASSIGNED_BY_ID", 1),
                    "DESCRIPTION": f"Лид с высокой оценкой AI: {score}/10\n\nСвязаться в течение 2 часов!",
                    "DEADLINE": datetime.now().strftime("%Y-%m-%d")
                })
                high_priority += 1
            
            processed += 1
            
        except Exception as e:
            logger.error(f"Ошибка обработки лида {lead['ID']}: {str(e)}")
    
    logger.info(f"Обработано: {processed} лидов, приоритетных: {high_priority}")
    
    return {
        "total": len(leads),
        "processed": processed,
        "high_priority": high_priority
    }

def extract_score(text: str) -> int:
    """Извлечение оценки из текста анализа"""
    import re
    match = re.search(r'(\d+)/10', text)
    return int(match.group(1)) if match else 5

if __name__ == "__main__":
    result = daily_lead_analysis()
    print(f"✅ Анализ завершен: {result}")
