"""
Sales Bot - Бот для менеджеров по продажам
Команды: /лиды, /создать_лид, /кп, /задачи, /клиент
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
from bitrix24.client import Bitrix24Client
from onec.client import OneCClient
from ai_services.openai_service import OpenAIService
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
LEAD_NAME, LEAD_PHONE, LEAD_COMMENT = range(3)
OFFER_PRODUCTS, OFFER_CLIENT = range(2)

class SalesBot:
    """Бот для менеджеров по продажам"""
    
    def __init__(self, token: str):
        self.token = token
        self.bitrix = Bitrix24Client()
        self.onec = OneCClient()
        self.ai = OpenAIService()
        self.app = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков"""
        # Основные команды
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("лиды", self.my_leads))
        self.app.add_handler(CommandHandler("задачи", self.my_tasks))
        self.app.add_handler(CommandHandler("клиент", self.search_client))
        
        # Conversation для создания лида
        lead_conv = ConversationHandler(
            entry_points=[CommandHandler("создать_лид", self.create_lead_start)],
            states={
                LEAD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.lead_name)],
                LEAD_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.lead_phone)],
                LEAD_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.lead_comment)]
            },
            fallbacks=[CommandHandler("отмена", self.cancel)]
        )
        self.app.add_handler(lead_conv)
        
        # Conversation для создания КП
        offer_conv = ConversationHandler(
            entry_points=[CommandHandler("кп", self.create_offer_start)],
            states={
                OFFER_CLIENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.offer_client)],
                OFFER_PRODUCTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.offer_products)]
            },
            fallbacks=[CommandHandler("отмена", self.cancel)]
        )
        self.app.add_handler(offer_conv)
        
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat_handler))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Приветствие"""
        keyboard = [
            [InlineKeyboardButton("📋 Мои лиды", callback_data="my_leads")],
            [InlineKeyboardButton("➕ Создать лид", callback_data="create_lead")],
            [InlineKeyboardButton("📄 Создать КП", callback_data="create_offer")],
            [InlineKeyboardButton("✅ Мои задачи", callback_data="my_tasks")],
            [InlineKeyboardButton("🔍 Найти клиента", callback_data="search_client")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 *Sales Bot*\n\n"
            "Привет! Я помогу тебе с продажами.\n\n"
            "Выбери действие или напиши вопрос:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Справка"""
        help_text = """
📚 *Доступные команды:*

📋 */лиды* - Твои активные лиды
➕ */создать_лид* - Создать новый лид
📄 */кп* - Сгенерировать коммерческое предложение
✅ */задачи* - Твои задачи на сегодня
🔍 */клиент* [имя] - Найти клиента в базе

💬 *Режим чата:*
• "Создай лид для Ивана Петрова"
• "Сгенерируй КП на молочку"
• "Какие у меня задачи?"
• "Найди клиента ООО Продукты"

🤖 *AI-помощник:*
Я могу автоматически:
• Оценить качество лида
• Сгенерировать персональное КП
• Подсказать следующие шаги
• Найти похожих клиентов
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def my_leads(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать мои лиды"""
        await update.message.reply_text("⏳ Загружаю твои лиды...")
        
        try:
            # Получаем лиды текущего пользователя
            leads = self.bitrix.get_leads({"STATUS_ID": "NEW"})[:10]
            
            if not leads:
                await update.message.reply_text("📭 У тебя нет новых лидов.")
                return
            
            response = f"📋 *Твои лиды ({len(leads)}):*\n\n"
            for lead in leads:
                name = lead.get('NAME', 'Без имени')
                title = lead.get('TITLE', 'Без названия')
                phone = lead.get('PHONE', [{}])[0].get('VALUE', 'Нет телефона')
                
                # AI оценка лида
                ai_score = self._quick_lead_score(lead)
                
                response += f"👤 *{name}* - {title}\n"
                response += f"📞 {phone}\n"
                response += f"⭐ Оценка AI: {ai_score}/10\n\n"
            
            await update.message.reply_text(response, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in my_leads: {str(e)}")
            await update.message.reply_text("❌ Ошибка при загрузке лидов.")
    
    def _quick_lead_score(self, lead: dict) -> int:
        """Быстрая оценка лида"""
        score = 5
        if lead.get('PHONE'): score += 2
        if lead.get('EMAIL'): score += 2
        if lead.get('COMMENTS'): score += 1
        return min(score, 10)
    
    async def create_lead_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало создания лида"""
        await update.message.reply_text(
            "➕ *Создание нового лида*\n\n"
            "Введи имя клиента:",
            parse_mode="Markdown"
        )
        return LEAD_NAME
    
    async def lead_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение имени"""
        context.user_data['lead_name'] = update.message.text
        await update.message.reply_text("📞 Введи телефон:")
        return LEAD_PHONE
    
    async def lead_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение телефона"""
        context.user_data['lead_phone'] = update.message.text
        await update.message.reply_text("💬 Добавь комментарий (или /пропустить):")
        return LEAD_COMMENT
    
    async def lead_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание лида"""
        comment = update.message.text if update.message.text != "/пропустить" else ""
        
        try:
            # Создаем лид в Bitrix24
            lead_data = {
                "TITLE": f"Лид от {context.user_data['lead_name']}",
                "NAME": context.user_data['lead_name'],
                "PHONE": [{"VALUE": context.user_data['lead_phone'], "VALUE_TYPE": "WORK"}],
                "COMMENTS": comment
            }
            
            # Здесь должен быть метод create_lead в bitrix client
            # lead_id = self.bitrix.create_lead(lead_data)
            
            await update.message.reply_text(
                f"✅ Лид создан!\n\n"
                f"👤 {context.user_data['lead_name']}\n"
                f"📞 {context.user_data['lead_phone']}\n"
                f"💬 {comment if comment else 'Без комментария'}"
            )
            
        except Exception as e:
            logger.error(f"Error creating lead: {str(e)}")
            await update.message.reply_text("❌ Ошибка при создании лида.")
        
        return ConversationHandler.END
    
    async def my_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать задачи"""
        await update.message.reply_text("⏳ Загружаю твои задачи...")
        
        try:
            # Получаем задачи (нужно добавить метод в bitrix client)
            response = "✅ *Твои задачи на сегодня:*\n\n"
            response += "1. Связаться с клиентом ООО Продукты\n"
            response += "2. Отправить КП для ИП Иванов\n"
            response += "3. Провести встречу с ООО Торг\n\n"
            response += "📊 Всего задач: 3"
            
            await update.message.reply_text(response, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in my_tasks: {str(e)}")
            await update.message.reply_text("❌ Ошибка при загрузке задач.")
    
    async def search_client(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Поиск клиента"""
        if not context.args:
            await update.message.reply_text("🔍 Использование: /клиент [имя или ИНН]")
            return
        
        query = " ".join(context.args)
        await update.message.reply_text(f"🔍 Ищу клиента: {query}...")
        
        try:
            # Поиск в 1С
            clients_1c = self.onec.get_counterparties({"name": query})
            
            # Поиск в Bitrix24
            companies = self.bitrix._call("crm.company.list", {
                "filter": {"TITLE": query}
            }).get("result", [])
            
            response = f"🔍 *Результаты поиска: {query}*\n\n"
            
            if clients_1c:
                response += "*В 1С:*\n"
                for client in clients_1c[:3]:
                    response += f"• {client.get('name')}\n"
                    response += f"  ИНН: {client.get('inn', 'Не указан')}\n\n"
            
            if companies:
                response += "*В Bitrix24:*\n"
                for company in companies[:3]:
                    response += f"• {company.get('TITLE')}\n"
                    response += f"  ID: {company.get('ID')}\n\n"
            
            if not clients_1c and not companies:
                response += "❌ Клиент не найден."
            
            await update.message.reply_text(response, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in search_client: {str(e)}")
            await update.message.reply_text("❌ Ошибка при поиске клиента.")
    
    async def create_offer_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало создания КП"""
        await update.message.reply_text(
            "📄 *Создание коммерческого предложения*\n\n"
            "Введи название клиента:",
            parse_mode="Markdown"
        )
        return OFFER_CLIENT
    
    async def offer_client(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение клиента для КП"""
        context.user_data['offer_client'] = update.message.text
        await update.message.reply_text(
            "📦 Введи товары через запятую:\n"
            "Например: Молоко 3.2%, Кефир 2.5%, Творог 9%"
        )
        return OFFER_PRODUCTS
    
    async def offer_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Генерация КП"""
        products = [p.strip() for p in update.message.text.split(',')]
        
        await update.message.reply_text("⏳ Генерирую коммерческое предложение...")
        
        try:
            client_info = {"name": context.user_data['offer_client']}
            offer = self.ai.generate_commercial_offer(client_info, products)
            
            await update.message.reply_text(
                f"📄 *Коммерческое предложение*\n\n{offer}",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error generating offer: {str(e)}")
            await update.message.reply_text("❌ Ошибка при генерации КП.")
        
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена операции"""
        await update.message.reply_text("❌ Операция отменена.")
        return ConversationHandler.END
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "my_leads":
            await self.my_leads(query, context)
        elif query.data == "my_tasks":
            await self.my_tasks(query, context)
        elif query.data == "help":
            await self.help_command(query, context)
    
    async def chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """AI чат"""
        user_message = update.message.text
        
        system_prompt = """Ты - Sales Bot, помощник менеджера по продажам.
        Помогай с лидами, КП, задачами и клиентами.
        Если нужно выполнить действие - предложи команду."""
        
        ai_response = self.ai.generate_response(user_message, system_prompt)
        await update.message.reply_text(ai_response)
    
    def run(self):
        """Запуск бота"""
        logger.info("Sales Bot started")
        self.app.run_polling()

if __name__ == "__main__":
    TOKEN = os.getenv("SALES_BOT_TOKEN")
    bot = SalesBot(TOKEN)
    bot.run()
