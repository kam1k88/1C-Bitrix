from anthropic import Anthropic
from typing import Dict
from config.settings import settings

class ClaudeService:
    """Сервис для работы с Claude API"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Генерация ответа через Claude"""
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=settings.MAX_TOKENS,
            system=system_prompt or "Ты - полезный AI-ассистент.",
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def analyze_customer_request(self, request_text: str) -> Dict:
        """Анализ запроса клиента"""
        system_prompt = """Ты - AI-аналитик клиентских запросов. 
        Определи: тип запроса, срочность, категорию товара, настроение клиента."""
        
        prompt = f"""Проанализируй запрос клиента:
        
        "{request_text}"
        
        Предоставь структурированный анализ в формате JSON."""
        
        analysis = self.generate_response(prompt, system_prompt)
        return {"analysis": analysis, "original_request": request_text}
    
    def create_response_template(self, situation: str) -> str:
        """Создание шаблона ответа для типовой ситуации"""
        system_prompt = """Ты - эксперт по клиентскому сервису. 
        Создай профессиональный шаблон ответа."""
        
        prompt = f"Создай шаблон ответа для ситуации: {situation}"
        return self.generate_response(prompt, system_prompt)
