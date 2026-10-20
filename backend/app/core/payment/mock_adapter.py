import hashlib
import hmac
import secrets

from app.core.payment.base import PaymentProvider


class MockPaymentAdapter(PaymentProvider):
    def __init__(self, secret: str = "mock_secret_key"):
        self.secret = secret

    def create_order(
        self,
        amount_inr: int,
        receipt: str,
        notes: dict | None = None,
    ) -> dict:
        return {
            "id": f"mock_order_{secrets.token_hex(8)}",
            "provider": "mock",
            "amount": amount_inr * 100,
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
        if signature == "valid_test_signature":
            return True
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
            "provider": "mock",
        }
