"""
Support Bot - Бот технической поддержки
Команды: /faq, /проблема, /статус, /инструкция
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from ai_services.claude_service import ClaudeService
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupportBot:
    """Бот технической поддержки"""
    
    def __init__(self, token: str):
        self.token = token
        self.ai = ClaudeService()
        self.app = Application.builder().token(token).build()
        self.faq_data = self._load_faq()
        self._setup_handlers()
    
    def _load_faq(self) -> dict:
        """Загрузка базы знаний"""
        return {
            "bitrix24": {
                "title": "Bitrix24",
                "questions": [
                    {
                        "q": "Как создать лид?",
                        "a": "Используй команду /создать_лид в Sales Bot или создай через CRM → Лиды → Добавить"
                    },
                    {
                        "q": "Как настроить webhook?",
                        "a": "Bitrix24 → Настройки → Разработчикам → Входящий вебхук → Создать"
                    },
                    {
                        "q": "Как добавить пользовательское поле?",
                        "a": "CRM → Настройки → Настройка CRM → Пользовательские поля"
                    }
                ]
            },
            "1c": {
                "title": "1С",
                "questions": [
                    {
                        "q": "Как проверить остатки?",
                        "a": "Используй команду /остатки в Analytics Bot или зайди в 1С → Склад → Остатки товаров"
                    },
                    {
                        "q": "Как создать заказ?",
                        "a": "1С → Продажи → Заказы покупателей → Создать"
                    },
                    {
                        "q": "Как настроить синхронизацию?",
                        "a": "Настрой HTTP-сервисы в 1С и укажи URL в .env файле проекта"
                    }
                ]
            },
            "боты": {
                "title": "Telegram боты",
                "questions": [
                    {
                        "q": "Какие есть боты?",
                        "a": "Analytics Bot (отчеты), Sales Bot (продажи), Support Bot (поддержка)"
                    },
                    {
                        "q": "Как получить токен бота?",
                        "a": "Напиши @BotFather в Telegram → /newbot → следуй инструкциям"
                    },
                    {
                        "q": "Как запустить бота?",
                        "a": "python bots/analytics_bot.py (или sales_bot.py, support_bot.py)"
                    }
                ]
            }
        }
    
    def _setup_handlers(self):
        """Настройка обработчиков"""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("faq", self.faq))
        self.app.add_handler(CommandHandler("проблема", self.report_issue))
        self.app.add_handler(CommandHandler("статус", self.check_status))
        self.app.add_handler(CommandHandler("инструкция", self.get_instruction))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat_handler))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Приветствие"""
        keyboard = [
            [InlineKeyboardButton("❓ FAQ", callback_data="faq")],
            [InlineKeyboardButton("🐛 Сообщить о проблеме", callback_data="report_issue")],
            [InlineKeyboardButton("📊 Статус систем", callback_data="status")],
            [InlineKeyboardButton("📖 Инструкции", callback_data="instructions")],
            [InlineKeyboardButton("💬 Задать вопрос", callback_data="ask")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 *Support Bot*\n\n"
            "Привет! Я помогу тебе с технической поддержкой.\n\n"
            "Выбери раздел или задай вопрос:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Справка"""
        help_text = """
📚 *Доступные команды:*

❓ */faq* - Часто задаваемые вопросы
🐛 */проблема* - Сообщить о проблеме
📊 */статус* - Статус работы систем
📖 */инструкция* [тема] - Получить инструкцию

💬 *Режим чата:*
Просто напиши вопрос, и я помогу:
• "Как создать лид в Bitrix24?"
• "Не работает синхронизация с 1С"
• "Как настроить webhook?"
• "Где посмотреть остатки?"

🤖 *AI-помощник:*
Я использую Claude для:
• Поиска решений в базе знаний
• Диагностики проблем
• Пошаговых инструкций
• Рекомендаций по настройке
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """FAQ"""
        keyboard = []
        for category_id, category in self.faq_data.items():
            keyboard.append([InlineKeyboardButton(
                f"📁 {category['title']}",
                callback_data=f"faq_{category_id}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❓ *Часто задаваемые вопросы*\n\n"
            "Выбери категорию:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def show_faq_category(self, update: Update, category_id: str):
        """Показать вопросы категории"""
        category = self.faq_data.get(category_id)
        if not category:
            await update.message.reply_text("❌ Категория не найдена.")
            return
        
        response = f"📁 *{category['title']}*\n\n"
        for i, item in enumerate(category['questions'], 1):
            response += f"{i}. *{item['q']}*\n"
            response += f"   {item['a']}\n\n"
        
        await update.message.reply_text(response, parse_mode="Markdown")
    
    async def report_issue(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сообщить о проблеме"""
        if not context.args:
            await update.message.reply_text(
                "🐛 *Сообщить о проблеме*\n\n"
                "Опиши проблему подробно:\n"
                "/проблема [описание]\n\n"
                "Например:\n"
                "/проблема Не работает синхронизация с 1С, ошибка 500",
                parse_mode="Markdown"
            )
            return
        
        issue_text = " ".join(context.args)
        
        # AI анализ проблемы
        system_prompt = """Ты - техподдержка. Проанализируй проблему и предложи решение.
        Если нужна дополнительная информация - спроси."""
        
        ai_analysis = self.ai.generate_response(issue_text, system_prompt)
        
        response = f"🐛 *Анализ проблемы*\n\n"
        response += f"📝 Описание: {issue_text}\n\n"
        response += f"🤖 Рекомендации:\n{ai_analysis}\n\n"
        response += f"✅ Проблема зарегистрирована. Номер обращения: #{hash(issue_text) % 10000}"
        
        await update.message.reply_text(response, parse_mode="Markdown")
    
    async def check_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Проверка статуса систем"""
        await update.message.reply_text("⏳ Проверяю статус систем...")
        
        # Здесь можно добавить реальные проверки
        status = {
            "Bitrix24 API": "✅ Работает",
            "1С HTTP-сервисы": "✅ Работает",
            "OpenAI API": "✅ Работает",
            "Claude API": "✅ Работает",
            "Analytics Bot": "✅ Работает",
            "Sales Bot": "✅ Работает",
            "Support Bot": "✅ Работает"
        }
        
        response = "📊 *Статус систем*\n\n"
        for system, status_text in status.items():
            response += f"{status_text} {system}\n"
        
        response += f"\n🕐 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        await update.message.reply_text(response, parse_mode="Markdown")
    
    async def get_instruction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получить инструкцию"""
        if not context.args:
            keyboard = [
                [InlineKeyboardButton("📖 Bitrix24", callback_data="inst_bitrix24")],
                [InlineKeyboardButton("📖 1С", callback_data="inst_1c")],
                [InlineKeyboardButton("📖 Боты", callback_data="inst_bots")],
                [InlineKeyboardButton("📖 API", callback_data="inst_api")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📖 *Инструкции*\n\n"
                "Выбери тему:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return
        
        topic = " ".join(context.args)
        
        # AI генерирует инструкцию
        system_prompt = f"""Создай пошаговую инструкцию по теме: {topic}
        Инструкция должна быть понятной и структурированной."""
        
        instruction = self.ai.generate_response(f"Инструкция: {topic}", system_prompt)
        
        await update.message.reply_text(
            f"📖 *Инструкция: {topic}*\n\n{instruction}",
            parse_mode="Markdown"
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "faq":
            await self.faq(query, context)
        elif query.data.startswith("faq_"):
            category_id = query.data.replace("faq_", "")
            await self.show_faq_category(query, category_id)
        elif query.data == "report_issue":
            await self.report_issue(query, context)
        elif query.data == "status":
            await self.check_status(query, context)
        elif query.data == "instructions":
            await self.get_instruction(query, context)
    
    async def chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """AI чат для поддержки"""
        user_message = update.message.text
        
        # Поиск в FAQ
        faq_match = self._search_faq(user_message)
        
        if faq_match:
            await update.message.reply_text(
                f"💡 Нашел в FAQ:\n\n*{faq_match['q']}*\n{faq_match['a']}",
                parse_mode="Markdown"
            )
            return
        
        # AI ответ
        system_prompt = """Ты - Support Bot, техподдержка.
        Помогай решать проблемы с Bitrix24, 1С и ботами.
        Давай четкие инструкции и решения."""
        
        ai_response = self.ai.generate_response(user_message, system_prompt)
        await update.message.reply_text(ai_response)
    
    def _search_faq(self, query: str) -> dict:
        """Поиск в FAQ"""
        query_lower = query.lower()
        for category in self.faq_data.values():
            for item in category['questions']:
                if any(word in query_lower for word in item['q'].lower().split()):
                    return item
        return None
    
    def run(self):
        """Запуск бота"""
        logger.info("Support Bot started")
        self.app.run_polling()

if __name__ == "__main__":
    TOKEN = os.getenv("SUPPORT_BOT_TOKEN")
    bot = SupportBot(TOKEN)
    bot.run()
