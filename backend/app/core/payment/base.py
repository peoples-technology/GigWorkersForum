from abc import ABC, abstractmethod


class PaymentProvider(ABC):
    @abstractmethod
    def create_order(
        self,
        amount_inr: int,
        receipt: str,
        notes: dict | None = None,
    ) -> dict:
        """Create an order with the payment gateway."""
        pass

    @abstractmethod
    def verify_webhook_signature(
        self,
        payload_bytes: bytes,
        signature: str,
        secret: str,
    ) -> bool:
        """Verify the cryptographic signature of an inbound webhook."""
        pass

    @abstractmethod
    def fetch_payment_status(
        self,
        provider_payment_id: str,
    ) -> dict:
        """Fetch status of a payment by ID."""
        pass
