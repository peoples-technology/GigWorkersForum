import hashlib
import hmac
import secrets

from app.core.payment.base import PaymentProvider


class RazorpayAdapter(PaymentProvider):
    def __init__(self, key_id: str = "rzp_test_key", key_secret: str = "rzp_test_secret"):
        self.key_id = key_id
        self.key_secret = key_secret

    def create_order(
        self,
        amount_inr: int,
        receipt: str,
        notes: dict | None = None,
    ) -> dict:
        """Create a Razorpay order structure."""
        order_id = f"order_{secrets.token_hex(10)}"
        return {
            "id": order_id,
            "provider": "razorpay",
            "amount": amount_inr * 100,  # in paise
            "currency": "INR",
            "receipt": receipt,
            "notes": notes or {},
            "status": "created",
        }

    def verify_webhook_signature(
        self,
        payload_bytes: bytes,
        signature: str,
        secret: str,
    ) -> bool:
        """Verify Razorpay HMAC-SHA256 signature."""
        computed_mac = hmac.new(
            secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(computed_mac, signature)

    def fetch_payment_status(self, provider_payment_id: str) -> dict:
        return {
            "id": provider_payment_id,
            "status": "captured",
            "provider": "razorpay",
        }
