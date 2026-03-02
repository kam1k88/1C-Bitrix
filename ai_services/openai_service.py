from openai import OpenAI
from typing import List, Dict
from config.settings import settings

class OpenAIService:
    """Сервис для работы с OpenAI API"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Генерация ответа через ChatGPT"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=settings.DEFAULT_AI_MODEL,
            messages=messages,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE
        )
        return response.choices[0].message.content
    
    def analyze_lead(self, lead_data: Dict) -> Dict:
        """Анализ лида с помощью AI"""
        system_prompt = """Ты - AI-ассистент для анализа лидов в CRM. 
        Проанализируй информацию о лиде и предоставь:
        1. Оценку качества лида (1-10)
        2. Рекомендации по работе с лидом
        3. Предполагаемую вероятность конверсии
        4. Следующие шаги для менеджера"""
        
        prompt = f"""Информация о лиде:
        Имя: {lead_data.get('NAME', 'Не указано')}
        Компания: {lead_data.get('COMPANY_TITLE', 'Не указано')}
        Телефон: {lead_data.get('PHONE', 'Не указано')}
        Email: {lead_data.get('EMAIL', 'Не указано')}
        Комментарий: {lead_data.get('COMMENTS', 'Нет комментариев')}
        
        Проанализируй этого лида."""
        
        analysis = self.generate_response(prompt, system_prompt)
        return {"analysis": analysis, "lead_id": lead_data.get('ID')}
    
    def generate_commercial_offer(self, client_info: Dict, products: List[str]) -> str:
        """Генерация коммерческого предложения"""
        system_prompt = """Ты - эксперт по составлению коммерческих предложений 
        в сфере продовольствия и FMCG. Создай профессиональное КП."""
        
        prompt = f"""Создай коммерческое предложение для:
        Клиент: {client_info.get('name')}
        Компания: {client_info.get('company')}
        Продукты: {', '.join(products)}
        
        КП должно быть убедительным и профессиональным."""
        
        return self.generate_response(prompt, system_prompt)
