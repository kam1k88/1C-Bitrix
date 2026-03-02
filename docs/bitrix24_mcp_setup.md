# Настройка Bitrix24 MCP с JWT токеном

## Ваша конфигурация

Ваш Bitrix24 MCP уже настроен со следующими параметрами:

- **MCP URL**: `https://mcp-dev.bitrix24.tech/mcp`
- **Domain**: `b24-z373vc.bitrix24.ru`
- **User ID**: 1
- **Token expires**: 2026-03-10

## Быстрый старт

### 1. Проверка токена

```python
from bitrix24.mcp_client import Bitrix24MCPClient

client = Bitrix24MCPClient()
token_info = client.check_token_expiry()

print(f"Token expires: {token_info['expires_at']}")
print(f"Days until expiry: {token_info['days_until_expiry']}")
```

### 2. Получение данных

```python
# Получить все новые лиды
leads = client.get_leads({"STATUS_ID": "NEW"})
print(f"Found {len(leads)} new leads")

# Получить сделки
deals = client.get_deals({"STAGE_ID": "C1:NEW"})

# Получить текущего пользователя
user = client.get_current_user()
print(f"User: {user['NAME']} {user['LAST_NAME']}")
```

### 3. Создание данных

```python
# Создать лид
lead_id = client.create_lead({
    "TITLE": "Новый лид через MCP",
    "NAME": "Иван",
    "LAST_NAME": "Петров",
    "PHONE": [{"VALUE": "+79001234567", "VALUE_TYPE": "WORK"}],
    "EMAIL": [{"VALUE": "ivan@example.com", "VALUE_TYPE": "WORK"}]
})

# Добавить комментарий
client.add_comment("lead", lead_id, "Лид создан через MCP API")

# Создать задачу
task_id = client.create_task({
    "TITLE": "Связаться с клиентом",
    "RESPONSIBLE_ID": 1,
    "DESCRIPTION": "Позвонить и уточнить детали"
})
```

## Использование через AI

После настройки MCP в `.kiro/settings/mcp.json`, вы можете работать через естественный язык:

### Пример 1: Анализ лидов

```
Проанализируй все новые лиды в моем Bitrix24.
Для каждого лида:
1. Оцени полноту информации (есть ли телефон, email)
2. Оцени качество описания (1-10)
3. Добавь комментарий с рекомендациями
```

### Пример 2: Создание задач

```
Найди все сделки на стадии "Переговоры" и создай для каждой
задачу "Отправить КП" с дедлайном через 2 дня
```

### Пример 3: Обогащение данных

```
Найди все контакты без email. Для каждого контакта:
1. Если есть компания, найди сайт компании
2. Попробуй найти email на сайте
3. Если нашел, обнови контакт
```

## Интеграция с существующим кодом

```python
from bitrix24.mcp_client import Bitrix24MCPClient
from ai_services.openai_service import OpenAIService

# MCP клиент для прямого доступа
mcp_client = Bitrix24MCPClient()

# AI сервис для анализа
ai = OpenAIService()

# Получаем лиды через MCP
leads = mcp_client.get_leads({"STATUS_ID": "NEW"})

# Анализируем через AI
for lead in leads:
    analysis = ai.analyze_lead(lead)
    
    # Добавляем комментарий через MCP
    mcp_client.add_comment(
        "lead",
        lead["ID"],
        f"AI Анализ: {analysis['analysis']}"
    )
```

## Автоматизация

### Создание автоматического сценария

```python
from bitrix24.mcp_client import Bitrix24MCPClient
from ai_services.openai_service import OpenAIService

def daily_lead_processing():
    """Ежедневная обработка лидов"""
    client = Bitrix24MCPClient()
    ai = OpenAIService()
    
    # Получаем новые лиды
    leads = client.get_leads({"STATUS_ID": "NEW"})
    
    for lead in leads:
        # AI анализ
        analysis = ai.analyze_lead(lead)
        score = analysis.get("score", 0)
        
        # Добавляем комментарий
        client.add_comment(
            "lead",
            lead["ID"],
            f"🤖 AI Оценка: {score}/10\n{analysis['analysis']}"
        )
        
        # Если высокая оценка - создаем задачу
        if score >= 8:
            client.create_task({
                "TITLE": f"Приоритетный лид: {lead['TITLE']}",
                "RESPONSIBLE_ID": lead.get("ASSIGNED_BY_ID", 1),
                "DESCRIPTION": f"Лид с высокой оценкой AI: {score}/10",
                "DEADLINE": "tomorrow"
            })

# Запуск
if __name__ == "__main__":
    daily_lead_processing()
```

## Мониторинг токена

Токен действителен до **2026-03-10**. Создайте скрипт для проверки:

```python
from bitrix24.mcp_client import Bitrix24MCPClient
from datetime import datetime

def check_token_status():
    client = Bitrix24MCPClient()
    info = client.check_token_expiry()
    
    if info.get("is_expired"):
        print("⚠️ ВНИМАНИЕ: Токен истек!")
        print("Получите новый токен в Bitrix24")
    elif info["days_until_expiry"] < 30:
        print(f"⚠️ Токен истекает через {info['days_until_expiry']} дней")
    else:
        print(f"✅ Токен действителен еще {info['days_until_expiry']} дней")
    
    return info

# Запуск проверки
check_token_status()
```

## Обновление токена

Когда токен истечет (после 2026-03-10):

1. Откройте Bitrix24
2. Перейдите в настройки MCP
3. Сгенерируйте новый токен
4. Обновите `.env.mcp`:

```bash
BITRIX24_MCP_TOKEN=новый_токен_здесь
```

5. Перезапустите приложение

## Troubleshooting

### Ошибка 401 Unauthorized

Проверьте:
- Правильность токена в `.env.mcp`
- Срок действия токена (не истек ли)

### Ошибка 403 Forbidden

Проверьте права доступа токена в Bitrix24.

### Ошибка подключения

Проверьте доступность `https://mcp-dev.bitrix24.tech/mcp`

## Лучшие практики

1. **Регулярно проверяйте срок токена**
2. **Используйте autoApprove только для безопасных операций**
3. **Логируйте все операции для аудита**
4. **Создавайте резервные копии важных данных**

## Следующие шаги

1. Протестируйте подключение: `python bitrix24/mcp_client.py`
2. Изучите примеры в `automation/mcp_scenarios.py`
3. Создайте свои автоматические сценарии
4. Настройте cron для регулярного запуска
