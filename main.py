import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers import start, choose_sport, get_name, get_email, get_phone, get_player_url, get_additional_info, cancel
from handlers import SPORT, NAME, EMAIL, PHONE, PLAYER_URL, ADDITIONAL_INFO  # Состояния диалога

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Запуск бота."""
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_sport)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT & ~filters.COMMAND, get_phone)],
            PLAYER_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_player_url)],
            ADDITIONAL_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_additional_info)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()