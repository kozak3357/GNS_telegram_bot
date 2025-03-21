import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")  # Основной получатель


def send_email(subject, message, cc_emails=None):
    """Отправка email через SMTP"""

    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)  # Добавляем копии
        recipients = [RECEIVER_EMAIL] + cc_emails
    else:
        recipients = [RECEIVER_EMAIL]

    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Включаем безопасное соединение
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, recipients, msg.as_string())

        logging.info("📧 Email успешно отправлен")
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
