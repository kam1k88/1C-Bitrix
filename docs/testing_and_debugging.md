# Тестирование и отладка

## Быстрая проверка системы

### 1. Базовая проверка компонентов
```bash
python quick_test.py
```

Проверяет:
- Импорты всех модулей
- Загрузку конфигурации
- Создание основных клиентов
- Инициализацию LeadProcessor

### 2. Полная диагностика
```bash
python debug_check.py
```

Выполняет комплексную проверку:
- ✓ Переменные окружения
- ✓ Установленные пакеты
- ✓ Структура проекта
- ✓ Конфигурация
- ✓ SDK Client
- ✓ AI сервисы
- ✓ Lead Processor

## Запуск тестов

### Установка зависимостей для тестирования
```bash
pip install pytest pytest-mock pytest-cov pytest-asyncio
```

### Запуск всех тестов
```bash
pytest tests/ -v
```

### Запуск с покрытием кода
```bash
pytest tests/ --cov=. --cov-report=html
```

Отчет будет доступен в `htmlcov/index.html`

### Запуск конкретного теста
```bash
# Один файл
pytest tests/test_sdk_client.py -v

# Один класс
pytest tests/test_sdk_client.py::TestBitrix24SDKClient -v

# Один метод
pytest tests/test_sdk_client.py::TestBitrix24SDKClient::test_get_leads -v
```

## Отладка компонентов

### Bitrix24 SDK Client

```python
from bitrix24.sdk_client import create_client_from_webhook
from config.settings import settings

# Создание клиента
client = create_client_from_webhook(settings.BITRIX24_WEBHOOK_URL)

# Тест получения лидов
try:
    leads = client.get_leads(filter_params={"STATUS_ID": "NEW"})
    print(f"Получено лидов: {len(leads)}")
    if leads:
        print(f"Первый лид: {leads[0]}")
except Exception as e:
    print(f"Ошибка: {e}")
```

### OpenAI Service

```python
from ai_services.openai_service import OpenAIService

service = OpenAIService()

# Тест простого запроса
try:
    response = service.generate_response("Привет, как дела?")
    print(f"Ответ: {response}")
except Exception as e:
    print(f"Ошибка: {e}")
```

### Lead Processor

```python
from automation.lead_processor import LeadProcessor

processor = LeadProcessor()

# Тест обработки лида (с реальным ID из вашей CRM)
try:
    result = processor.process_new_lead(123)
    print(f"Результат: {result}")
except Exception as e:
    print(f"Ошибка: {e}")
```

## Проверка конфигурации

### Просмотр текущих настроек
```python
from config.settings import settings

print("Bitrix24:")
print(f"  Webhook URL: {settings.BITRIX24_WEBHOOK_URL[:50]}..." if settings.BITRIX24_WEBHOOK_URL else "  Не установлен")
print(f"  Domain: {settings.BITRIX24_DOMAIN}")

print("\nAI Services:")
print(f"  OpenAI: {'✓' if settings.OPENAI_API_KEY else '✗'}")
print(f"  Anthropic: {'✓' if settings.ANTHROPIC_API_KEY else '✗'}")
print(f"  Model: {settings.DEFAULT_AI_MODEL}")

print("\n1C:")
print(f"  Base URL: {settings.ONEC_BASE_URL}")
```

## Логирование

### Включение debug логов
В `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Просмотр логов в коде
```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug сообщение")
logger.info("Info сообщение")
logger.warning("Warning сообщение")
logger.error("Error сообщение")
```

## Частые проблемы

### 1. Ошибка импорта модулей
```
ModuleNotFoundError: No module named 'b24pysdk'
```

Решение:
```bash
pip install -r requirements.txt
```

### 2. Ошибка конфигурации
```
ValueError: Either webhook_url or OAuth credentials must be provided
```

Решение: Проверьте `.env` файл и установите `BITRIX24_WEBHOOK_URL`

### 3. Ошибка API ключа
```
openai.error.AuthenticationError: Incorrect API key provided
```

Решение: Проверьте `OPENAI_API_KEY` в `.env`

### 4. Ошибка подключения к Bitrix24
```
ConnectionError: Failed to connect to Bitrix24
```

Решение:
- Проверьте URL вебхука
- Убедитесь, что вебхук активен в Bitrix24
- Проверьте интернет-соединение

## Мониторинг в production

### Health check endpoint
```bash
curl http://localhost:8000/api/health
```

Ответ:
```json
{
  "status": "healthy",
  "bitrix24": "connected",
  "openai": "available",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Проверка работы API
```bash
# Получить лиды
curl http://localhost:8000/api/leads

# Анализ запроса
curl -X POST http://localhost:8000/api/analyze-request \
  -H "Content-Type: application/json" \
  -d '{"text": "Нужна молочная продукция"}'
```

## Профилирование производительности

### Измерение времени выполнения
```python
import time

start = time.time()
result = processor.process_new_lead(123)
elapsed = time.time() - start

print(f"Время выполнения: {elapsed:.2f} сек")
```

### Memory profiling
```bash
pip install memory-profiler

python -m memory_profiler script.py
```

## CI/CD Integration

### GitHub Actions пример
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v --cov=.
```

## Рекомендации

1. **Запускайте тесты перед коммитом**
   ```bash
   pytest tests/ -v
   ```

2. **Используйте debug_check.py при проблемах**
   ```bash
   python debug_check.py
   ```

3. **Проверяйте покрытие кода**
   ```bash
   pytest tests/ --cov=. --cov-report=term-missing
   ```

4. **Логируйте важные операции**
   ```python
   logger.info(f"Processing lead {lead_id}")
   ```

5. **Используйте try-except для внешних API**
   ```python
   try:
       result = api_call()
   except Exception as e:
       logger.error(f"API error: {e}")
       return {"error": str(e)}
   ```
