import logging
import smtplib
from email.message import EmailMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_password_reset_email(to_email: str, reset_url: str) -> bool:
        subject = "Восстановление пароля в Family Finance"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f7f5fb; padding: 20px;">
                <div style="max-width: 500px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 16px; border: 1px solid #e9d5ff;">
                    <h2 style="color: #6b21a8; margin-top: 0;">Сброс пароля</h2>
                    <p style="color: #374151; font-size: 14px;">Здравствуйте! Вы запросили восстановление доступа к семейному бюджету.</p>
                    <p style="color: #374151; font-size: 14px;">Для установки нового пароля перейдите по кнопке ниже:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" style="background-color: #8b5cf6; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block;">
                            Установить новый пароль
                        </a>
                    </div>
                    <p style="color: #6b7280; font-size: 12px;">Ссылка действительна в течение 1 часа. Если вы не запрашивали сброс, просто проигнорируйте это письмо.</p>
                </div>
            </body>
        </html>
        """

        if not settings.SMTP_HOST:
            logger.info("=================================================================")
            logger.info(f"[EMAIL SERVICE - DEV MODE] Ссылка для сброса пароля ({to_email}):")
            logger.info(f"{reset_url}")
            logger.info("=================================================================")
            return True

        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = to_email
            msg.set_content(f"Для сброса пароля перейдите по ссылке: {reset_url}")
            msg.add_alternative(html_content, subtype="html")

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as exc:
            logger.error(f"Ошибка отправки email: {exc}")
            return False