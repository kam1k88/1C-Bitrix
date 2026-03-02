"""
Скрипт для отладки и проверки основных компонентов системы
"""
import sys
import os
from typing import Dict, Any

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_status(message: str, status: str = "info"):
    """Вывод статуса с цветом"""
    colors = {
        "success": GREEN,
        "error": RED,
        "warning": YELLOW,
        "info": BLUE
    }
    color = colors.get(status, RESET)
    symbol = {
        "success": "✓",
        "error": "✗",
        "warning": "⚠",
        "info": "ℹ"
    }
    print(f"{color}{symbol.get(status, '•')} {message}{RESET}")


def check_environment() -> Dict[str, Any]:
    """Проверка переменных окружения"""
    print("\n" + "="*60)
    print("1. ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("="*60)
    
    results = {}
    required_vars = {
        "BITRIX24_WEBHOOK_URL": "Bitrix24 Webhook URL",
        "OPENAI_API_KEY": "OpenAI API Key",
    }
    
    optional_vars = {
        "ANTHROPIC_API_KEY": "Anthropic API Key",
        "ONEC_BASE_URL": "1C Base URL",
        "BITRIX24_DOMAIN": "Bitrix24 Domain (OAuth)",
    }
    
    # Проверка обязательных переменных
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print_status(f"{description}: установлен", "success")
            results[var] = True
        else:
            print_status(f"{description}: НЕ УСТАНОВЛЕН", "error")
            results[var] = False
    
    # Проверка опциональных переменных
    print("\nОпциональные переменные:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print_status(f"{description}: установлен", "success")
        else:
            print_status(f"{description}: не установлен", "warning")
    
    return results


def check_imports() -> Dict[str, Any]:
    """Проверка импортов модулей"""
    print("\n" + "="*60)
    print("2. ПРОВЕРКА ИМПОРТОВ МОДУЛЕЙ")
    print("="*60)
    
    results = {}
    modules = {
        "fastapi": "FastAPI",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "b24pysdk": "Bitrix24 SDK",
        "pydantic": "Pydantic",
        "dotenv": "Python-dotenv"
    }
    
    for module, name in modules.items():
        try:
            __import__(module)
            print_status(f"{name}: установлен", "success")
            results[module] = True
        except ImportError as e:
            print_status(f"{name}: НЕ УСТАНОВЛЕН ({str(e)})", "error")
            results[module] = False
    
    return results


def check_project_structure() -> Dict[str, Any]:
    """Проверка структуры проекта"""
    print("\n" + "="*60)
    print("3. ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА")
    print("="*60)
    
    results = {}
    required_files = {
        "config/settings.py": "Конфигурация",
        "bitrix24/sdk_client.py": "Bitrix24 SDK Client",
        "ai_services/openai_service.py": "OpenAI Service",
        "ai_services/claude_service.py": "Claude Service",
        "automation/lead_processor.py": "Lead Processor",
        "main.py": "FastAPI Application",
        "requirements.txt": "Dependencies"
    }
    
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print_status(f"{description}: найден", "success")
            results[file_path] = True
        else:
            print_status(f"{description}: НЕ НАЙДЕН", "error")
            results[file_path] = False
    
    return results


def check_config() -> Dict[str, Any]:
    """Проверка конфигурации"""
    print("\n" + "="*60)
    print("4. ПРОВЕРКА КОНФИГУРАЦИИ")
    print("="*60)
    
    results = {}
    
    try:
        from config.settings import settings
        print_status("Settings загружены успешно", "success")
        results["settings_load"] = True
        
        # Проверка основных настроек
        if settings.BITRIX24_WEBHOOK_URL or settings.BITRIX24_DOMAIN:
            print_status("Bitrix24 настроен", "success")
            results["bitrix24_config"] = True
        else:
            print_status("Bitrix24 НЕ настроен", "error")
            results["bitrix24_config"] = False
        
        if settings.OPENAI_API_KEY:
            print_status("OpenAI API настроен", "success")
            results["openai_config"] = True
        else:
            print_status("OpenAI API НЕ настроен", "error")
            results["openai_config"] = False
        
        print(f"\nТекущие настройки:")
        print(f"  - DEBUG: {settings.DEBUG}")
        print(f"  - LOG_LEVEL: {settings.LOG_LEVEL}")
        print(f"  - DEFAULT_AI_MODEL: {settings.DEFAULT_AI_MODEL}")
        print(f"  - MAX_TOKENS: {settings.MAX_TOKENS}")
        
    except Exception as e:
        print_status(f"Ошибка загрузки конфигурации: {str(e)}", "error")
        results["settings_load"] = False
    
    return results


def check_sdk_client() -> Dict[str, Any]:
    """Проверка SDK клиента"""
    print("\n" + "="*60)
    print("5. ПРОВЕРКА BITRIX24 SDK CLIENT")
    print("="*60)
    
    results = {}
    
    try:
        from bitrix24.sdk_client import Bitrix24SDKClient, create_client_from_webhook
        print_status("SDK Client импортирован успешно", "success")
        results["import"] = True
        
        # Проверка создания клиента (без реального подключения)
        webhook_url = os.getenv("BITRIX24_WEBHOOK_URL")
        if webhook_url:
            try:
                client = create_client_from_webhook(webhook_url)
                print_status("SDK Client создан успешно", "success")
                results["client_creation"] = True
                
                # Проверка методов
                methods = ["get_leads", "get_lead", "create_lead", "update_lead", 
                          "get_deals", "batch_update_leads"]
                for method in methods:
                    if hasattr(client, method):
                        print_status(f"Метод {method}: доступен", "success")
                    else:
                        print_status(f"Метод {method}: НЕ НАЙДЕН", "error")
                
            except Exception as e:
                print_status(f"Ошибка создания клиента: {str(e)}", "error")
                results["client_creation"] = False
        else:
            print_status("BITRIX24_WEBHOOK_URL не установлен, пропуск теста", "warning")
            results["client_creation"] = None
            
    except Exception as e:
        print_status(f"Ошибка импорта SDK Client: {str(e)}", "error")
        results["import"] = False
    
    return results


def check_ai_services() -> Dict[str, Any]:
    """Проверка AI сервисов"""
    print("\n" + "="*60)
    print("6. ПРОВЕРКА AI СЕРВИСОВ")
    print("="*60)
    
    results = {}
    
    # OpenAI Service
    try:
        from ai_services.openai_service import OpenAIService
        print_status("OpenAI Service импортирован", "success")
        results["openai_import"] = True
        
        if os.getenv("OPENAI_API_KEY"):
            try:
                service = OpenAIService()
                print_status("OpenAI Service инициализирован", "success")
                results["openai_init"] = True
            except Exception as e:
                print_status(f"Ошибка инициализации OpenAI: {str(e)}", "error")
                results["openai_init"] = False
        else:
            print_status("OPENAI_API_KEY не установлен", "warning")
            results["openai_init"] = None
            
    except Exception as e:
        print_status(f"Ошибка импорта OpenAI Service: {str(e)}", "error")
        results["openai_import"] = False
    
    # Claude Service
    try:
        from ai_services.claude_service import ClaudeService
        print_status("Claude Service импортирован", "success")
        results["claude_import"] = True
        
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                service = ClaudeService()
                print_status("Claude Service инициализирован", "success")
                results["claude_init"] = True
            except Exception as e:
                print_status(f"Ошибка инициализации Claude: {str(e)}", "error")
                results["claude_init"] = False
        else:
            print_status("ANTHROPIC_API_KEY не установлен (опционально)", "warning")
            results["claude_init"] = None
            
    except Exception as e:
        print_status(f"Ошибка импорта Claude Service: {str(e)}", "error")
        results["claude_import"] = False
    
    return results


def check_lead_processor() -> Dict[str, Any]:
    """Проверка Lead Processor"""
    print("\n" + "="*60)
    print("7. ПРОВЕРКА LEAD PROCESSOR")
    print("="*60)
    
    results = {}
    
    try:
        from automation.lead_processor import LeadProcessor
        print_status("LeadProcessor импортирован", "success")
        results["import"] = True
        
        try:
            processor = LeadProcessor()
            print_status("LeadProcessor инициализирован", "success")
            results["init"] = True
            
            # Проверка методов
            methods = ["process_new_lead", "generate_offer_for_lead", 
                      "analyze_customer_request"]
            for method in methods:
                if hasattr(processor, method):
                    print_status(f"Метод {method}: доступен", "success")
                else:
                    print_status(f"Метод {method}: НЕ НАЙДЕН", "error")
                    
        except Exception as e:
            print_status(f"Ошибка инициализации: {str(e)}", "error")
            results["init"] = False
            
    except Exception as e:
        print_status(f"Ошибка импорта LeadProcessor: {str(e)}", "error")
        results["import"] = False
    
    return results


def generate_report(all_results: Dict[str, Dict[str, Any]]):
    """Генерация итогового отчета"""
    print("\n" + "="*60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("="*60)
    
    total_checks = 0
    passed_checks = 0
    failed_checks = 0
    warnings = 0
    
    for category, results in all_results.items():
        for key, value in results.items():
            total_checks += 1
            if value is True:
                passed_checks += 1
            elif value is False:
                failed_checks += 1
            elif value is None:
                warnings += 1
    
    print(f"\nВсего проверок: {total_checks}")
    print_status(f"Успешно: {passed_checks}", "success")
    print_status(f"Ошибок: {failed_checks}", "error" if failed_checks > 0 else "success")
    print_status(f"Предупреждений: {warnings}", "warning" if warnings > 0 else "info")
    
    if failed_checks == 0:
        print_status("\n✓ Все критические проверки пройдены!", "success")
        print_status("Система готова к работе", "success")
        return 0
    else:
        print_status(f"\n✗ Обнаружено {failed_checks} ошибок", "error")
        print_status("Необходимо исправить ошибки перед запуском", "error")
        return 1


def main():
    """Главная функция"""
    print(f"{BLUE}")
    print("="*60)
    print("  ОТЛАДКА И ПРОВЕРКА СИСТЕМЫ")
    print("  AI Integration Platform v2.0")
    print("="*60)
    print(f"{RESET}")
    
    all_results = {}
    
    # Выполнение всех проверок
    all_results["environment"] = check_environment()
    all_results["imports"] = check_imports()
    all_results["structure"] = check_project_structure()
    all_results["config"] = check_config()
    all_results["sdk_client"] = check_sdk_client()
    all_results["ai_services"] = check_ai_services()
    all_results["lead_processor"] = check_lead_processor()
    
    # Генерация отчета
    exit_code = generate_report(all_results)
    
    print("\n" + "="*60)
    print("Для запуска тестов используйте: pytest tests/ -v")
    print("Для запуска сервера: python main.py")
    print("="*60 + "\n")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
