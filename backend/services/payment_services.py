import razorpay
from backend.core.config import settings


class PaymentService:

    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET)
        )

    def create_order(self, amount: int):
        try:
            order = self.client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })
            return order

        except Exception as e:
            raise Exception(f"Payment creation failed: {str(e)}")

    def verify_signature(self, data):
        try:
            params_dict = {
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_signature": data["razorpay_signature"]
            }

            self.client.utility.verify_payment_signature(params_dict)

        except Exception as e:
            raise Exception(f"Payment verification failed: {str(e)}")