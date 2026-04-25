import smtplib
from email.message import EmailMessage
from backend.core.config import settings


class EmailService:

    def send_ticket_email(self, user_email, user_name, event_title, ticket_image):

        msg = EmailMessage()
        msg["Subject"] = f"Your Ticket for {event_title}"
        msg["From"] = settings.EMAIL_USER
        msg["To"] = user_email

        msg.set_content(f"""
Hello {user_name},

Your ticket has been successfully booked.

Event: {event_title}

Please find your ticket attached.

Thank you!
Tiya Golf Club
""")

        with open(ticket_image, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="image",
                subtype="png",
                filename="ticket.png"
            )

        try:
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
                smtp.send_message(msg)

        except Exception as e:
            print("Email failed:", e)