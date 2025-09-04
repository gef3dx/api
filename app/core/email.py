from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib

from app.core.config import settings


async def send_email(
    recipient: str, subject: str, body: str, html_body: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP.

    Args:
        recipient: The recipient's email address
        subject: The email subject
        body: The plain text email body
        html_body: Optional HTML email body

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = settings.EMAIL_FROM
        message["To"] = recipient
        message["Subject"] = subject

        # Add plain text part
        text_part = MIMEText(body, "plain")
        message.attach(text_part)

        # Add HTML part if provided
        if html_body:
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)

        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME or None,
            password=settings.SMTP_PASSWORD or None,
            use_tls=settings.SMTP_PORT == 465,
            start_tls=settings.SMTP_PORT == 587,
        )

        return True
    except Exception as e:
        # In production, you would log this error
        print(f"Failed to send email: {e}")
        return False


async def send_password_reset_email(recipient: str, token: str) -> bool:
    """
    Send a password reset email.

    Args:
        recipient: The recipient's email address
        token: The password reset token

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    reset_link = f"https://frontend/reset?token={token}"

    subject = "Password Reset Request"
    body = f"""
    You have requested to reset your password.

    Please click the link below to reset your password:
    {reset_link}

    This link will expire in 1 hour.

    If you did not request this, please ignore this email.
    """

    html_body = f"""
    <html>
      <body>
        <p>You have requested to reset your password.</p>
        <p>Please click the link below to reset your password:</p>
        <p><a href="{reset_link}">Reset Password</a></p>
        <p>This link will expire in 1 hour.</p>
        <p>If you did not request this, please ignore this email.</p>
      </body>
    </html>
    """

    return await send_email(recipient, subject, body, html_body)
