# Настройка интеграции с Bitrix24

## Получение Webhook URL

1. Войдите в ваш Bitrix24
2. Перейдите: Меню → Разработчикам → Другое → Входящий вебхук
3. Нажмите "Создать вебхук"
4. Выберите права доступа:
   - CRM (все операции)
   - Задачи (чтение)
   - Диск (чтение/запись)
5. Скопируйте URL вида: `https://your-domain.bitrix24.ru/rest/1/xxxxx/`

## Настройка автоматизации в Bitrix24

### Автоматическая обработка новых лидов

1. Откройте CRM → Лиды → Настройки → Автоматизация
2. Создайте новое правило:
   - Триггер: "При создании лида"
   - Действие: "Вызвать webhook"
   - URL: `http://your-server:8000/webhook/bitrix/lead`
   - Метод: POST
   - Тело запроса:
   ```json
   {
     "lead_id": "{=Document:ID}"
   }
   ```

### Кнопка "Сгенерировать КП"

1. Откройте CRM → Лиды → Настройки → Пользовательские поля
2. Создайте поле типа "Кнопка":
   - Название: "Сгенерировать КП"
   - Код: `UF_GENERATE_OFFER`
   - Webhook URL: `http://your-server:8000/api/generate-offer`

### Автоматическое создание заказа в 1С

1. CRM → Сделки → Автоматизация
2. Триггер: "При переходе в стадию 'Счет выставлен'"
3. Действие: "Вызвать webhook"
4. URL: `http://your-server:8000/api/sync-deal-to-1c`

## Настройка пользовательских полей

### Для лидов

Создайте следующие поля:

1. `UF_AI_SCORE` - Число - "AI оценка качества"
2. `UF_AI_PROBABILITY` - Число - "Вероятность конверсии %"
3. `UF_CLIENT_IN_1C` - Да/Нет - "Клиент есть в 1С"

### Для сделок

1. `UF_1C_ORDER_ID` - Строка - "ID заказа в 1С"
2. `UF_1C_ORDER_NUMBER` - Строка - "Номер заказа в 1С"

### Для компаний

1. `UF_1C_CLIENT_ID` - Строка - "ID клиента в 1С"
2. `UF_LAST_SYNC` - Дата/время - "Последняя синхронизация"

## Использование Bitrix24 REST API

### Примеры запросов

#### Получить список лидов

```bash
curl "https://your-domain.bitrix24.ru/rest/1/xxxxx/crm.lead.list"
```

#### Обновить лид

```bash
curl -X POST "https://your-domain.bitrix24.ru/rest/1/xxxxx/crm.lead.update" \
  -d "id=123&fields[STATUS_ID]=NEW"
```

#### Добавить комментарий

```bash
curl -X POST "https://your-domain.bitrix24.ru/rest/1/xxxxx/crm.timeline.comment.add" \
  -d "fields[ENTITY_ID]=123&fields[ENTITY_TYPE]=lead&fields[COMMENT]=Тест"
```

## Интеграция с Bitrix24 через MCP

Для более продвинутой интеграции можно использовать MCP сервер:

### Установка MCP сервера для Bitrix24

1. Создайте файл `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "bitrix24": {
      "command": "node",
      "args": ["path/to/bitrix24-mcp-server/index.js"],
      "env": {
        "BITRIX24_WEBHOOK": "https://your-domain.bitrix24.ru/rest/1/xxxxx/"
      },
      "disabled": false,
      "autoApprove": ["bitrix24_get_leads", "bitrix24_get_deals"]
    }
  }
}
```

2. Перезапустите Kiro или переподключите MCP сервер

### Использование MCP инструментов

После настройки MCP вы сможете использовать инструменты напрямую:

- `bitrix24_get_leads` - Получить лиды
- `bitrix24_create_lead` - Создать лид
- `bitrix24_update_lead` - Обновить лид
- `bitrix24_get_deals` - Получить сделки
- `bitrix24_create_deal` - Создать сделку

## Настройка уведомлений

### Уведомления в Telegram

1. Создайте бота через @BotFather
2. Получите токен бота
3. Добавьте в `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

4. Настройте отправку уведомлений при важных событиях

### Уведомления в Bitrix24

Используйте метод `im.notify` для отправки уведомлений пользователям:

```python
def notify_manager(user_id: int, message: str):
    bitrix._call("im.notify", {
        "to": user_id,
        "message": message,
        "type": "SYSTEM"
    })
```

## Мониторинг интеграции

### Dashboard в Bitrix24

Создайте отчет с метриками:
- Количество обработанных лидов
- Средняя AI-оценка лидов
- Конверсия лидов с высокой оценкой
- Количество синхронизированных заказов

### Логирование

Все действия логируются в системе. Просмотр логов:

```bash
tail -f logs/bitrix24_integration.log
```

## Troubleshooting

### Webhook не срабатывает

1. Проверьте доступность вашего сервера из интернета
2. Убедитесь, что порт открыт
3. Проверьте логи Bitrix24: Настройки → Журнал событий

### Ошибка прав доступа

Убедитесь, что webhook имеет необходимые права:
- CRM: чтение и запись
- Задачи: чтение
- Диск: чтение и запись

### Медленная работа

1. Используйте batch-запросы для массовых операций
2. Кэшируйте часто используемые данные
3. Оптимизируйте фильтры запросов
