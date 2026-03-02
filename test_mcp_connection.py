"""
Тест подключения к Bitrix24 через MCP
"""

from bitrix24.mcp_client import Bitrix24MCPClient
from datetime import datetime

def test_connection():
    """Тестирование подключения к Bitrix24 MCP"""
    
    print("=" * 60)
    print("Тест подключения к Bitrix24 MCP")
    print("=" * 60)
    
    try:
        # Создаем клиент
        client = Bitrix24MCPClient()
        print("✅ MCP клиент создан")
        
        # Проверяем токен
        print("\n📋 Проверка токена...")
        token_info = client.check_token_expiry()
        
        if token_info.get("error"):
            print(f"❌ Ошибка проверки токена: {token_info['error']}")
            return False
        
        print(f"   Domain: {token_info['domain']}")
        print(f"   User ID: {token_info['user_id']}")
        print(f"   Issued: {token_info['issued_at']}")
        print(f"   Expires: {token_info['expires_at']}")
        print(f"   Days until expiry: {token_info['days_until_expiry']}")
        
        if token_info['is_expired']:
            print("❌ Токен истек! Получите новый токен в Bitrix24")
            return False
        elif token_info['days_until_expiry'] < 30:
            print(f"⚠️  Токен истекает через {token_info['days_until_expiry']} дней")
        else:
            print("✅ Токен действителен")
        
        # Тест получения текущего пользователя
        print("\n👤 Получение текущего пользователя...")
        try:
            user = client.get_current_user()
            print(f"✅ Пользователь: {user.get('NAME')} {user.get('LAST_NAME')}")
            print(f"   Email: {user.get('EMAIL')}")
        except Exception as e:
            print(f"❌ Ошибка получения пользователя: {str(e)}")
            return False
        
        # Тест получения лидов
        print("\n📊 Получение лидов...")
        try:
            leads = client.get_leads()
            print(f"✅ Получено {len(leads)} лидов")
            
            if leads:
                lead = leads[0]
                print(f"   Первый лид: {lead.get('TITLE')} (ID: {lead.get('ID')})")
        except Exception as e:
            print(f"❌ Ошибка получения лидов: {str(e)}")
            return False
        
        # Тест получения сделок
        print("\n💼 Получение сделок...")
        try:
            deals = client.get_deals()
            print(f"✅ Получено {len(deals)} сделок")
        except Exception as e:
            print(f"❌ Ошибка получения сделок: {str(e)}")
            return False
        
        # Тест получения задач
        print("\n✓ Получение задач...")
        try:
            tasks = client.get_tasks()
            print(f"✅ Получено {len(tasks)} задач")
        except Exception as e:
            print(f"❌ Ошибка получения задач: {str(e)}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ Все тесты пройдены успешно!")
        print("=" * 60)
        print("\n🚀 Система готова к работе!")
        print("\nСледующие шаги:")
        print("1. Запустите main.py для старта API сервера")
        print("2. Используйте AI для автоматизации через MCP")
        print("3. Изучите примеры в docs/bitrix24_mcp_setup.md")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}")
        print("\nПроверьте:")
        print("1. Правильность токена в .env.mcp")
        print("2. Доступность https://mcp-dev.bitrix24.tech/mcp")
        print("3. Срок действия токена")
        return False

if __name__ == "__main__":
    test_connection()
