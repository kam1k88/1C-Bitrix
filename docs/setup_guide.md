# Руководство по установке и настройке

## Требования

- Python 3.9+
- Доступ к Bitrix24 (webhook)
- API ключи OpenAI и/или Anthropic
- Доступ к 1С через HTTP-сервисы

## Шаг 1: Установка зависимостей

```bash
pip install -r requirements.txt
```

## Шаг 2: Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполните необходимые данные:

### Bitrix24 Webhook

1. Откройте Bitrix24
2. Перейдите в "Разработчикам" → "Другое" → "Входящий вебхук"
3. Создайте новый webhook с правами на CRM
4. Скопируйте URL в формате: `https://your-domain.bitrix24.ru/rest/1/xxxxx/`
5. Вставьте в `.env` как `BITRIX24_WEBHOOK_URL`

### OpenAI API Key

1. Зарегистрируйтесь на https://platform.openai.com
2. Перейдите в API Keys
3. Создайте новый ключ
4. Вставьте в `.env` как `OPENAI_API_KEY`

### Anthropic API Key

1. Зарегистрируйтесь на https://console.anthropic.com
2. Создайте API ключ
3. Вставьте в `.env` как `ANTHROPIC_API_KEY`

### 1С HTTP-сервисы

1. В 1С создайте HTTP-сервис для интеграции
2. Настройте методы: counterparties, products, orders, prices
3. Укажите URL, логин и пароль в `.env`

## Шаг 3: Запуск системы

```bash
python main.py
```

Система запустится на http://localhost:8000

## Шаг 4: Настройка webhook в Bitrix24

1. Откройте Bitrix24 → Настройки → Настройки CRM → Вебхуки
2. Создайте webhook на событие "Добавление лида"
3. URL обработчика: `http://your-server:8000/webhook/bitrix/lead`
4. Сохраните настройки

## Шаг 5: Проверка работы

### Тест API

```bash
curl http://localhost:8000/
```

Ответ: `{"message": "AI Integration Platform API", "status": "running"}`

### Тест получения лидов

```bash
curl http://localhost:8000/api/leads
```

### Тест анализа запроса

```bash
curl -X POST http://localhost:8000/api/analyze-request \
  -H "Content-Type: application/json" \
  -d '{"text": "Хочу заказать молочную продукцию на 50000 рублей"}'
```

## Развертывание в production

### Вариант 1: Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Запуск:
```bash
docker build -t ai-integration .
docker run -p 8000:8000 --env-file .env ai-integration
```

### Вариант 2: Systemd service

Создайте файл `/etc/systemd/system/ai-integration.service`:

```ini
[Unit]
Description=AI Integration Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ai-integration
Environment="PATH=/opt/ai-integration/venv/bin"
ExecStart=/opt/ai-integration/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl enable ai-integration
sudo systemctl start ai-integration
```

## Мониторинг и логи

Логи приложения доступны в stdout. Для production рекомендуется настроить:

- Sentry для отслеживания ошибок
- Prometheus для метрик
- ELK Stack для централизованных логов

## Безопасность

1. Используйте HTTPS для production
2. Ограничьте доступ к API через firewall
3. Регулярно обновляйте зависимости
4. Храните `.env` в безопасном месте
5. Используйте разные API ключи для dev/prod

## Troubleshooting

### Ошибка подключения к Bitrix24

Проверьте:
- Правильность webhook URL
- Права webhook (должны быть права на CRM)
- Доступность Bitrix24 из вашей сети

### Ошибка AI API

Проверьте:
- Наличие средств на балансе OpenAI/Anthropic
- Правильность API ключей
- Лимиты запросов

### Ошибка подключения к 1С

Проверьте:
- Доступность 1С сервера
- Правильность логина/пароля
- Настройки HTTP-сервиса в 1С
