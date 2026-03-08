# AI Integration Platform для 1С и Bitrix24

```
├── bitrix24/              # Интеграция с Bitrix24
│   ├── sdk_client.py      # Официальный b24pysdk клиент (рекомендуется)
│   ├── client.py          # Legacy REST API клиент
│   └── mcp_client.py      # MCP клиент (legacy)
├── onec/                  # Интеграция с 1С
│   └── client.py          # HTTP-сервисы клиент
├── ai_services/           # AI-сервисы
│   ├── openai_service.py  # ChatGPT интеграция
│   └── claude_service.py  # Claude интеграция
├── automation/            # Автоматизация
│   ├── lead_processor.py  # Обработка лидов
│   ├── sync.py            # Синхронизация данных
│   └── mass_operations.py # Массовые операции
├── docs/                  # Документация
│   ├── user_guide.md      # Руководство пользователя
│   ├── prompts_library.md # Библиотека промптов
│   ├── setup_guide.md     # Установка и настройка
│   └── ...                # Другие руководства
├── config/                # Конфигурация
│   └── settings.py        # Настройки системы
└── main.py               # Главный API сервер
```
Начните с [Руководства пользователя](docs/user_guide.md)

Проект настроен для работы с GitHub Copilot через Model Context Protocol (MCP):
1. Откройте `.vscode/mcp.json` и нажмите **Start**
2. В Copilot Chat выберите агента `@b24-dev-mcp`
3. Copilot будет использовать контекст Bitrix24 API при генерации кода

Подробнее: [docs/github_copilot_mcp_setup.md](docs/github_copilot_mcp_setup.md)

### Быстрая проверка системы
```bash
# Базовая проверка компонентов
python quick_test.py

# Полная диагностика
python debug_check.py
```

### Запуск тестов
```bash
# Установка зависимостей для тестирования
pip install pytest pytest-mock pytest-cov

# Запуск всех тестов
pytest tests/ -v

# Запуск с покрытием кода
pytest tests/ --cov=. --cov-report=html
```

Подробнее: [docs/testing_and_debugging.md](docs/testing_and_debugging.md)

## 📚 Документация

### Для пользователей
- [Руководство пользователя](docs/user_guide.md) - Как использовать систему
- [Библиотека промптов](docs/prompts_library.md) - Готовые промпты для работы
- [Быстрый старт](docs/quick_start_guide.md) - Начало работы за 5 минут

### Для разработчиков
- [Установка и настройка](docs/setup_guide.md) - Детальная установка
- [Миграция на b24pysdk](docs/b24pysdk_migration_guide.md) - Руководство по переходу
- [Интеграция с 1С](docs/integration_1c.md) - Настройка HTTP-сервисов
- [Настройка Bitrix24](docs/bitrix24_setup.md) - Webhook и OAuth
- [Продвинутые техники AI](docs/ai_prompts_advanced.md) - Prompt engineering


### Синхронизация с 1С

```python
from automation.sync import sync_deal_to_order

result = sync_deal_to_order(deal_id=456)
print(f"Заказ создан: {result['order_id']}")
```

## 🔌 API Endpoints

```bash
# Получить лиды
GET /api/leads

# Анализ запроса
POST /api/analyze-request
{"text": "Нужна молочная продукция"}

# Генерация КП
POST /api/generate-offer
{"lead_id": 123, "products": ["Молоко", "Кефир"]}

# Webhook для Bitrix24
POST /webhook/bitrix/lead
{"lead_id": 123}
```

## 🛠 Технологии

- **Python 3.9+** - Основной язык
- **FastAPI** - REST API сервер
- **OpenAI API** - ChatGPT интеграция
- **Anthropic API** - Claude интеграция
- **Bitrix24 SDK (b24pysdk)** - Официальный Python SDK
- **1С HTTP-сервисы** - ERP интеграция

## 📋 Требования

- Python 3.9+
- Bitrix24 аккаунт с webhook
- OpenAI API ключ
- Anthropic API ключ (опционально)
- 1С с настроенными HTTP-сервисами





