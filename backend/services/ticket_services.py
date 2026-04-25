import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class TicketService:

    def __init__(self):
        self.ticket_folder = Path("static/tickets")
        self.template_path = "static/ticket_template.png"

    def generate_ticket(self, ticket_id, event_title, date, location):

        self.ticket_folder.mkdir(parents=True, exist_ok=True)

        template = Image.open(self.template_path)
        draw = ImageDraw.Draw(template)

        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()

        draw.text((420, 365), event_title, fill="black", font=font)
        draw.text((420, 430), str(date), fill="black", font=font)
        draw.text((420, 495), location, fill="black", font=font)
        draw.text((420, 563), str(ticket_id), fill="black", font=font)

        qr_data = f"http://127.0.0.1:8000/verify-ticket/{ticket_id}"

        qr = qrcode.make(qr_data)
        qr = qr.resize((200, 200))

        template.paste(qr, (1150, 350))

        ticket_path = self.ticket_folder / f"ticket_{ticket_id}.png"
        template.save(ticket_path)

        return str(ticket_path)