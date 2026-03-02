# План рефакторинга на b24pysdk

## Что меняем

### 1. Bitrix24 Integration

**Было (старый подход)**:
```python
# bitrix24/client.py
class Bitrix24Client:
    def __init__(self):
        self.webhook_url = settings.BITRIX24_WEBHOOK_URL
    
    def _call(self, method: str, params: Dict = None) -> Dict:
        url = f"{self.webhook_url}{method}"
        response = requests.post(url, json=params or {})
        return response.json()
```

**Стало (b24pysdk)**:
```python
# bitrix24/client.py
from b24pysdk import Client, BitrixWebhook

class Bitrix24Client:
    def __init__(self):
        webhook = BitrixWebhook(
            domain=settings.BITRIX24_DOMAIN,
            auth_token=settings.BITRIX24_WEBHOOK_TOKEN
        )
        self.client = Client(webhook, prefer_version=3)
```

### 2. Преимущества b24pysdk

✅ **Типизация** - Type hints для всех методов
✅ **Валидация** - Автоматическая проверка типов
✅ **Пагинация** - `.as_list()` и `.as_list_fast()` для больших данных
✅ **Batch запросы** - `.call_batch()` и `.call_batches()`
✅ **Retry логика** - Автоматические повторы при ошибках
✅ **OAuth** - Автоматическое обновление токенов
✅ **События** - Подписка на события (token refresh, domain change)
✅ **Логирование** - Встроенная система логов

### 3. Новая структура проекта

```
├── bitrix24/
│   ├── __init__.py
│   ├── client.py              # Обертка над b24pysdk
│   ├── chatbots.py            # Чат-боты для Open Lines
│   ├── automation.py          # Роботы и триггеры
│   └── webhooks.py            # Обработчики webhook событий
│
├── marketplaces/
│   ├── __init__.py
│   ├── ozon_connector.py      # Ozon API
│   ├── wildberries_connector.py  # Wildberries API
│   ├── yandex_market_connector.py  # Яндекс.Маркет API
│   └── sync_manager.py        # Синхронизация с Bitrix24
│
├── assistants/
│   ├── __init__.py
│   ├── analytics_assistant.py  # BI и аналитика
│   ├── sales_assistant.py      # Помощник менеджера
│   ├── warehouse_assistant.py  # Управление складом
│   └── base_assistant.py       # Базовый класс
│
├── ai_services/
│   ├── __init__.py
│   ├── openai_service.py      # GPT-4 (без изменений)
│   ├── claude_service.py      # Claude (без изменений)
│   └── prompt_templates.py    # Шаблоны промптов
│
├── automation/
│   ├── __init__.py
│   ├── lead_processor.py      # Обработка лидов
│   ├── order_processor.py     # Обработка заказов
│   └── sync_engine.py         # Синхронизация данных
│
└── config/
    ├── __init__.py
    └── settings.py            # Настройки (обновлено)
```

## Этапы рефакторинга

### Этап 1: Обновление зависимостей
```bash
pip install b24pysdk
```

### Этап 2: Обновление settings.py
```python
# Было
BITRIX24_WEBHOOK_URL = "https://domain.bitrix24.ru/rest/1/xxxxx/"

# Стало
BITRIX24_DOMAIN = "domain.bitrix24.ru"
BITRIX24_WEBHOOK_TOKEN = "1/xxxxx"  # user_id/webhook_key
```

### Этап 3: Рефакторинг Bitrix24Client
- Использовать b24pysdk.Client
- Добавить типизацию
- Использовать встроенные методы

### Этап 4: Удаление устаревшего кода
- ❌ Удалить `bots/` (Telegram боты)
- ❌ Удалить `onec/client.py` (используем 1С коннектор Bitrix24)
- ❌ Удалить `bitrix24/js_integration.py` (не нужен)
- ❌ Удалить `bitrix24/mcp_client.py` (не нужен)

### Этап 5: Создание новых компонентов
- ✅ Чат-боты для Bitrix24 Open Lines
- ✅ Коннекторы маркетплейсов
- ✅ AI-ассистенты
- ✅ Автоматизация через Bitrix24

## Примеры использования b24pysdk

### Получение лидов
```python
# Старый способ
leads = bitrix.get_leads({"STATUS_ID": "NEW"})

# Новый способ (b24pysdk)
request = client.crm.lead.list(filter={"STATUS_ID": "NEW"})
leads = request.as_list().result  # Автоматическая пагинация
```

### Создание сделки
```python
# Старый способ
deal_id = bitrix._call("crm.deal.add", {"fields": {...}})

# Новый способ (b24pysdk)
request = client.crm.deal.add(fields={
    "TITLE": "Новая сделка",
    "STAGE_ID": "NEW",
    "OPPORTUNITY": 10000
})
deal_id = request.result
```

### Batch запросы
```python
# Старый способ - вручную
batch_commands = []
for lead_id in lead_ids:
    batch_commands.append({
        "method": "crm.lead.get",
        "params": {"id": lead_id}
    })
result = bitrix._call("batch", {"cmd": batch_commands})

# Новый способ (b24pysdk)
requests = {
    f"lead_{lead_id}": client.crm.lead.get(bitrix_id=lead_id)
    for lead_id in lead_ids
}
batch_result = client.call_batch(requests)
```

### Обработка больших списков
```python
# Старый способ - ручная пагинация
all_deals = []
start = 0
while True:
    deals = bitrix.get_deals({"start": start})
    if not deals:
        break
    all_deals.extend(deals)
    start += 50

# Новый способ (b24pysdk)
request = client.crm.deal.list()
all_deals = request.as_list_fast().result  # Generator для экономии памяти

for deal in all_deals:  # Ленивая загрузка
    process_deal(deal)
```

## Новые возможности

### 1. Автоматическое обновление OAuth токенов
```python
from b24pysdk import BitrixToken, BitrixApp

bitrix_app = BitrixApp(
    client_id="app_code",
    client_secret="app_key"
)

bitrix_token = BitrixToken(
    domain="example.bitrix24.ru",
    auth_token="access_token",
    refresh_token="refresh_token",
    bitrix_app=bitrix_app
)

client = Client(bitrix_token)
# SDK автоматически обновит токен при истечении
```

### 2. Подписка на события
```python
from b24pysdk.events import OAuthTokenRenewedEvent

def on_token_renewed(event: OAuthTokenRenewedEvent):
    # Сохранить новый токен в БД
    save_token(event.new_token)

bitrix_token.subscribe(OAuthTokenRenewedEvent, on_token_renewed)
```

### 3. Использование констант
```python
from b24pysdk.constants.crm import EntityTypeID

fields = client.crm.item.fields(
    entity_type_id=EntityTypeID.DEAL
).result
```

### 4. Валидация данных
```python
from b24pysdk.credentials.oauth_placement_data import OAuthPlacementData

try:
    placement_data = OAuthPlacementData.from_dict(data)
    print(f"App ID: {placement_data.app_id}")
except OAuthPlacementData.ValidationError as e:
    print(f"Invalid data: {e}")
```

## Миграция кода

### automation/lead_processor.py
```python
# Было
class LeadProcessor:
    def __init__(self):
        self.bitrix = Bitrix24Client()
    
    def process_new_lead(self, lead_id: int):
        lead = self.bitrix.get_lead(lead_id)
        # ...

# Стало
from b24pysdk import Client, BitrixWebhook

class LeadProcessor:
    def __init__(self):
        webhook = BitrixWebhook(
            domain=settings.BITRIX24_DOMAIN,
            auth_token=settings.BITRIX24_WEBHOOK_TOKEN
        )
        self.client = Client(webhook, prefer_version=3)
    
    def process_new_lead(self, lead_id: int):
        request = self.client.crm.lead.get(bitrix_id=lead_id)
        lead = request.result
        # ...
```

### automation/mass_operations.py
```python
# Было
def analyze_all_leads():
    leads = bitrix.get_leads({"STATUS_ID": "NEW"})
    for lead in leads:
        # ...

# Стало
def analyze_all_leads():
    request = client.crm.lead.list(filter={"STATUS_ID": "NEW"})
    leads = request.as_list_fast().result  # Generator
    
    for lead in leads:  # Ленивая загрузка
        # ...
```

## Преимущества после рефакторинга

✅ **Меньше кода** - SDK берет на себя рутину
✅ **Типобезопасность** - Type hints везде
✅ **Производительность** - Оптимизированная пагинация
✅ **Надежность** - Встроенные retry и error handling
✅ **Поддержка** - Официальный SDK от Bitrix24
✅ **Документация** - Полная документация API
✅ **Обновления** - Автоматическая поддержка новых версий API

## Следующие шаги

1. ✅ Установить b24pysdk
2. ✅ Обновить settings.py
3. ✅ Рефакторить bitrix24/client.py
4. ✅ Обновить automation/
5. ✅ Удалить устаревший код
6. ✅ Создать новые компоненты
7. ✅ Обновить документацию
8. ✅ Тестирование

Начинаем рефакторинг?
