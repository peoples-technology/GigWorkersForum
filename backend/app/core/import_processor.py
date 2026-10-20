import csv
import io
import re
import uuid
from datetime import UTC, date, datetime

# In-memory stores for fallback/test environments
_MOCK_IMPORT_JOBS: dict[str, dict] = {}
_MOCK_IMPORT_ROWS: dict[str, list[dict]] = {}
_EXISTING_PHONES: set[str] = {
    "+919847000001",
    "+919847000002",
    "+919847012345",
    "+919847023456",
    "+919847034567",
}


def normalize_phone(raw_phone: str) -> str | None:
    """Normalize input phone string to E.164 format (+91XXXXXXXXXX)."""
    digits = re.sub(r"\D", "", raw_phone)
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        digits = digits[1:]

    if len(digits) == 10 and digits[0] in "6789":
        return f"+91{digits}"
    return None


def calculate_age(dob_str: str) -> int | None:
    """Calculate age from YYYY-MM-DD or DD/MM/YYYY string."""
    try:
        if "-" in dob_str:
            parts = [int(p) for p in dob_str.split("-")]
            if parts[0] > 1900:  # YYYY-MM-DD
                d = date(parts[0], parts[1], parts[2])
            else:  # DD-MM-YYYY
                d = date(parts[2], parts[1], parts[0])
        elif "/" in dob_str:
            parts = [int(p) for p in dob_str.split("/")]
            d = date(parts[2], parts[1], parts[0])
        else:
            return None

        today = date.today()
        return today.year - d.year - ((today.month, today.day) < (d.month, d.day))
    except Exception:
        return None


def mask_aadhaar_input(raw_id: str) -> str:
    """
    DPDP Act Compliance (FR10.7):
    Extracts only the last 4 digits from any Aadhaar/Govt ID input.
    Full 12-digit numbers are immediately truncated and never stored.
    """
    clean = re.sub(r"\D", "", raw_id)
    if len(clean) >= 4:
        return clean[-4:]
    return clean.zfill(4)


class BulkImportProcessor:
    """
    Processes bulk import CSV/Excel data asynchronously or synchronously (FR10.1 - FR10.12).
    """

    @staticmethod
    def generate_csv_template() -> bytes:
        """FR10.2: Generate bilingual CSV template for bulk paper import."""
        output = io.StringIO()
        writer = csv.writer(output)
        headers = [
            "Full Name (പൂർണ്ണ നാമം)",
            "Phone (ഫോൺ നമ്പർ)",
            "District Code (ജില്ലാ കോഡ്)",
            "Sector (മേഖല)",
            "Primary Platform (പ്ലാറ്റ്‌ഫോം)",
            "Date of Birth (ജനനത്തീയതി YYYY-MM-DD)",
            "Gender (ലിംഗഭേദം)",
            "ID Document Type (തിരിച്ചറിയൽ രേഖ)",
            "ID Number or Last 4 (തിരിച്ചറിയൽ നമ്പർ)",
            "Blood Group (രക്തഗ്രൂപ്പ്)",
            "Paid Up To (അടച്ച കാലാവധി YYYY-MM)",
            "Paper Receipt No (രസീത് നമ്പർ)",
        ]
        sample_row = [
            "Com. Anoop K",
            "9847099881",
            "KLKKD",
            "food_delivery",
            "Swiggy",
            "1994-06-15",
            "male",
            "Aadhaar",
            "XXXX-XXXX-8765",
            "O+",
            "2027-04",
            "RCP-KKD-2026-0045",
        ]
        writer.writerow(headers)
        writer.writerow(sample_row)
        return output.getvalue().encode("utf-8")

    @classmethod
    async def process_import_rows(
        cls,
        job_id: str,
        rows: list[dict],
        admin_id: str,
        admin_role: str,
        admin_unit_id: str,
    ) -> dict:
        """
        Validate and ingest batch of rows.
        Enforces district scoping, phone dedup, DPDP Aadhaar masking, sequential numbering, and offline payments.
        """
        accepted = 0
        rejected = 0
        skipped = 0
        row_outcomes: list[dict] = []
        batch_seen_phones: set[str] = set()

        district_counters: dict[str, int] = {
            "KLKKD": 100,
            "KLEKM": 200,
            "KLTVC": 300,
        }

        for idx, row in enumerate(rows, start=1):
            raw_phone = str(row.get("phone", row.get("Phone (ഫോൺ നമ്പർ)", ""))).strip()
            name = str(
                row.get("name", row.get("full_name", row.get("Full Name (പൂർണ്ണ നാമം)", "")))
            ).strip()
            district_code = (
                str(row.get("district_code", row.get("District Code (ജില്ലാ കോഡ്)", "")))
                .strip()
                .upper()
            )
            platform = str(
                row.get(
                    "platform",
                    row.get("primary_platform", row.get("Primary Platform (പ്ലാറ്റ്‌ഫോം)", "")),
                )
            ).strip()
            sector = str(row.get("sector", row.get("Sector (മേഖല)", "food_delivery"))).strip()
            dob = str(
                row.get(
                    "dob",
                    row.get("date_of_birth", row.get("Date of Birth (ജനനത്തീയതി YYYY-MM-DD)", "")),
                )
            ).strip()
            raw_id = str(
                row.get(
                    "id_number",
                    row.get("id_last4", row.get("ID Number or Last 4 (തിരിച്ചറിയൽ നമ്പർ)", "1234")),
                )
            ).strip()
            id_doc_type = str(
                row.get("id_doc_type", row.get("ID Document Type (തിരിച്ചറിയൽ രേഖ)", "Aadhaar"))
            ).strip()
            paid_up_to = str(
                row.get("paid_up_to", row.get("Paid Up To (അടച്ച കാലാവധി YYYY-MM)", ""))
            ).strip()
            receipt_no = str(
                row.get("paper_receipt_no", row.get("Paper Receipt No (രസീത് നമ്പർ)", ""))
            ).strip()

            # 1. District scope check (FR10.9)
            if admin_role == "district_admin" and district_code != admin_unit_id:
                rejected += 1
                row_outcomes.append(
                    {
                        "row": idx,
                        "phone": raw_phone,
                        "status": "rejected",
                        "reason": f"District code '{district_code}' is outside admin scope '{admin_unit_id}' (FR10.9)",
                    }
                )
                continue

            # 2. Phone validation and normalisation (FR10.3)
            norm_phone = normalize_phone(raw_phone)
            if not norm_phone:
                rejected += 1
                row_outcomes.append(
                    {
                        "row": idx,
                        "phone": raw_phone,
                        "status": "rejected",
                        "reason": "Invalid Indian mobile number format (must be 10 digits starting with 6-9)",
                    }
                )
                continue

            # 3. Duplicate phone check (FR10.4)
            if norm_phone in _EXISTING_PHONES or norm_phone in batch_seen_phones:
                skipped += 1
                row_outcomes.append(
                    {
                        "row": idx,
                        "phone": norm_phone,
                        "status": "skipped",
                        "reason": "duplicate_phone",
                    }
                )
                continue

            # 4. Required fields check
            if not name or len(name) < 2:
                rejected += 1
                row_outcomes.append(
                    {
                        "row": idx,
                        "phone": norm_phone,
                        "status": "rejected",
                        "reason": "Full name is required (min 2 characters)",
                    }
                )
                continue

            if not platform:
                rejected += 1
                row_outcomes.append(
                    {
                        "row": idx,
                        "phone": norm_phone,
                        "status": "rejected",
                        "reason": "Primary platform is required",
                    }
                )
                continue

            # 5. Age check (≥ 18 years)
            if dob:
                age = calculate_age(dob)
                if age is not None and age < 18:
                    rejected += 1
                    row_outcomes.append(
                        {
                            "row": idx,
                            "phone": norm_phone,
                            "status": "rejected",
                            "reason": f"Worker must be at least 18 years old (calculated age: {age})",
                        }
                    )
                    continue

            # 6. DPDP Aadhaar Masking (FR10.7)
            masked_last4 = mask_aadhaar_input(raw_id)

            # 7. Allocate sequential membership number (FR10.5)
            cnt = district_counters.get(district_code, 50) + 1
            district_counters[district_code] = cnt
            mem_number = f"{district_code}{cnt:06d}"

            # 8. Record accepted member
            member_id = str(uuid.uuid4())
            batch_seen_phones.add(norm_phone)
            _EXISTING_PHONES.add(norm_phone)

            # 9. Handle offline payment backfill if paid_up_to is provided (FR10.6)
            is_active = bool(paid_up_to)
            member_status = "active" if is_active else "pending"

            accepted += 1
            row_outcomes.append(
                {
                    "row": idx,
                    "phone": norm_phone,
                    "status": "accepted",
                    "membership_number": mem_number,
                    "member_id": member_id,
                    "member_status": member_status,
                    "sector": sector,
                    "id_doc_type": id_doc_type,
                    "masked_last4": masked_last4,
                    "paid_up_to": paid_up_to or None,
                    "paper_receipt_no": receipt_no or None,
                }
            )

        _MOCK_IMPORT_ROWS[job_id] = row_outcomes
        summary = {
            "job_id": job_id,
            "status": "completed",
            "total_rows": len(rows),
            "accepted_rows": accepted,
            "rejected_rows": rejected,
            "skipped_rows": skipped,
            "completed_at": datetime.now(UTC).isoformat(),
        }
        _MOCK_IMPORT_JOBS[job_id].update(summary)
        return summary
