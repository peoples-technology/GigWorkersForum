import secrets
from calendar import monthrange
from datetime import date


def calculate_allocations(
    amount_inr: int,
    is_initial_registration: bool = True,
    current_paid_up_to: date | None = None,
    registration_fee: int = 100,
    monthly_fee: int = 10,
) -> tuple[list[dict], date]:
    """
    Compute ledger allocations and new paid_up_to date (FR3.1, FR3.2, FR3.9).
    Returns (allocations_list, new_paid_up_to).
    """
    allocations: list[dict] = []
    remaining_amount = amount_inr

    # 1. Allocate registration fee if initial
    if is_initial_registration:
        if remaining_amount < registration_fee:
            raise ValueError(
                f"Initial payment must be at least the registration fee of ₹{registration_fee}"
            )
        allocations.append(
            {
                "type": "registration_fee",
                "amount": registration_fee,
                "description": "One-time Trade Union Registration Fee / പ്രവേശന ഫീസ്",
            }
        )
        remaining_amount -= registration_fee

    # 2. Allocate monthly subscriptions
    months_count = remaining_amount // monthly_fee
    if months_count == 0 and not is_initial_registration:
        raise ValueError(
            f"Payment amount must cover at least 1 month subscription (₹{monthly_fee})"
        )

    # Determine starting month
    today = date.today()
    if current_paid_up_to and current_paid_up_to >= today:
        # Start from month after current_paid_up_to
        start_year = current_paid_up_to.year
        start_month = current_paid_up_to.month + 1
        if start_month > 12:
            start_year += 1
            start_month = 1
    else:
        # Start from current month
        start_year = today.year
        start_month = today.month

    curr_y = start_year
    curr_m = start_month

    for _ in range(months_count):
        month_str = f"{curr_y}-{curr_m:02d}"
        allocations.append(
            {
                "type": "monthly_subscription",
                "amount": monthly_fee,
                "month": month_str,
                "description": f"CITU Membership Subscription for {month_str}",
            }
        )
        curr_m += 1
        if curr_m > 12:
            curr_y += 1
            curr_m = 1

    # Final paid_up_to is last day of the last paid month
    last_alloc_month = curr_m - 1
    last_alloc_year = curr_y
    if last_alloc_month == 0:
        last_alloc_month = 12
        last_alloc_year -= 1

    _, last_day = monthrange(last_alloc_year, last_alloc_month)
    new_paid_up_to = date(last_alloc_year, last_alloc_month, last_day)

    return allocations, new_paid_up_to


def generate_receipt_number(year: int | None = None) -> str:
    """Generate a numbered digital receipt string (FR3.8)."""
    yr = year or date.today().year
    rand_seq = secrets.randbelow(900000) + 100000
    return f"REC-{yr}-{rand_seq}"
