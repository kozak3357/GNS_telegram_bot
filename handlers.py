import re
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from email_sender import send_email  # Импортируем функцию отправки email

# Состояния диалога
SPORT, NAME, EMAIL, PHONE, PLAYER_URL, ADDITIONAL_INFO = range(6)

# Словарь для хранения данных пользователя
user_data = {}

# Регулярные выражения для валидации
NAME_REGEX = r"^[a-zA-Zа-яА-ЯёЁ\s-]{2,50}$"  # Только буквы, пробелы, дефисы, 2-50 символов
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"  # Базовая email-валидация
PHONE_REGEX = r"^\+?[0-9]{7,15}$"  # Телефон должен начинаться с + и содержать только цифры (7-15 символов)

# Валидные URL-форматы
ELITEPROSPECTS_REGEX = r"^https://www\.eliteprospects\.com/player/\d+/[a-zA-Z-]+$"
TRANSFERMARKT_REGEX = r"^https://www\.transfermarkt\.[a-z]+/[^/]+/profil/[^/]+/\d+$"

async def start(update: Update, context: CallbackContext) -> int:
    """Запрос выбора спорта"""
    keyboard = [["🏒 Хоккей", "⚽ Футбол"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🏆 Выберите вид спорта:", reply_markup=reply_markup)
    return SPORT

async def choose_sport(update: Update, context: CallbackContext) -> int:
    """Обработка выбора спорта"""
    sport = update.message.text.strip().lower()

    if sport == "🏒 хоккей":
        user_data["sport"] = "hockey"
    elif sport == "⚽ футбол":
        user_data["sport"] = "football"
    else:
        await update.message.reply_text("⚠ Пожалуйста, выберите '🏒 Хоккей' или '⚽ Футбол'.")
        return SPORT

    await update.message.reply_text("Введите полное имя игрока:")
    return NAME

async def get_name(update: Update, context: CallbackContext) -> int:
    """Сохранить имя и запросить email."""
    name = update.message.text.strip()

    if not re.match(NAME_REGEX, name):
        await update.message.reply_text("⚠ Некорректное имя! Введите только буквы и пробелы (до 50 символов). Попробуйте снова:")
        return NAME

    user_data["name"] = name
    await update.message.reply_text("Введите email игрока:")
    return EMAIL

async def get_email(update: Update, context: CallbackContext) -> int:
    """Сохранить email и запросить номер телефона."""
    email = update.message.text.strip()

    if not re.match(EMAIL_REGEX, email):
        await update.message.reply_text("⚠ Некорректный email! Попробуйте снова:")
        return EMAIL

    user_data["email"] = email
    keyboard = [[KeyboardButton("📞 Поделиться номером", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Введите номер телефона игрока или нажмите кнопку ниже:", reply_markup=reply_markup)
    return PHONE

async def get_phone(update: Update, context: CallbackContext) -> int:
    """Сохранить номер телефона и запросить ссылку на профиль игрока."""
    if update.message.contact:
        user_data["phone"] = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
        if not re.match(PHONE_REGEX, phone):
            keyboard = [[KeyboardButton("📞 Поделиться номером", request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("⚠ Некорректный номер! Введите снова или нажмите кнопку ниже:", reply_markup=reply_markup)
            return PHONE
        user_data["phone"] = phone

    await update.message.reply_text("Введите ссылку на профиль игрока:")
    return PLAYER_URL

async def get_player_url(update: Update, context: CallbackContext) -> int:
    """Сохранить ссылку на профиль игрока с учетом спорта."""
    url = update.message.text.strip()

    if user_data["sport"] == "hockey":
        if not re.match(ELITEPROSPECTS_REGEX, url):
            await update.message.reply_text("⚠ Некорректная ссылка! Формат для хоккея: https://www.eliteprospects.com/player/12345/name")
            return PLAYER_URL
    elif user_data["sport"] == "football":
        if not re.match(TRANSFERMARKT_REGEX, url):
            await update.message.reply_text("⚠ Некорректная ссылка! Формат для футбола: https://www.transfermarkt.xx/name/profil/spieler/12345")
            return PLAYER_URL

    user_data["player_url"] = url
    await update.message.reply_text("Добавьте дополнительную информацию (или напишите 'нет'):")
    return ADDITIONAL_INFO


async def get_additional_info(update: Update, context: CallbackContext) -> int:
    """Сохраняем данные и отправляем email"""

    # Проверяем, есть ли текст в сообщении
    additional_info = update.message.text.strip() if update.message.text else "Нет доп. информации"
    user_data["additional_info"] = additional_info

    subject = "📩 Новая заявка на игрока"
    message = f"""
    🏆 Спорт: {user_data['sport']}
    Имя: {user_data['name']}
    Email: {user_data['email']}
    Телефон: {user_data['phone']}
    Профиль: {user_data['player_url']}
    Доп. инфо: {user_data['additional_info']}
    """

    send_email(user_data["sport"], subject, message)  # Отправляем email

    await update.message.reply_text("✅ Данные успешно отправлены!")
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """Отмена сбора данных."""
    await update.message.reply_text("⛔ Сбор данных отменен.")
    return ConversationHandler.END
