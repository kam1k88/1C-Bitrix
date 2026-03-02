# Быстрый старт: AI Integration Platform

## За 5 минут до первого результата

### Шаг 1: Клонирование и установка (2 минуты)

```bash
# Установка Python зависимостей
pip install -r requirements.txt

# Создание .env файла
cp .env.example .env
```

### Шаг 2: Настройка API ключей (2 минуты)

Откройте `.env` и заполните:

```env
# Минимальная конфигурация для старта
BITRIX24_WEBHOOK_URL=https://your-domain.bitrix24.ru/rest/1/xxxxx/
OPENAI_API_KEY=sk-your-key-here
```

**Где взять ключи:**
- Bitrix24: Меню → Разработчикам → Входящий вебхук
- OpenAI: https://platform.openai.com/api-keys

### Шаг 3: Первый запуск (1 минута)

```bash
python main.py
```

Откройте http://localhost:8000 - вы должны увидеть:
```json
{"message": "AI Integration Platform API", "status": "running"}
```

## Первые задачи

### Задача 1: Анализ лида через AI

```python
from automation.lead_processor import LeadProcessor

processor = LeadProcessor()

# Анализируем лид с ID = 123
result = processor.process_new_lead(123)

print(result['analysis'])
# Вывод: AI-анализ с оценкой качества и рекомендациями
```

### Задача 2: Генерация коммерческого предложения

```python
offer = processor.generate_offer_for_lead(
    lead_id=123,
    products=["Молоко 3.2%", "Кефир 2.5%", "Творог 9%"]
)

print(offer)
# Вывод: Готовое коммерческое предложение
```

### Задача 3: Анализ запроса клиента

```python
from ai_services.claude_service import ClaudeService

claude = ClaudeService()

analysis = claude.analyze_customer_request(
    "Нужно срочно 100 литров молока к завтрашнему утру!"
)

print(analysis)
# Вывод: Структурированный анализ с определением срочности и категории
```

## Автоматизация через Webhook

### Настройка автоматической обработки лидов

1. В Bitrix24: CRM → Лиды → Автоматизация
2. Создайте правило:
   - Триггер: "При создании лида"
   - Действие: "Вызвать webhook"
   - URL: `http://your-server:8000/webhook/bitrix/lead`
   - Тело: `{"lead_id": "{=Document:ID}"}`

Теперь каждый новый лид автоматически анализируется AI!

## Массовые операции

### Анализ всех новых лидов

```python
from automation.mass_operations import analyze_all_leads

result = analyze_all_leads()
print(f"Проанализировано {result['analyzed']} лидов")
```

### Генерация КП для всех сделок на стадии

```python
from automation.mass_operations import generate_all_offers

result = generate_all_offers(
    stage_id="C1:NEW",
    products=["Молоко", "Кефир", "Творог"]
)
print(f"Сгенерировано {result['generated']} КП")
```

## Интеграция с 1С

### Проверка клиента в 1С

```python
from onec.client import OneCClient

onec = OneCClient()

# Поиск клиента по телефону
clients = onec.get_counterparties({"phone": "+79001234567"})

if clients:
    print(f"Клиент найден: {clients[0]['name']}")
else:
    print("Клиент не найден в 1С")
```

### Создание заказа в 1С из сделки Bitrix24

```python
from automation.sync import sync_deal_to_order

result = sync_deal_to_order(deal_id=456)
print(f"Создан заказ в 1С: {result['order_id']}")
```

## Использование промптов

### Пример: Анализ качества лида

```python
from ai_services.openai_service import OpenAIService

ai = OpenAIService()

prompt = """
Проанализируй лид:
- Компания: ООО "Продукты+"
- Контакт: Иван Петров
- Запрос: Нужна молочная продукция для сети магазинов
- Источник: Холодный звонок

Оцени качество лида (1-10) и дай рекомендации.
"""

analysis = ai.generate_response(prompt)
print(analysis)
```

### Пример: Создание шаблона ответа

```python
from ai_services.claude_service import ClaudeService

claude = ClaudeService()

template = claude.create_response_template(
    "Клиент жалуется на задержку доставки"
)

print(template)
# Вывод: Профессиональный шаблон ответа
```

## API Endpoints

### Получить список лидов

```bash
curl http://localhost:8000/api/leads
```

### Анализ запроса клиента

```bash
curl -X POST http://localhost:8000/api/analyze-request \
  -H "Content-Type: application/json" \
  -d '{"text": "Хочу заказать молочную продукцию"}'
```

### Генерация КП

```bash
curl -X POST http://localhost:8000/api/generate-offer \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 123,
    "products": ["Молоко", "Кефир"]
  }'
```

## Мониторинг

### Проверка работы системы

```python
from bitrix24.client import Bitrix24Client
from ai_services.openai_service import OpenAIService

# Проверка Bitrix24
bitrix = Bitrix24Client()
leads = bitrix.get_leads()
print(f"✓ Bitrix24: {len(leads)} лидов доступно")

# Проверка OpenAI
ai = OpenAIService()
response = ai.generate_response("Тест")
print(f"✓ OpenAI: Работает")

print("\n✓ Все системы работают!")
```

## Следующие шаги

1. **Изучите библиотеку промптов**: `docs/prompts_library.md`
2. **Настройте интеграцию с 1С**: `docs/integration_1c.md`
3. **Продвинутые техники AI**: `docs/ai_prompts_advanced.md`
4. **Настройка Bitrix24 JS SDK**: `docs/bitrix24_js_sdk_integration.md`

## Частые вопросы

**Q: Как изменить модель AI?**
```python
# В config/settings.py
DEFAULT_AI_MODEL = "gpt-4"  # или "gpt-3.5-turbo"
```

**Q: Как добавить свои промпты?**
Создайте файл в `prompts/` и используйте:
```python
with open("prompts/my_prompt.txt") as f:
    prompt = f.read()
    
result = ai.generate_response(prompt)
```

**Q: Как обрабатывать ошибки?**
```python
try:
    result = processor.process_new_lead(123)
except Exception as e:
    print(f"Ошибка: {str(e)}")
    # Логирование, уведомление и т.д.
```

## Получение помощи

- Документация: `docs/`
- Примеры: `examples/`
- Issues: GitHub Issues
- Telegram: @ai_integration_support
