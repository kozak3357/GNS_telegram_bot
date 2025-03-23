import re
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from email_sender import send_email  # Импортируем функцию отправки email

# Состояния диалога
SPORT, NAME, EMAIL, PHONE, PLAYER_URL, ADDITIONAL_INFO = range(6)

# Регулярные выражения для валидации
NAME_REGEX = r"^[a-zA-Zа-яА-ЯёЁ\s-]{2,50}$"  # Только буквы, пробелы, дефисы, 2-50 символов
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"  # Базовая email-валидация
PHONE_REGEX = r"^\+?[0-9]{7,15}$"  # Телефон должен начинаться с + и содержать только цифры (7-15 символов)

# Валидные URL-форматы
ELITEPROSPECTS_REGEX = r"^https://www\.eliteprospects\.com/player/\d+/[a-zA-Z-]+$"
TRANSFERMARKT_REGEX = r"^https://www\.transfermarkt\.[a-z]+/[^/]+/profil/[^/]+/\d+$"


async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [["🏒 Хоккей", "⚽ Футбол"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🏆 Выберите вид спорта:", reply_markup=reply_markup)
    return SPORT


async def choose_sport(update: Update, context: CallbackContext) -> int:
    sport = update.message.text.strip().lower()

    if sport == "🏒 хоккей":
        context.user_data["sport"] = "hockey"
    elif sport == "⚽ футбол":
        context.user_data["sport"] = "football"
    else:
        await update.message.reply_text("⚠ Пожалуйста, выберите '🏒 Хоккей' или '⚽ Футбол'.")
        return SPORT

    await update.message.reply_text("Введите полное имя игрока:")
    return NAME


async def get_name(update: Update, context: CallbackContext) -> int:
    name = update.message.text.strip()

    if not re.match(NAME_REGEX, name):
        await update.message.reply_text(
            "⚠ Некорректное имя! Введите только буквы и пробелы (до 50 символов). Попробуйте снова:")
        return NAME

    context.user_data["name"] = name
    await update.message.reply_text("Введите email игрока:")
    return EMAIL


async def get_email(update: Update, context: CallbackContext) -> int:
    email = update.message.text.strip()

    if not re.match(EMAIL_REGEX, email):
        await update.message.reply_text("⚠ Некорректный email! Попробуйте снова:")
        return EMAIL

    context.user_data["email"] = email
    keyboard = [[KeyboardButton("📞 Поделиться номером", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Введите номер телефона игрока или нажмите кнопку ниже:", reply_markup=reply_markup)
    return PHONE


async def get_phone(update: Update, context: CallbackContext) -> int:
    if update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
        if not re.match(PHONE_REGEX, phone):
            keyboard = [[KeyboardButton("📞 Поделиться номером", request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("⚠ Некорректный номер! Введите снова или нажмите кнопку ниже:",
                                            reply_markup=reply_markup)
            return PHONE
        context.user_data["phone"] = phone

    sport = context.user_data["sport"]
    if sport == "hockey":
        message = "Введите ссылку на профиль игрока в EliteProspects:"
    else:
        message = "Введите ссылку на профиль игрока в TransferMarkt:"

    await update.message.reply_text(message)
    return PLAYER_URL


async def get_player_url(update: Update, context: CallbackContext) -> int:
    url = update.message.text.strip()
    sport = context.user_data.get("sport")

    if sport == "hockey" and not re.match(ELITEPROSPECTS_REGEX, url):
        await update.message.reply_text(
            "⚠ Некорректная ссылка! Формат: https://www.eliteprospects.com/player/12345/name")
        return PLAYER_URL
    elif sport == "football" and not re.match(TRANSFERMARKT_REGEX, url):
        await update.message.reply_text(
            "⚠ Некорректная ссылка! Формат: https://www.transfermarkt.xx/name/profil/spieler/12345")
        return PLAYER_URL

    context.user_data["player_url"] = url
    await update.message.reply_text("Добавьте дополнительную информацию (или напишите 'нет'):")
    return ADDITIONAL_INFO


async def get_additional_info(update: Update, context: CallbackContext) -> int:
    context.user_data["additional_info"] = update.message.text.strip() if update.message.text else "Нет доп. информации"

    phone = context.user_data.get("phone", "Не указан")
    player_url = context.user_data.get("player_url", "Не указан")

    subject = "📩 Новая заявка на игрока"
    message = f"""
    🏆 Спорт: {context.user_data['sport']}
    👤 Имя: {context.user_data['name']}
    📧 Email: {context.user_data['email']}
    📞 Телефон: {phone}
    🔗 Профиль игрока: {player_url}
    📝 Доп. информация: {context.user_data['additional_info']}
    """

    send_email(context.user_data["sport"], subject, message)
    await update.message.reply_text("✅ Данные успешно отправлены! Мы свяжемся с Вами в течение 2-3 рабочих дней")
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("⛔ Сбор данных отменен.")
    return ConversationHandler.END
