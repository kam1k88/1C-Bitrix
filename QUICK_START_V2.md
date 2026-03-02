# Быстрый старт v2.0 (b24pysdk)

## 🚀 Установка за 5 минут

### 1. Клонирование и установка зависимостей

```bash
# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка Bitrix24 Webhook

1. Откройте ваш портал Bitrix24
2. Перейдите в **Разработчикам** → **Другое** → **Входящий вебхук**
3. Создайте новый вебхук с правами:
   - CRM (чтение и запись)
   - Пользователи (чтение)
4. Скопируйте URL вебхука (формат: `https://your-domain.bitrix24.ru/rest/1/xxxxx/`)

### 3. Настройка переменных окружения

```bash
# Копируем шаблон
cp .env.example .env

# Редактируем .env
nano .env  # или любой редактор
```

**Минимальная конфигурация:**
```env
# Bitrix24 (обязательно)
BITRIX24_WEBHOOK_URL=https://your-domain.bitrix24.ru/rest/1/xxxxx/

# AI Services (хотя бы один)
OPENAI_API_KEY=sk-your-openai-key
# или
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

### 4. Проверка работоспособности

```bash
# Запуск примеров SDK
python examples/sdk_usage_example.py

# Если все ОК, запускаем API сервер
python main.py
```

Откройте http://localhost:8000 - вы должны увидеть:
```json
{
  "message": "AI Integration Platform API v2.0",
  "status": "running",
  "sdk": "b24pysdk",
  "api_version": 2
}
```

### 5. Проверка здоровья системы

```bash
curl http://localhost:8000/api/health
```

Должны увидеть статус всех сервисов.

## 📝 Первые шаги

### Получение лидов

```bash
# Все новые лиды
curl http://localhost:8000/api/leads?status=NEW&limit=10

# Все лиды
curl http://localhost:8000/api/leads
```

### Анализ лида через AI

```bash
curl -X POST http://localhost:8000/webhook/bitrix/lead \
  -H "Content-Type: application/json" \
  -d '{"lead_id": 123}'
```

### Массовый анализ всех новых лидов

```bash
curl -X POST http://localhost:8000/api/batch/analyze-leads
```

### Генерация коммерческого предложения

```bash
curl -X POST http://localhost:8000/api/generate-offer \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 123,
    "products": ["Мука пшеничная", "Сахар", "Масло подсолнечное"]
  }'
```

## 🔧 Использование в коде

### Базовый пример

```python
from bitrix24.sdk_client import create_client_from_webhook
from config.settings import settings

# Создание клиента
client = create_client_from_webhook(settings.BITRIX24_WEBHOOK_URL)

# Получение лидов
leads = client.get_leads(filter_params={"STATUS_ID": "NEW"})
print(f"Найдено лидов: {len(leads)}")

# Обновление лида
client.update_lead(123, {"COMMENTS": "Обработано через SDK"})

# Добавление комментария
client.add_comment(
    entity_type="lead",
    entity_id=123,
    comment="Тестовый комментарий"
)
```

### Batch операции

```python
# Массовое обновление
updates = [
    {"id": 1, "fields": {"STATUS_ID": "IN_PROCESS"}},
    {"id": 2, "fields": {"STATUS_ID": "IN_PROCESS"}},
    {"id": 3, "fields": {"STATUS_ID": "IN_PROCESS"}},
]
results = client.batch_update_leads(updates)
print(f"Обновлено: {len([r for r in results if r])}")
```

### Автоматическая пагинация

```python
# Получить ВСЕ лиды (автоматическая пагинация)
all_leads = client.get_leads()
print(f"Всего лидов: {len(all_leads)}")

# С фильтром
new_leads = client.get_leads(filter_params={"STATUS_ID": "NEW"})
print(f"Новых лидов: {len(new_leads)}")
```

## 🎯 Типичные сценарии

### Сценарий 1: Ежедневный анализ новых лидов

```python
from automation.mass_operations import analyze_all_leads

# Запуск анализа
result = analyze_all_leads()
print(f"Проанализировано: {result['analyzed']} из {result['total_leads']}")
```

### Сценарий 2: Создание сделок из лидов

```python
from automation.mass_operations import create_deals_from_leads

# ID лидов для конвертации
lead_ids = [123, 124, 125]

# Создание сделок
result = create_deals_from_leads(lead_ids)
print(f"Создано сделок: {result['deals_created']}")
print(f"ID сделок: {result['deal_ids']}")
```

### Сценарий 3: Обработка webhook от Bitrix24

```python
from automation.lead_processor import LeadProcessor

processor = LeadProcessor()

# При получении webhook с новым лидом
def on_new_lead(lead_id: int):
    result = processor.process_new_lead(lead_id)
    print(f"Лид {lead_id} обработан")
    print(f"Оценка: {result['analysis'].get('score')}/10")
```

## 🐛 Решение проблем

### Ошибка: "Bitrix24 credentials not configured"

**Решение:** Проверьте `.env` файл, убедитесь что `BITRIX24_WEBHOOK_URL` установлен.

### Ошибка: "Package b24pysdk is not installed"

**Решение:**
```bash
pip install b24pysdk>=0.2.0
```

### Ошибка: "BitrixAPIError: QUERY_LIMIT_EXCEEDED"

**Решение:** SDK автоматически обрабатывает лимиты. Если ошибка повторяется, увеличьте `BITRIX24_MAX_RETRIES` в `.env`.

### Медленная работа с большими списками

**Решение:** Используйте `limit` параметр:
```python
# Вместо
all_leads = client.get_leads()  # может быть медленно

# Используйте
first_100 = client.get_leads(limit=100)
```

### Ошибка: "Token expired"

**Решение:** 
- Для webhook: создайте новый вебхук в Bitrix24
- Для OAuth: SDK автоматически обновит токен (если настроен refresh_token)

## 📚 Дополнительные ресурсы

- **Полная документация**: [docs/b24pysdk_migration_guide.md](docs/b24pysdk_migration_guide.md)
- **Примеры кода**: [examples/sdk_usage_example.py](examples/sdk_usage_example.py)
- **API документация**: http://localhost:8000/docs (после запуска сервера)
- **Bitrix24 API**: https://apidocs.bitrix24.com/
- **b24pysdk GitHub**: https://github.com/bitrix24/b24pysdk

## 🎓 Следующие шаги

1. ✅ Изучите примеры в `examples/sdk_usage_example.py`
2. ✅ Настройте webhook в Bitrix24 для автоматической обработки
3. ✅ Настройте AI сервисы (OpenAI или Anthropic)
4. ✅ Запустите массовый анализ лидов
5. ✅ Интегрируйте с 1С (опционально)
6. ✅ Настройте Telegram ботов (опционально)

## 💡 Полезные команды

```bash
# Проверка версии SDK
python -c "import b24pysdk; print(b24pysdk.__version__)"

# Запуск с автоперезагрузкой
uvicorn main:app --reload

# Просмотр логов
tail -f app.log  # если настроено логирование в файл

# Тестирование API
curl http://localhost:8000/api/health
```

## 🤝 Поддержка

Если возникли вопросы:
1. Проверьте [docs/b24pysdk_migration_guide.md](docs/b24pysdk_migration_guide.md)
2. Изучите примеры в `examples/`
3. Проверьте логи приложения
4. Обратитесь к документации b24pysdk

---

**Версия**: 2.0.0  
**SDK**: b24pysdk >= 0.2.0  
**Python**: 3.9+
