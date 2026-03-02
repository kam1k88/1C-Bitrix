# AI Integration Platform для 1С и Bitrix24

> Комплексная система автоматизации бизнес-процессов с использованием AI-инструментов (ChatGPT, Claude) и интеграцией с 1С и Bitrix24 для компаний в сфере продовольствия и FMCG.

## 🎉 Обновление v2.0 - Миграция на b24pysdk

Проект полностью переведен на официальный SDK от Bitrix24 - [b24pysdk](https://github.com/bitrix24/b24pysdk)!

**Новые возможности:**
- ✅ Официальная поддержка от Bitrix24
- ✅ Автоматическая пагинация для больших списков
- ✅ Встроенные batch операции (до 50+ запросов)
- ✅ Автоматическое обновление OAuth токенов
- ✅ Retry логика и настраиваемые таймауты
- ✅ Поддержка API v2 и v3
- ✅ Типизация и валидация

📖 **Руководство по миграции**: [docs/b24pysdk_migration_guide.md](docs/b24pysdk_migration_guide.md)

## � Быстрый старт

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Настройка окружения
cp .env.example .env
# Отредактируйте .env и добавьте ваши API ключи

# 3. Запуск примеров SDK
python examples/sdk_usage_example.py

# 4. Запуск API сервера
python main.py

# 5. Запуск Telegram ботов (опционально)
python bots/bot_manager.py
```

Откройте http://localhost:8000 - система готова к работе!

📖 **Подробная инструкция**: [docs/quick_start_guide.md](docs/quick_start_guide.md)
📖 **Примеры использования SDK**: [examples/sdk_usage_example.py](examples/sdk_usage_example.py)
🤖 **Telegram боты**: [docs/bots_guide.md](docs/bots_guide.md)

## ✨ Основные возможности

### 🤖 AI-Автоматизация
- **Анализ лидов**: Автоматическая оценка качества (1-10), вероятность конверсии, рекомендации
- **Генерация КП**: Персонализированные коммерческие предложения за секунды
- **Анализ запросов**: Определение типа, срочности, категории и настроения клиента
- **Категоризация**: Автоматическая классификация входящих запросов
- **Массовая обработка**: Batch анализ всех новых лидов одним запросом

### 🔄 Интеграция с Bitrix24 (b24pysdk)
- **Webhook аутентификация** - простая настройка за 2 минуты
- **OAuth 2.0** - для приложений с автообновлением токенов
- **Batch API** - массовые операции до 50+ запросов
- **Автоматическая пагинация** - получение всех записей без ограничений
- **API v2 и v3** - поддержка обеих версий
- **Retry логика** - автоматические повторы при сбоях

### 💼 Интеграция с 1С
- HTTP-сервисы для обмена данными
- Синхронизация клиентов и контрагентов
- Автоматическое создание заказов
- Обновление цен и остатков
- Проверка наличия клиентов в базе

### 🤖 Telegram Боты

#### Analytics Bot 📊
Для аналитиков и руководителей:
- Отчеты по остаткам товаров
- Отчеты по продажам за период
- Топ клиентов по выручке
- Анализ конверсии лидов
- AI-рекомендации

#### Sales Bot 💼
Для менеджеров по продажам:
- Просмотр и создание лидов
- Генерация коммерческих предложений
- Управление задачами
- Поиск клиентов в базе
- AI-оценка качества лидов

#### Support Bot 🛠️
Для технической поддержки:
- База знаний (FAQ)
- Регистрация проблем
- Статус работы систем
- Инструкции по настройке
- AI-помощник

### 📊 Массовые операции
- Анализ всех новых лидов одной командой
- Генерация КП для сделок на определенной стадии
- Обогащение лидов данными из 1С
- Batch-обработка с автоматическим разбиением

## 📁 Структура проекта

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

## 🧪 Тестирование и отладка

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
- **Bitrix24 SDK (b24pysdk)** - Официальный Python SDK
- **1С HTTP-сервисы** - ERP интеграция

## 📋 Требования

- Python 3.9+
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
