# Руководство по миграции на b24pysdk

## Обзор

Проект был полностью переведен на использование официального SDK от Bitrix24 - [b24pysdk](https://github.com/bitrix24/b24pysdk). Это обеспечивает:

- Официальную поддержку от Bitrix24
- Автоматическое обновление токенов
- Эффективную пагинацию и batch операции
- Типизацию и валидацию
- Retry логику и таймауты
- Поддержку API v2 и v3

## Что изменилось

### 1. Новый клиент Bitrix24

**Было:**
```python
from bitrix24.client import Bitrix24Client

bitrix = Bitrix24Client()
leads = bitrix.get_leads({"STATUS_ID": "NEW"})
```

**Стало:**
```python
from bitrix24.sdk_client import Bitrix24SDKClient, create_client_from_webhook
from config.settings import settings

# Через фабрику (рекомендуется)
bitrix = create_client_from_webhook(settings.BITRIX24_WEBHOOK_URL)

# Или напрямую
bitrix = Bitrix24SDKClient(
    domain="example.bitrix24.com",
    auth_token="user_id/webhook_key",
    auth_type="webhook"
)

# Получение лидов с автоматической пагинацией
leads = bitrix.get_leads(filter_params={"STATUS_ID": "NEW"})
```

### 2. Обновленная конфигурация

**Новые переменные окружения:**

```bash
# SDK Settings
BITRIX24_API_VERSION=2  # 2 или 3
BITRIX24_TIMEOUT=10
BITRIX24_MAX_RETRIES=3

# OAuth (опционально)
BITRIX24_DOMAIN=your-domain.bitrix24.ru
BITRIX24_CLIENT_ID=your_client_id
BITRIX24_CLIENT_SECRET=your_client_secret
BITRIX24_ACCESS_TOKEN=your_access_token
BITRIX24_REFRESH_TOKEN=your_refresh_token

# Application
DEBUG=False
LOG_LEVEL=INFO
```

### 3. Batch операции

**Было (самописная реализация):**
```python
batch_commands = []
for item in items:
    batch_commands.append({
        "method": "crm.lead.update",
        "params": {"id": item["id"], "fields": item["fields"]}
    })

# Ручное разбиение на чанки
for i in range(0, len(batch_commands), 50):
    chunk = batch_commands[i:i+50]
    result = bitrix._call("batch", {"cmd": chunk})
```

**Стало (встроенный batch API):**
```python
# SDK автоматически разбивает на чанки и обрабатывает
updates = [
    {"id": 1, "fields": {"TITLE": "New title 1"}},
    {"id": 2, "fields": {"TITLE": "New title 2"}},
    # ... можно передать любое количество
]

results = bitrix.batch_update_leads(updates)
```

### 4. Пагинация

**Было:**
```python
# Получали только первые 50 записей
leads = bitrix.get_leads()  # max 50
```

**Стало:**
```python
# Автоматическая пагинация - получаем ВСЕ записи
leads = bitrix.get_leads()  # все записи

# Или с ограничением
leads = bitrix.get_leads(limit=100)  # первые 100

# Эффективная пагинация для больших объемов
leads = bitrix.get_leads()  # возвращает генератор
for lead in leads:
    process(lead)  # запросы делаются лениво
```

### 5. Обработка ошибок

**Было:**
```python
try:
    lead = bitrix.get_lead(lead_id)
except Exception as e:
    print(f"Error: {e}")
```

**Стало:**
```python
from b24pysdk.error import BitrixAPIError, BitrixRequestTimeout, BitrixAPIExpiredToken

try:
    lead = bitrix.get_lead(lead_id)
except BitrixAPIError as e:
    print(f"API Error: {e.error} - {e.error_description}")
except BitrixRequestTimeout:
    print("Request timeout")
except BitrixAPIExpiredToken:
    print("Token expired (auto-refresh for OAuth)")
```

### 6. Комментарии

**Было:**
```python
bitrix.add_comment(lead_id, "Комментарий")
```

**Стало:**
```python
bitrix.add_comment(
    entity_type="lead",
    entity_id=lead_id,
    comment="Комментарий"
)
```

## Миграция кода

### LeadProcessor

**Было:**
```python
class LeadProcessor:
    def __init__(self):
        self.bitrix = Bitrix24Client()
```

**Стало:**
```python
class LeadProcessor:
    def __init__(self, bitrix_client: Optional[Bitrix24SDKClient] = None):
        if bitrix_client:
            self.bitrix = bitrix_client
        elif settings.BITRIX24_WEBHOOK_URL:
            self.bitrix = create_client_from_webhook(
                settings.BITRIX24_WEBHOOK_URL,
                prefer_api_version=settings.BITRIX24_API_VERSION
            )
```

### MassOperations

**Было:**
```python
class MassOperations:
    def __init__(self):
        self.bitrix = Bitrix24Client()
    
    def analyze_all_new_leads(self):
        leads = self.bitrix.get_leads({"STATUS_ID": "NEW"})
        # Ручная batch обработка...
```

**Стало:**
```python
class MassOperations:
    def __init__(self, bitrix_client: Optional[Bitrix24SDKClient] = None):
        if bitrix_client:
            self.bitrix = bitrix_client
        elif settings.BITRIX24_WEBHOOK_URL:
            self.bitrix = create_client_from_webhook(
                settings.BITRIX24_WEBHOOK_URL
            )
    
    def analyze_all_new_leads(self):
        # Автоматическая пагинация
        leads = self.bitrix.get_leads(filter_params={"STATUS_ID": "NEW"})
        
        # Batch через SDK
        requests = [...]
        batch_result = self.bitrix.client.call_batches(requests)
```

## Новые возможности

### 1. API v3 Support

```python
# Используйте API v3 для новых методов
client = Bitrix24SDKClient(
    domain="example.bitrix24.com",
    auth_token="token",
    auth_type="webhook",
    prefer_api_version=3  # API v3
)
```

### 2. Автоматическое обновление токенов

```python
# Для OAuth токены обновляются автоматически
client = Bitrix24SDKClient(
    domain="example.bitrix24.com",
    auth_token=access_token,
    auth_type="oauth",
    client_id=client_id,
    client_secret=client_secret,
    refresh_token=refresh_token
)

# SDK автоматически обновит токен при истечении
```

### 3. Настройка таймаутов и retry

```python
from b24pysdk import Config

cfg = Config()
cfg.configure(
    default_timeout=(3.05, 10),  # (connect, read)
    default_max_retries=3,
    default_initial_retry_delay=1,
    default_retry_delay_increment=1
)
```

### 4. Логирование

```python
from b24pysdk.log import StreamLogger

cfg = Config()
cfg.configure(logger=StreamLogger())
```

### 5. Константы

```python
from b24pysdk.constants.crm import EntityTypeID

fields = client.get_fields(EntityTypeID.DEAL)
```

## Тестирование

### Запуск примеров

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка .env
cp .env.example .env
# Отредактируйте .env

# Запуск примеров
python examples/sdk_usage_example.py
```

### Проверка работоспособности

```bash
# Запуск API сервера
python main.py

# Проверка health check
curl http://localhost:8000/api/health

# Получение лидов
curl http://localhost:8000/api/leads?limit=10
```

## Обратная совместимость

Старые клиенты (`bitrix24/client.py`, `bitrix24/mcp_client.py`) оставлены для обратной совместимости, но рекомендуется мигрировать на новый SDK.

## Troubleshooting

### Ошибка: "Bitrix24 credentials not configured"

Проверьте, что в `.env` установлен `BITRIX24_WEBHOOK_URL` или OAuth параметры.

### Ошибка: "Package b24pysdk is not installed"

```bash
pip install b24pysdk>=0.2.0
```

### Медленная работа с большими списками

Используйте `limit` параметр или генераторы:

```python
# Вместо
all_leads = bitrix.get_leads()  # загружает все в память

# Используйте
for lead in bitrix.get_leads():  # ленивая загрузка
    process(lead)
```

## Дополнительные ресурсы

- [Официальная документация b24pysdk](https://github.com/bitrix24/b24pysdk)
- [Bitrix24 REST API](https://apidocs.bitrix24.com/)
- [Примеры использования](../examples/sdk_usage_example.py)

## Поддержка

При возникновении проблем:
1. Проверьте логи приложения
2. Убедитесь, что используете последнюю версию SDK
3. Проверьте настройки в `.env`
4. Обратитесь к документации b24pysdk
