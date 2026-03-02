"""
Быстрая проверка основных компонентов
"""
import sys

print("="*60)
print("БЫСТРАЯ ПРОВЕРКА КОМПОНЕНТОВ")
print("="*60)

# 1. Проверка импортов
print("\n1. Проверка импортов...")
try:
    from config.settings import settings
    print("✓ config.settings")
except Exception as e:
    print(f"✗ config.settings: {e}")
    sys.exit(1)

try:
    from bitrix24.sdk_client import Bitrix24SDKClient
    print("✓ bitrix24.sdk_client")
except Exception as e:
    print(f"✗ bitrix24.sdk_client: {e}")
    sys.exit(1)

try:
    from ai_services.openai_service import OpenAIService
    print("✓ ai_services.openai_service")
except Exception as e:
    print(f"✗ ai_services.openai_service: {e}")
    sys.exit(1)

try:
    from ai_services.claude_service import ClaudeService
    print("✓ ai_services.claude_service")
except Exception as e:
    print(f"✗ ai_services.claude_service: {e}")
    sys.exit(1)

try:
    from automation.lead_processor import LeadProcessor
    print("✓ automation.lead_processor")
except Exception as e:
    print(f"✗ automation.lead_processor: {e}")
    sys.exit(1)

# 2. Проверка конфигурации
print("\n2. Проверка конфигурации...")
print(f"  DEBUG: {settings.DEBUG}")
print(f"  LOG_LEVEL: {settings.LOG_LEVEL}")
print(f"  DEFAULT_AI_MODEL: {settings.DEFAULT_AI_MODEL}")
print(f"  BITRIX24_WEBHOOK_URL: {'установлен' if settings.BITRIX24_WEBHOOK_URL else 'не установлен'}")
print(f"  OPENAI_API_KEY: {'установлен' if settings.OPENAI_API_KEY else 'не установлен'}")

# 3. Проверка создания клиентов
print("\n3. Проверка создания клиентов...")
try:
    if settings.BITRIX24_WEBHOOK_URL:
        client = Bitrix24SDKClient(webhook_url=settings.BITRIX24_WEBHOOK_URL)
        print("✓ Bitrix24SDKClient создан")
    else:
        print("⚠ BITRIX24_WEBHOOK_URL не установлен")
except Exception as e:
    print(f"✗ Ошибка создания Bitrix24SDKClient: {e}")

try:
    if settings.OPENAI_API_KEY:
        openai_service = OpenAIService()
        print("✓ OpenAIService создан")
    else:
        print("⚠ OPENAI_API_KEY не установлен")
except Exception as e:
    print(f"✗ Ошибка создания OpenAIService: {e}")

# 4. Проверка LeadProcessor
print("\n4. Проверка LeadProcessor...")
try:
    processor = LeadProcessor()
    print("✓ LeadProcessor создан")
    print(f"  Методы: {[m for m in dir(processor) if not m.startswith('_')][:5]}...")
except Exception as e:
    print(f"✗ Ошибка создания LeadProcessor: {e}")

print("\n" + "="*60)
print("✓ БАЗОВАЯ ПРОВЕРКА ЗАВЕРШЕНА")
print("="*60)
print("\nДля полной проверки запустите: python debug_check.py")
print("Для запуска тестов: pytest tests/ -v")
