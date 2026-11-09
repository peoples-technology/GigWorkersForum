from datetime import datetime


def generate_receipt_summary(
    receipt_number: str,
    member_name: str,
    membership_number: str | None,
    amount_inr: int,
    payment_type: str,
    provider_payment_id: str,
    allocations: list[dict],
    paid_up_to: str,
    created_at: datetime,
) -> dict:
    """Generate structured receipt data for UI and PDF rendering."""
    return {
        "receipt_number": receipt_number,
        "union": {
            "name": "Kerala State Gig & Platform Workers Union (CITU)",
            "name_ml": "കേരള സ്റ്റേറ്റ് ഗിഗ് & പ്ലാറ്റ്ഫോം വർക്കേഴ്സ് യൂണിയൻ - സിഐടിയു",
            "registration_number": "Tu19965",
            "address": "E Balananda Smaraka Office, CITU State Committee Office, Mele Thampanoor, Thampanoor P.O., Thiruvananthapuram, Kerala",
            "phone": "9846063666, 9447695655",
        },
        "member": {
            "name": member_name,
            "membership_number": membership_number or "Pending Activation",
        },
        "payment": {
            "amount_inr": amount_inr,
            "payment_type": payment_type,
            "provider_payment_id": provider_payment_id,
            "date": created_at.strftime("%d-%m-%Y %H:%M:%S UTC"),
            "allocations": allocations,
            "paid_up_to": paid_up_to,
        },
    }
