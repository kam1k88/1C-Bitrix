# Тесты

## Структура тестов

```
tests/
├── __init__.py
├── test_config.py          # Тесты конфигурации
├── test_sdk_client.py      # Тесты Bitrix24 SDK Client
└── test_lead_processor.py  # Тесты LeadProcessor
```

## Запуск тестов

### Все тесты
```bash
pytest tests/ -v
```

### Конкретный файл
```bash
pytest tests/test_sdk_client.py -v
```

### Конкретный тест
```bash
pytest tests/test_sdk_client.py::TestBitrix24SDKClient::test_get_leads -v
```

### С покрытием кода
```bash
pytest tests/ --cov=. --cov-report=html
```

## Типы тестов

### Unit тесты
Тестируют отдельные компоненты в изоляции с использованием моков:
- `test_config.py` - тесты конфигурации
- `test_sdk_client.py` - тесты SDK клиента
- `test_lead_processor.py` - тесты обработчика лидов

### Integration тесты (планируются)
Тестируют взаимодействие компонентов с реальными API (требуют настроенные credentials).

## Моки и фикстуры

Тесты используют `unittest.mock` для изоляции компонентов:
- `Mock` - базовый мок объект
- `MagicMock` - мок с магическими методами
- `patch` - декоратор для подмены модулей

## Примеры

### Запуск с подробным выводом
```bash
pytest tests/ -v -s
```

### Запуск только быстрых тестов
```bash
pytest tests/ -m "not slow"
```

### Запуск с остановкой на первой ошибке
```bash
pytest tests/ -x
```

## Отладка

### Быстрая проверка системы
```bash
python quick_test.py
```

### Полная диагностика
```bash
python debug_check.py
```

## Добавление новых тестов

1. Создайте файл `test_<module_name>.py`
2. Создайте класс `Test<ClassName>`
3. Добавьте методы `test_<functionality>`
4. Используйте моки для внешних зависимостей

Пример:
```python
import pytest
from unittest.mock import Mock, patch

class TestMyClass:
    @patch('module.ExternalDependency')
    def test_my_method(self, mock_dependency):
        # Arrange
        mock_dependency.return_value = "mocked_value"
        
        # Act
        result = my_function()
        
        # Assert
        assert result == "expected_value"
        mock_dependency.assert_called_once()
```

## Требования

Установите зависимости для тестирования:
```bash
pip install pytest pytest-mock pytest-cov pytest-asyncio
```

Или используйте requirements.txt:
```bash
pip install -r requirements.txt
```
