import razorpay
import os

RAZORPAY_KEY = os.getenv("RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")

client = razorpay.Client(
    auth=(RAZORPAY_KEY, RAZORPAY_SECRET)
)


def create_razorpay_order(amount):

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return order
