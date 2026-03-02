"""
Analytics Bot - Бот для аналитиков
Команды: /остатки, /продажи, /топ_клиенты, /отчет
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from datetime import datetime, timedelta
from bitrix24.client import Bitrix24Client
from onec.client import OneCClient
from ai_services.openai_service import OpenAIService
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsBot:
    """Бот для аналитиков - отчеты и статистика"""
    
    def __init__(self, token: str):
        self.token = token
        self.bitrix = Bitrix24Client()
        self.onec = OneCClient()
        self.ai = OpenAIService()
        self.app = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков команд"""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("остатки", self.stock_report))
        self.app.add_handler(CommandHandler("продажи", self.sales_report))
        self.app.add_handler(CommandHandler("топ_клиенты", self.top_clients))
        self.app.add_handler(CommandHandler("отчет", self.custom_report))
        self.app.add_handler(CommandHandler("конверсия", self.conversion_report))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat_handler))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Приветствие и главное меню"""
        keyboard = [
            [InlineKeyboardButton("📊 Отчет по остаткам", callback_data="stock")],
            [InlineKeyboardButton("💰 Отчет по продажам", callback_data="sales")],
            [InlineKeyboardButton("👥 Топ клиенты", callback_data="top_clients")],
            [InlineKeyboardButton("📈 Конверсия лидов", callback_data="conversion")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 *Analytics Bot*\n\n"
            "Привет! Я помогу тебе с аналитикой и отчетами.\n\n"
            "Выбери нужный отчет или напиши вопрос в свободной форме:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Справка по командам"""
        help_text = """
📚 *Доступные команды:*

📊 */остатки* - Отчет по остаткам товаров в 1С
💰 */продажи* [период] - Отчет по продажам
   Примеры: /продажи сегодня, /продажи неделя, /продажи месяц
👥 */топ_клиенты* [N] - Топ N клиентов по выручке
   Пример: /топ_клиенты 10
📈 */конверсия* - Анализ конверсии лидов
📋 */отчет* - Создать кастомный отчет

💬 *Режим чата:*
Просто напиши вопрос, и я помогу:
• "Сколько продали за вчера?"
• "Какие товары заканчиваются?"
• "Кто наш лучший клиент?"
• "Как настроить отчет?"

🔄 Данные синхронизируются между Bitrix24 и 1С автоматически.
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
  
  async def stock_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отчет по остаткам товаров"""
        await update.message.reply_text("⏳ Формирую отчет по остаткам...")
        
        try:
            # Получаем остатки из 1С
            products = self.onec.get_products()
            
            # Фильтруем товары с низкими остатками
            low_stock = [p for p in products if p.get('quantity', 0) < 10]
            out_of_stock = [p for p in products if p.get('quantity', 0) == 0]
            
            report = f"📊 *Отчет по остаткам на {datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n"
            report += f"📦 Всего товаров: {len(products)}\n"
            report += f"⚠️ Заканчиваются (< 10 шт): {len(low_stock)}\n"
            report += f"❌ Нет в наличии: {len(out_of_stock)}\n\n"
            
            if low_stock:
                report += "*Товары с низким остатком:*\n"
                for product in low_stock[:10]:
                    report += f"• {product.get('name')}: {product.get('quantity')} шт\n"
            
            if out_of_stock:
                report += f"\n*Товары отсутствуют ({len(out_of_stock)} шт):*\n"
                for product in out_of_stock[:5]:
                    report += f"• {product.get('name')}\n"
            
            await update.message.reply_text(report, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in stock_report: {str(e)}")
            await update.message.reply_text(
                "❌ Ошибка при получении данных из 1С. Проверьте подключение."
            )
    
    async def sales_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отчет по продажам"""
        period = context.args[0] if context.args else "сегодня"
        await update.message.reply_text(f"⏳ Формирую отчет по продажам за {period}...")
        
        try:
            # Определяем период
            if period == "сегодня":
                start_date = datetime.now().replace(hour=0, minute=0, second=0)
            elif period == "вчера":
                start_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0)
            elif period == "неделя":
                start_date = datetime.now() - timedelta(days=7)
            elif period == "месяц":
                start_date = datetime.now() - timedelta(days=30)
            else:
                start_date = datetime.now().replace(hour=0, minute=0, second=0)
            
            # Получаем сделки из Bitrix24
            deals = self.bitrix.get_deals({
                ">=CLOSEDATE": start_date.strftime("%Y-%m-%d"),
                "STAGE_ID": "WON"
            })
            
            total_amount = sum(float(deal.get('OPPORTUNITY', 0)) for deal in deals)
            avg_check = total_amount / len(deals) if deals else 0
            
            report = f"💰 *Отчет по продажам за {period}*\n\n"
            report += f"📊 Закрыто сделок: {len(deals)}\n"
            report += f"💵 Общая сумма: {total_amount:,.2f} ₽\n"
            report += f"📈 Средний чек: {avg_check:,.2f} ₽\n\n"
            
            # Топ-5 сделок
            if deals:
                sorted_deals = sorted(deals, key=lambda x: float(x.get('OPPORTUNITY', 0)), reverse=True)
                report += "*Топ-5 сделок:*\n"
                for i, deal in enumerate(sorted_deals[:5], 1):
                    report += f"{i}. {deal.get('TITLE')}: {float(deal.get('OPPORTUNITY', 0)):,.2f} ₽\n"
            
            await update.message.reply_text(report, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in sales_report: {str(e)}")
            await update.message.reply_text("❌ Ошибка при получении данных о продажах.")
    
    async def top_clients(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Топ клиентов по выручке"""
        limit = int(context.args[0]) if context.args else 10
        await update.message.reply_text(f"⏳ Формирую топ-{limit} клиентов...")
        
        try:
            # Получаем все сделки
            deals = self.bitrix.get_deals({"STAGE_ID": "WON"})
            
            # Группируем по компаниям
            clients_revenue = {}
            for deal in deals:
                company_id = deal.get('COMPANY_ID')
                if company_id:
                    revenue = float(deal.get('OPPORTUNITY', 0))
                    if company_id in clients_revenue:
                        clients_revenue[company_id]['revenue'] += revenue
                        clients_revenue[company_id]['deals'] += 1
                    else:
                        clients_revenue[company_id] = {
                            'revenue': revenue,
                            'deals': 1,
                            'title': deal.get('COMPANY_TITLE', 'Без названия')
                        }
            
            # Сортируем по выручке
            sorted_clients = sorted(
                clients_revenue.items(),
                key=lambda x: x[1]['revenue'],
                reverse=True
            )[:limit]
            
            report = f"👥 *Топ-{limit} клиентов по выручке*\n\n"
            for i, (client_id, data) in enumerate(sorted_clients, 1):
                report += f"{i}. *{data['title']}*\n"
                report += f"   💰 {data['revenue']:,.2f} ₽ ({data['deals']} сделок)\n\n"
            
            await update.message.reply_text(report, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in top_clients: {str(e)}")
            await update.message.reply_text("❌ Ошибка при получении данных о клиентах.")
    
    async def conversion_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Анализ конверсии лидов"""
        await update.message.reply_text("⏳ Анализирую конверсию лидов...")
        
        try:
            # Получаем лиды и сделки
            leads = self.bitrix.get_leads()
            deals = self.bitrix.get_deals()
            won_deals = [d for d in deals if d.get('STAGE_ID') == 'WON']
            
            total_leads = len(leads)
            total_deals = len(deals)
            won_count = len(won_deals)
            
            conversion_to_deal = (total_deals / total_leads * 100) if total_leads > 0 else 0
            conversion_to_won = (won_count / total_leads * 100) if total_leads > 0 else 0
            
            report = f"📈 *Анализ конверсии*\n\n"
            report += f"📊 Всего лидов: {total_leads}\n"
            report += f"🔄 Конвертировано в сделки: {total_deals} ({conversion_to_deal:.1f}%)\n"
            report += f"✅ Закрыто успешно: {won_count} ({conversion_to_won:.1f}%)\n\n"
            
            # AI анализ
            ai_prompt = f"""Проанализируй конверсию:
            - Лидов: {total_leads}
            - Сделок: {total_deals}
            - Закрыто: {won_count}
            
            Дай краткие рекомендации по улучшению конверсии."""
            
            ai_analysis = self.ai.generate_response(ai_prompt)
            report += f"🤖 *AI Рекомендации:*\n{ai_analysis}"
            
            await update.message.reply_text(report, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error in conversion_report: {str(e)}")
            await update.message.reply_text("❌ Ошибка при анализе конверсии.")
    
    async def custom_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание кастомного отчета"""
        await update.message.reply_text(
            "📋 *Создание кастомного отчета*\n\n"
            "Опиши, какой отчет тебе нужен, например:\n"
            "• Продажи по менеджерам за месяц\n"
            "• Динамика лидов по неделям\n"
            "• Товары с максимальной наценкой\n\n"
            "Просто напиши описание следующим сообщением.",
            parse_mode="Markdown"
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "stock":
            await self.stock_report(query, context)
        elif query.data == "sales":
            await self.sales_report(query, context)
        elif query.data == "top_clients":
            await self.top_clients(query, context)
        elif query.data == "conversion":
            await self.conversion_report(query, context)
        elif query.data == "help":
            await self.help_command(query, context)
    
    async def chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка свободных сообщений через AI"""
        user_message = update.message.text
        
        # AI определяет намерение и генерирует ответ
        system_prompt = """Ты - Analytics Bot, помощник аналитика.
        У тебя есть доступ к данным Bitrix24 CRM и 1С.
        Помогай пользователю с отчетами и аналитикой.
        Если нужен конкретный отчет - предложи команду.
        Отвечай кратко и по делу."""
        
        ai_response = self.ai.generate_response(user_message, system_prompt)
        await update.message.reply_text(ai_response)
    
    def run(self):
        """Запуск бота"""
        logger.info("Analytics Bot started")
        self.app.run_polling()

if __name__ == "__main__":
    TOKEN = os.getenv("ANALYTICS_BOT_TOKEN")
    bot = AnalyticsBot(TOKEN)
    bot.run()
