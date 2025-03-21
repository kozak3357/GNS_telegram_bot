import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
HOCKEY_EMAIL = os.getenv("HOCKEY_EMAIL")
FOOTBALL_EMAIL = os.getenv("FOOTBALL_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email(sport, subject, message, cc_emails=None):
    """Отправка email в зависимости от вида спорта"""

    # Выбираем получателя
    receiver_email = HOCKEY_EMAIL if sport == "hockey" else FOOTBALL_EMAIL

    # Корректное формирование списка получателей
    recipients = [receiver_email] + (cc_emails if cc_emails else [])

    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)  # Добавляем копии

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Включаем безопасное соединение
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, recipients, msg.as_string())

        logging.info(f"📧 Email успешно отправлен на {receiver_email}")
    except Exception as e:
        logging.error(f"⚠ Ошибка при отправке email: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Пример использования — отправка заявки на игрока
    test_subject = "📩 Новая заявка на игрока"
    test_message = """
    🔹 Данные игрока:

    Имя: Тест Игрок
    Email: test@email.com
    Телефон: +1234567890
    EliteProspects: https://www.eliteprospects.com/player/12345
    Доп. информация: Перспективный игрок, 18 лет
    """
    send_email(test_subject, test_message, cc_emails=["copy@example.com"])
