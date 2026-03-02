"""
Bot Manager - Управление всеми ботами
Запуск: python bots/bot_manager.py
"""

import os
import sys
import logging
from multiprocessing import Process
from analytics_bot import AnalyticsBot
from sales_bot import SalesBot
from support_bot import SupportBot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_analytics_bot():
    """Запуск Analytics Bot"""
    token = os.getenv("ANALYTICS_BOT_TOKEN")
    if not token:
        logger.error("ANALYTICS_BOT_TOKEN not found in environment")
        return
    
    logger.info("Starting Analytics Bot...")
    bot = AnalyticsBot(token)
    bot.run()

def run_sales_bot():
    """Запуск Sales Bot"""
    token = os.getenv("SALES_BOT_TOKEN")
    if not token:
        logger.error("SALES_BOT_TOKEN not found in environment")
        return
    
    logger.info("Starting Sales Bot...")
    bot = SalesBot(token)
    bot.run()

def run_support_bot():
    """Запуск Support Bot"""
    token = os.getenv("SUPPORT_BOT_TOKEN")
    if not token:
        logger.error("SUPPORT_BOT_TOKEN not found in environment")
        return
    
    logger.info("Starting Support Bot...")
    bot = SupportBot(token)
    bot.run()

def main():
    """Запуск всех ботов"""
    logger.info("Starting Bot Manager...")
    
    # Проверка токенов
    required_tokens = [
        "ANALYTICS_BOT_TOKEN",
        "SALES_BOT_TOKEN",
        "SUPPORT_BOT_TOKEN"
    ]
    
    missing_tokens = [t for t in required_tokens if not os.getenv(t)]
    if missing_tokens:
        logger.error(f"Missing tokens: {', '.join(missing_tokens)}")
        logger.error("Add tokens to .env file")
        sys.exit(1)
    
    # Запуск ботов в отдельных процессах
    processes = []
    
    analytics_process = Process(target=run_analytics_bot)
    sales_process = Process(target=run_sales_bot)
    support_process = Process(target=run_support_bot)
    
    processes.extend([analytics_process, sales_process, support_process])
    
    try:
        for process in processes:
            process.start()
            logger.info(f"Started process: {process.name}")
        
        # Ожидание завершения
        for process in processes:
            process.join()
            
    except KeyboardInterrupt:
        logger.info("Stopping all bots...")
        for process in processes:
            process.terminate()
            process.join()
        logger.info("All bots stopped")

if __name__ == "__main__":
    main()
