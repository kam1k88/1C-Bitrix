# AI Integration Platform для 1С и Bitrix24

> Комплексная система автоматизации бизнес-процессов с использованием AI-инструментов (ChatGPT, Claude) и интеграцией с 1С и Bitrix24 для компаний в сфере продовольствия и FMCG.

## 🚀 Быстрый старт

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Настройка окружения
cp .env.example .env
# Отредактируйте .env и добавьте ваши API ключи

# 3. Тест подключения к Bitrix24 MCP
python test_mcp_connection.py

# 4. Запуск
python main.py
```

Откройте http://localhost:8000 - система готова к работе!

📖 **Подробная инструкция**: [docs/quick_start_guide.md](docs/quick_start_guide.md)
📖 **Настройка MCP**: [docs/bitrix24_mcp_setup.md](docs/bitrix24_mcp_setup.md)

## ✨ Основные возможности

### 🤖 AI-Автоматизация
- **Анализ лидов**: Автоматическая оценка качества (1-10), вероятность конверсии, рекомендации
- **Генерация КП**: Персонализированные коммерческие предложения за секунды
- **Анализ запросов**: Определение типа, срочности, категории и настроения клиента
- **Категоризация**: Автоматическая классификация входящих запросов

### 🔄 Интеграция с Bitrix24
- REST API и Webhook интеграция
- Bitrix24 JS SDK для продвинутых операций
- **MCP (Model Context Protocol)** - прямая работа через AI
- Автоматическая обработка новых лидов
- Массовые операции (batch запросы)
- Синхронизация данных

### 💼 Интеграция с 1С
- HTTP-сервисы для обмена данными
- Синхронизация клиентов и контрагентов
- Автоматическое создание заказов
- Обновление цен и остатков
- Проверка наличия клиентов в базе

### 📊 Массовые операции
- Анализ всех новых лидов одной командой
- Генерация КП для сделок на определенной стадии
- Обогащение лидов данными из 1С
- Batch-обработка с автоматическим разбиением

## 📁 Структура проекта

```
├── bitrix24/              # Интеграция с Bitrix24
│   ├── client.py          # REST API клиент
│   └── js_integration.py  # Bitrix24 JS SDK интеграция
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

## 📚 Документация

### Для пользователей
- [Руководство пользователя](docs/user_guide.md) - Как использовать систему
- [Библиотека промптов](docs/prompts_library.md) - Готовые промпты для работы
- [Быстрый старт](docs/quick_start_guide.md) - Начало работы за 5 минут

### Для разработчиков
- [Установка и настройка](docs/setup_guide.md) - Детальная установка
- [Интеграция с 1С](docs/integration_1c.md) - Настройка HTTP-сервисов
- [Настройка Bitrix24](docs/bitrix24_setup.md) - Webhook и автоматизация
- [Bitrix24 JS SDK](docs/bitrix24_js_sdk_integration.md) - Продвинутая интеграция
- [Bitrix24 MCP](docs/bitrix24_mcp_integration.md) - Работа через Model Context Protocol
- [Bitrix24 MCP Setup](docs/bitrix24_mcp_setup.md) - Настройка с вашим JWT токеном
- [Продвинутые техники AI](docs/ai_prompts_advanced.md) - Prompt engineering

## 🎯 Примеры использования

### Анализ лида

```python
from automation.lead_processor import LeadProcessor

processor = LeadProcessor()
result = processor.process_new_lead(lead_id=123)

print(result['analysis'])
# AI-анализ с оценкой качества и рекомендациями
```

### Генерация КП

```python
offer = processor.generate_offer_for_lead(
    lead_id=123,
    products=["Молоко 3.2%", "Кефир 2.5%"]
)
```

### Массовый анализ

```python
from automation.mass_operations import analyze_all_leads

result = analyze_all_leads()
print(f"Проанализировано {result['analyzed']} лидов")
```

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
- **Bitrix24 REST API** - CRM интеграция
- **Bitrix24 JS SDK** - Продвинутая интеграция
- **1С HTTP-сервисы** - ERP интеграция

## 📋 Требования

- Python 3.9+
- Node.js 18+ (для Bitrix24 JS SDK)
- Bitrix24 аккаунт с webhook
- OpenAI API ключ
- Anthropic API ключ (опционально)
- 1С с настроенными HTTP-сервисами

## 🤝 Поддержка

- Email: support@company.ru
- Telegram: @ai_support_bot
- Документация: `docs/`

## 📄 Лицензия

MIT License - используйте свободно в коммерческих проектах

## 🎓 Обучение сотрудников

Система включает полную документацию для обучения сотрудников:
- Пошаговые руководства
- Библиотека готовых промптов
- Примеры использования
- Лучшие практики

Начните с [Руководства пользователя](docs/user_guide.md)
