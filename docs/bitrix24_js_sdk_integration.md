# Интеграция с Bitrix24 JS SDK

## Обзор

Bitrix24 JS SDK предоставляет мощные возможности для работы с REST API, включая:
- Автоматическую обработку пагинации
- Batch-запросы с автоматическим разбиением на чанки
- Потоковую обработку больших объемов данных
- Управление ограничениями и повторными попытками

## Установка

### Шаг 1: Установка Node.js

Убедитесь, что у вас установлен Node.js (версия 18+):

```bash
node --version
```

### Шаг 2: Настройка Node.js скриптов

```bash
cd bitrix24/js_scripts
npm install
```

Это установит `@bitrix24/b24jssdk` и все зависимости.

## Использование в Python

### Базовый пример

```python
from bitrix24.js_integration import Bitrix24JSIntegration

# Инициализация
b24_js = Bitrix24JSIntegration(webhook_url="https://your-domain.bitrix24.ru/rest/1/xxxxx/")

# Получение всех лидов (автоматическая пагинация)
leads = b24_js.get_all_leads(filter_params={"STATUS_ID": "NEW"})
print(f"Получено {len(leads)} лидов")

# Batch запрос
commands = [
    {"method": "crm.lead.get", "params": {"id": 1}},
    {"method": "crm.lead.get", "params": {"id": 2}},
    {"method": "crm.lead.get", "params": {"id": 3}},
]
results = b24_js.batch_request(commands)
```

## Продвинутые возможности

### 1. CallListV3 - Получение всех данных

Автоматически обрабатывает пагинацию и возвращает все записи:

```javascript
// Node.js
const leads = await b24.callListV3('crm.lead.list', {
    filter: { STATUS_ID: 'NEW' },
    select: ['ID', 'TITLE', 'NAME', 'PHONE']
});
```

```python
# Python обертка
leads = b24_js.get_all_leads({"STATUS_ID": "NEW"})
```

### 2. FetchListV3 - Потоковая обработка

Для работы с очень большими объемами данных без загрузки всего в память:

```javascript
// Node.js
for await (const deal of b24.fetchListV3('crm.deal.list', {
    filter: { STAGE_ID: 'WON' }
})) {
    console.log(deal);
    // Обработка каждой сделки по мере получения
}
```

### 3. BatchByChunkV3 - Batch с автоматическим разбиением

Выполнение любого количества команд (автоматически разбивается на чанки по 50):

```javascript
// Node.js
const commands = [];
for (let i = 1; i <= 200; i++) {
    commands.push({
        method: 'crm.lead.get',
        params: { id: i }
    });
}

// Автоматически разобьется на 4 batch запроса
const results = await b24.callBatchByChunkV3(commands);
```

## Создание Node.js микросервиса

Для более сложной интеграции создайте отдельный Node.js сервис:

### server.js

```javascript
import express from 'express';
import { initializeB24 } from '@bitrix24/b24jssdk';

const app = express();
app.use(express.json());

let b24;

// Инициализация
app.post('/init', async (req, res) => {
    try {
        b24 = await initializeB24({
            webhookUrl: req.body.webhook_url
        });
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Получение всех лидов
app.post('/leads/all', async (req, res) => {
    try {
        const leads = await b24.callListV3('crm.lead.list', {
            filter: req.body.filter || {},
            select: req.body.select || ['*']
        });
        res.json({ leads });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Batch запрос
app.post('/batch', async (req, res) => {
    try {
        const results = await b24.callBatchByChunkV3(req.body.commands);
        res.json({ results });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Массовое обновление
app.post('/leads/bulk-update', async (req, res) => {
    try {
        const { updates } = req.body; // [{ id: 1, fields: {...} }, ...]
        
        const commands = updates.map(update => ({
            method: 'crm.lead.update',
            params: {
                id: update.id,
                fields: update.fields
            }
        }));
        
        const results = await b24.callBatchByChunkV3(commands);
        res.json({ results });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Проверка здоровья API
app.get('/health', async (req, res) => {
    try {
        const health = await b24.healthCheck();
        res.json({ status: 'ok', health });
    } catch (error) {
        res.status(500).json({ status: 'error', error: error.message });
    }
});

// Ping - измерение скорости ответа
app.get('/ping', async (req, res) => {
    try {
        const responseTime = await b24.ping();
        res.json({ responseTime });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Bitrix24 JS SDK service running on port ${PORT}`);
});
```

### package.json

```json
{
  "name": "bitrix24-js-service",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@bitrix24/b24jssdk": "latest",
    "express": "^4.18.2"
  },
  "scripts": {
    "start": "node server.js"
  }
}
```

### Использование из Python

```python
import requests

class Bitrix24JSService:
    """Клиент для Node.js микросервиса с Bitrix24 JS SDK"""
    
    def __init__(self, service_url: str = "http://localhost:3000"):
        self.service_url = service_url
    
    def init(self, webhook_url: str):
        """Инициализация SDK"""
        response = requests.post(
            f"{self.service_url}/init",
            json={"webhook_url": webhook_url}
        )
        return response.json()
    
    def get_all_leads(self, filter_params: dict = None):
        """Получение всех лидов"""
        response = requests.post(
            f"{self.service_url}/leads/all",
            json={"filter": filter_params or {}}
        )
        return response.json()["leads"]
    
    def batch_request(self, commands: list):
        """Batch запрос"""
        response = requests.post(
            f"{self.service_url}/batch",
            json={"commands": commands}
        )
        return response.json()["results"]
    
    def bulk_update_leads(self, updates: list):
        """Массовое обновление лидов"""
        response = requests.post(
            f"{self.service_url}/leads/bulk-update",
            json={"updates": updates}
        )
        return response.json()["results"]
    
    def health_check(self):
        """Проверка здоровья API"""
        response = requests.get(f"{self.service_url}/health")
        return response.json()
    
    def ping(self):
        """Измерение скорости ответа"""
        response = requests.get(f"{self.service_url}/ping")
        return response.json()["responseTime"]

# Использование
service = Bitrix24JSService()
service.init("https://your-domain.bitrix24.ru/rest/1/xxxxx/")

# Получение всех новых лидов
leads = service.get_all_leads({"STATUS_ID": "NEW"})

# Массовое обновление
updates = [
    {"id": 1, "fields": {"TITLE": "Обновленный лид 1"}},
    {"id": 2, "fields": {"TITLE": "Обновленный лид 2"}},
]
results = service.bulk_update_leads(updates)
```

## Интеграция с AI

### Массовый анализ лидов

```python
from ai_services.openai_service import OpenAIService
from bitrix24.js_integration import Bitrix24JSService

def analyze_all_leads():
    """Анализ всех новых лидов через AI"""
    
    service = Bitrix24JSService()
    ai = OpenAIService()
    
    # Получаем все новые лиды
    leads = service.get_all_leads({"STATUS_ID": "NEW"})
    
    # Анализируем через AI
    updates = []
    for lead in leads:
        analysis = ai.analyze_lead(lead)
        
        # Подготавливаем обновление
        updates.append({
            "id": lead["ID"],
            "fields": {
                "UF_AI_SCORE": analysis.get("score", 0),
                "COMMENTS": f"AI Анализ: {analysis.get('summary', '')}"
            }
        })
    
    # Массово обновляем все лиды
    results = service.bulk_update_leads(updates)
    
    return results
```

## Мониторинг и логирование

### Использование Logger из JS SDK

```javascript
import { LoggerBrowser } from '@bitrix24/b24jssdk';

const logger = LoggerBrowser.build('MyApp', {
    level: 'info'
});

logger.info('Lead processed', { leadId: 123 });
logger.error('Failed to update lead', { error: err.message });
```

### Отправка логов в Telegram

```javascript
import { LoggerBrowser, TelegramHandler } from '@bitrix24/b24jssdk';

const logger = LoggerBrowser.build('MyApp');

// Добавляем Telegram handler
logger.addHandler(new TelegramHandler({
    botToken: 'YOUR_BOT_TOKEN',
    chatId: 'YOUR_CHAT_ID',
    level: 'error' // Отправлять только ошибки
}));

logger.error('Critical error in lead processing', { 
    leadId: 123,
    error: 'Database connection failed'
});
```

## Лучшие практики

### 1. Используйте CallListV3 вместо ручной пагинации

❌ Плохо:
```python
# Ручная пагинация
all_leads = []
start = 0
while True:
    leads = bitrix.get_leads({"start": start})
    if not leads:
        break
    all_leads.extend(leads)
    start += 50
```

✅ Хорошо:
```python
# Автоматическая пагинация
all_leads = b24_js.get_all_leads()
```

### 2. Используйте BatchByChunkV3 для массовых операций

❌ Плохо:
```python
# Последовательные запросы
for lead_id in lead_ids:
    bitrix.update_lead(lead_id, fields)
```

✅ Хорошо:
```python
# Batch запрос
commands = [
    {"method": "crm.lead.update", "params": {"id": lid, "fields": fields}}
    for lid in lead_ids
]
results = b24_js.batch_request(commands)
```

### 3. Используйте FetchListV3 для больших объемов

```python
# Для обработки миллионов записей
for deal in b24_js.stream_deals():
    process_deal(deal)
    # Память не переполняется
```

## Troubleshooting

### Ошибка: "Cannot find module '@bitrix24/b24jssdk'"

Решение:
```bash
cd bitrix24/js_scripts
npm install
```

### Ошибка: "Node.js not found"

Установите Node.js с https://nodejs.org/

### Медленная работа

Используйте:
- `BatchByChunkV3` для массовых операций
- `FetchListV3` для больших объемов
- Кэширование для часто запрашиваемых данных
