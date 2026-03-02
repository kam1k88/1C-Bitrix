"""
Примеры использования b24pysdk в проекте
Демонстрирует основные возможности официального SDK
"""

from bitrix24.sdk_client import Bitrix24SDKClient, create_client_from_webhook
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_basic_operations():
    """Пример 1: Базовые операции с лидами"""
    print("\n=== Пример 1: Базовые операции ===\n")
    
    # Создание клиента из webhook URL
    client = create_client_from_webhook(settings.BITRIX24_WEBHOOK_URL)
    
    # Получение списка лидов
    leads = client.get_leads(
        filter_params={"STATUS_ID": "NEW"},
        limit=10
    )
    print(f"Найдено новых лидов: {len(leads)}")
    
    # Получение конкретного лида
    if leads:
        lead = client.get_lead(int(leads[0]["ID"]))
        print(f"Лид: {lead.get('TITLE')}")
        
        # Обновление лида
        client.update_lead(
            int(leads[0]["ID"]),
            {"COMMENTS": "Обновлено через b24pysdk"}
        )
        print("Лид обновлен")
        
        # Добавление комментария
        client.add_comment(
            entity_type="lead",
            entity_id=int(leads[0]["ID"]),
            comment="Тестовый комментарий через SDK"
        )
        print("Комментарий добавлен")


def example_2_pagination():
    """Пример 2: Работа с пагинацией"""
    print("\n=== Пример 2: Пагинация ===\n")
    
    client = create_client_from_webhook(settings.BITRIX24_WEBHOOK_URL)
    
    # Получение ВСЕХ лидов с автоматической пагинацией
    # SDK автоматически делает несколько запросов
    all_leads = client.get_leads()  # Без limit получаем все
    print(f"Всего лидов в системе: {len(all_leads)}")
    
    # Получение всех сделок
    all_deals = client.get_deals()
    print(f"Всего сделок в системе: {len(all_deals)}")


def example_3_batch_operations():
    """Пример 3: Batch операции"""
    print("\n=== Пример 3: Batch операции ===\n")
    
    client = create_client_from_webhook(settings.BITRIX24_WEBHOOK_URL)
    
    # Получаем несколько лидов
    leads = client.get_leads(limit=5)
    
    if len(leads) >= 3:
        # Массовое обновление лидов
        updates = [
            {
                "id": int(leads[0]["ID"]),
                "fields": {"COMMENTS": "Batch update 1"}
            },
            {
                "id": int(leads[1]["ID"]),
                "fields": {"COMMENTS": "Batch update 2"}
            },
            {
                "id": int(leads[2]["ID"]),
                "fields": {"COMMENTS": "Batch update 3"}
            }
        ]
        
        results = client.batch_update_leads(updates)
        print(f"Обновлено лидов: {len([r for r in results if r])}")
    
    # Массовое создание сделок
    deals_data = [
        {
            "TITLE": "Тестовая сделка 1",
            "STAGE_ID": "NEW",
            "OPPORTUNITY": 10000,
            "CURRENCY_ID": "RUB"
        },
        {
            "TITLE": "Тестовая сделка 2",
            "STAGE_ID": "NEW",
            "OPPORTUNITY": 20000,
            "CURRENCY_ID": "RUB"
        }
    ]
    
    deal_ids = client.batch_create_deals(deals_data)
    print(f"Создано сделок: {len(deal_ids)}")
    print(f"ID сделок: {deal_ids}")


def example_4_error_handling():
    """Пример 4: Обработка ошибок"""
    print("\n=== Пример 4: Обработка ошибок ===\n")
    
    from b24pysdk.error import BitrixAPIError, BitrixRequestTimeout
    
    client = create_client_from_webhook(settings.BITRIX24_WEBHOOK_URL)
    
    try:
        # Попытка получить несуществующий лид
        lead = client.get_lead(999999999)
        print(f"Лид найден: {lead}")
    except BitrixAPIError as e:
        print(f"Ошибка API: {e.error}")
        print(f"Описание: {e.error_description}")
    except BitrixRequestTimeout:
        print("Превышено время ожидания запроса")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


def example_5_fields_metadata():
    """Пример 5: Получение метаданных полей"""
    print("\n=== Пример 5: Метаданные полей ===\n")
    
    client = create_client_from_webhook(settings.BITRIX24_WEBHOOK_URL)
    
    # Получение описания полей лида
    lead_fields = client.get_fields("lead")
    print(f"Полей в лиде: {len(lead_fields)}")
    
    # Вывод некоторых полей
    for field_name in ["TITLE", "STATUS_ID", "OPPORTUNITY"]:
        if field_name in lead_fields:
            field = lead_fields[field_name]
            print(f"  {field_name}: {field.get('title')} ({field.get('type')})")
    
    # Получение описания полей сделки
    deal_fields = client.get_fields("deal")
    print(f"\nПолей в сделке: {len(deal_fields)}")


def example_6_users_and_departments():
    """Пример 6: Работа с пользователями"""
    print("\n=== Пример 6: Пользователи ===\n")
    
    client = create_client_from_webhook(settings.BITRIX24_WEBHOOK_URL)
    
    # Получение текущего пользователя
    current_user = client.get_current_user()
    print(f"Текущий пользователь: {current_user.get('NAME')} {current_user.get('LAST_NAME')}")
    print(f"Email: {current_user.get('EMAIL')}")
    
    # Получение всех пользователей
    users = client.get_users()
    print(f"\nВсего пользователей: {len(users)}")
    
    # Вывод активных пользователей
    active_users = [u for u in users if u.get("ACTIVE") == True]
    print(f"Активных пользователей: {len(active_users)}")


def example_7_contacts_and_companies():
    """Пример 7: Работа с контактами и компаниями"""
    print("\n=== Пример 7: Контакты и компании ===\n")
    
    client = create_client_from_webhook(settings.BITRIX24_WEBHOOK_URL)
    
    # Создание контакта
    contact_id = client.create_contact({
        "NAME": "Иван",
        "LAST_NAME": "Тестовый",
        "PHONE": [{"VALUE": "+79991234567", "VALUE_TYPE": "WORK"}],
        "EMAIL": [{"VALUE": "test@example.com", "VALUE_TYPE": "WORK"}]
    })
    print(f"Создан контакт ID: {contact_id}")
    
    # Создание компании
    company_id = client.create_company({
        "TITLE": "Тестовая компания ООО",
        "PHONE": [{"VALUE": "+79991234567", "VALUE_TYPE": "WORK"}],
        "EMAIL": [{"VALUE": "info@test-company.ru", "VALUE_TYPE": "WORK"}]
    })
    print(f"Создана компания ID: {company_id}")
    
    # Получение списка контактов
    contacts = client.get_contacts(limit=10)
    print(f"\nВсего контактов (первые 10): {len(contacts)}")
    
    # Получение списка компаний
    companies = client.get_companies(limit=10)
    print(f"Всего компаний (первые 10): {len(companies)}")


def example_8_oauth_authentication():
    """Пример 8: OAuth аутентификация"""
    print("\n=== Пример 8: OAuth аутентификация ===\n")
    
    # Для OAuth нужны дополнительные параметры
    if settings.BITRIX24_ACCESS_TOKEN and settings.BITRIX24_CLIENT_ID:
        client = Bitrix24SDKClient(
            domain=settings.BITRIX24_DOMAIN,
            auth_token=settings.BITRIX24_ACCESS_TOKEN,
            auth_type="oauth",
            client_id=settings.BITRIX24_CLIENT_ID,
            client_secret=settings.BITRIX24_CLIENT_SECRET,
            refresh_token=settings.BITRIX24_REFRESH_TOKEN,
            prefer_api_version=3  # Можно использовать API v3
        )
        
        user = client.get_current_user()
        print(f"OAuth авторизация успешна: {user.get('NAME')}")
    else:
        print("OAuth не настроен. Используйте webhook для тестирования.")


def run_all_examples():
    """Запуск всех примеров"""
    examples = [
        example_1_basic_operations,
        example_2_pagination,
        example_3_batch_operations,
        example_4_error_handling,
        example_5_fields_metadata,
        example_6_users_and_departments,
        example_7_contacts_and_companies,
        example_8_oauth_authentication
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            logger.error(f"Ошибка в {example.__name__}: {e}")
        
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    print("Примеры использования b24pysdk")
    print("="*60)
    
    # Запуск всех примеров
    run_all_examples()
    
    print("\nВсе примеры выполнены!")
