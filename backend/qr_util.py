import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

TICKET_FOLDER = Path("static/tickets")
TEMPLATE_PATH = "static/ticket_template.png"

def generate_ticket_qr(ticket_id, event_title, date, location):

    TICKET_FOLDER.mkdir(parents=True, exist_ok=True)

    template = Image.open(TEMPLATE_PATH)

    draw = ImageDraw.Draw(template)

    font = ImageFont.truetype("arial.ttf", 36)

    draw.text((420,365), event_title, fill="black", font=font)
    draw.text((420,430), str(date), fill="black", font=font)
    draw.text((420,495), location, fill="black", font=font)
    draw.text((420,563), str(ticket_id), fill="black", font=font)

    qr_data = f"http://127.0.0.1:8000/verify-ticket/{ticket_id}"

    qr = qrcode.make(qr_data)
    qr = qr.resize((200,200))

    template.paste(qr, (1150,350))

    ticket_path = TICKET_FOLDER / f"ticket_{ticket_id}.png"

    template.save(ticket_path)

    return f"static/tickets/ticket_{ticket_id}.png"