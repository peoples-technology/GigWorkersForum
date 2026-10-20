import re
from datetime import date, datetime


def calculate_age(dob: date | str) -> int:
    """Calculate age in complete years from date of birth."""
    if isinstance(dob, str):
        dob = datetime.strptime(dob, "%Y-%m-%d").date()

    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age


def validate_answers_against_form_version(
    answers: dict,
    form_fields: list[dict],
) -> tuple[bool, list[str]]:
    """
    Validate submission answers against a form version's field specifications.
    Returns (is_valid, list_of_error_messages).
    """
    errors: list[str] = []

    for field in form_fields:
        key = field["key"]
        is_required = field.get("required", False)
        is_archived = field.get("is_archived", False)
        val = answers.get(key)

        # Skip validation for archived fields if not supplied
        if is_archived and val is None:
            continue

        # 1. Required check
        if is_required and (val is None or val == "" or val == []):
            label_en = field.get("labels", {}).get("en", key)
            errors.append(f"Field '{label_en}' is required / ഈ ഫീൽഡ് നിർബന്ധമാണ്.")
            continue

        if val is None or val == "":
            continue

        # 2. Age block check (< 18) per FR2.7
        if key == "dob":
            try:
                age = calculate_age(val)
                min_age = field.get("validation", {}).get("min_age", 18)
                if age < min_age:
                    errors.append(
                        f"Applicant must be at least {min_age} years old to join the union (Current age: {age}) / "
                        f"യൂണിയനിൽ ചേരാൻ കുറഞ്ഞത് {min_age} വയസ്സ് പൂർത്തിയായിരിക്കണം."
                    )
            except Exception:
                errors.append("Invalid date of birth format. Must be YYYY-MM-DD.")

        # 3. DPDP Masked Aadhaar check per FR2.2 & FR10.7
        if key == "id_last4":
            clean_digits = re.sub(r"\D", "", str(val))
            if len(str(val)) == 12:
                errors.append(
                    "Do not enter full 12-digit Aadhaar. For DPDP privacy, only enter the last 4 digits / "
                    "പൂർണ്ണ ആധാർ നമ്പർ നൽകരുത്. അവസാന 4 അക്കങ്ങൾ മാത്രം നൽകുക."
                )
            elif len(clean_digits) != 4:
                errors.append("ID proof must contain exactly 4 digits.")

        # 4. Mobile number format
        if field.get("type") == "phone":
            clean_phone = re.sub(r"[\s\-\+]", "", str(val))
            if clean_phone.startswith("91") and len(clean_phone) == 12:
                clean_phone = clean_phone[2:]
            if len(clean_phone) != 10 or not clean_phone.isdigit():
                errors.append(f"Invalid phone number format for '{key}'. Must be 10 digits.")

        # 5. Select options check
        options = field.get("options")
        if options and field.get("type") == "select" and val not in options:
            errors.append(f"Invalid selection '{val}' for field '{key}'.")

    # 6. Primary platform check per FR2.6
    primary_p = answers.get("primary_platform")
    platforms = answers.get("platforms", [])
    if primary_p and platforms and primary_p not in platforms:
        errors.append("Primary platform must be one of the selected platforms worked on.")

    return len(errors) == 0, errors
