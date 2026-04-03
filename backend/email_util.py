import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_ticket_email(user_email, user_name, event_title, ticket_image):

    msg = EmailMessage()

    msg["Subject"] = f"Your Ticket for {event_title}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = user_email

    msg.set_content(f"""
Hello {user_name},

Your ticket has been successfully booked.

Event: {event_title}

Please find your ticket attached below.

Show this ticket at the event entry.

Thank you!
Tiya Golf Club
""")

    # attach ticket image
    with open(ticket_image, "rb") as f:
        file_data = f.read()

    msg.add_attachment(
        file_data,
        maintype="image",
        subtype="png",
        filename="ticket.png"
    )

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)