import io

import pytest
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient
from PIL import Image

from app.core.form_validator import calculate_age, validate_answers_against_form_version
from app.core.image_processor import process_selfie
from app.core.storage import read_encrypted_document, save_encrypted_document
from app.db.seeds import CONFIRMED_15_FIELDS
from app.main import app


def test_age_calculation():
    """FR2.7: Age calculation from DOB."""
    assert calculate_age("2000-01-01") >= 24
    assert calculate_age("2015-05-01") < 18


def test_form_validation_under_18_blocked():
    """FR2.7: Block registration for anyone under 18."""
    bad_answers = {
        "full_name": "Minor Worker",
        "current_address": "Test Street, Kochi",
        "working_district": "KLEKM",
        "mobile_number": "9847011111",
        "whatsapp_number": "9847011111",
        "dob": "2015-01-01",  # ~11 years old
        "gender": "male",
        "mother_tongue": "Malayalam",
        "platforms": ["swiggy"],
        "primary_platform": "swiggy",
        "vehicle_type": "motorcycle",
        "id_doc_type": "aadhaar",
        "id_last4": "1234",
    }
    is_valid, errors = validate_answers_against_form_version(bad_answers, CONFIRMED_15_FIELDS)
    assert is_valid is False
    assert any("at least 18 years old" in e for e in errors)


def test_form_validation_full_aadhaar_rejected():
    """FR2.2: Reject full 12-digit Aadhaar input for DPDP compliance."""
    full_aadhaar_answers = {
        "full_name": "Com. Rahul",
        "current_address": "Kochi",
        "working_district": "KLEKM",
        "mobile_number": "9847011111",
        "whatsapp_number": "9847011111",
        "dob": "1998-05-14",
        "gender": "male",
        "mother_tongue": "Malayalam",
        "platforms": ["swiggy"],
        "primary_platform": "swiggy",
        "vehicle_type": "motorcycle",
        "id_doc_type": "aadhaar",
        "id_last4": "123456789012",  # 12 digits!
    }
    is_valid, errors = validate_answers_against_form_version(
        full_aadhaar_answers, CONFIRMED_15_FIELDS
    )
    assert is_valid is False
    assert any("Do not enter full 12-digit Aadhaar" in e for e in errors)


def test_form_validation_primary_platform_mismatch():
    """FR2.6: Primary platform must be part of chosen platforms."""
    mismatched = {
        "full_name": "Com. Rahul",
        "current_address": "Kochi",
        "working_district": "KLEKM",
        "mobile_number": "9847011111",
        "whatsapp_number": "9847011111",
        "dob": "1998-05-14",
        "gender": "male",
        "mother_tongue": "Malayalam",
        "platforms": ["swiggy"],
        "primary_platform": "uber",  # Not in platforms!
        "vehicle_type": "motorcycle",
        "id_doc_type": "aadhaar",
        "id_last4": "4821",
    }
    is_valid, errors = validate_answers_against_form_version(mismatched, CONFIRMED_15_FIELDS)
    assert is_valid is False
    assert any("Primary platform must be one of the selected platforms" in e for e in errors)


def test_image_processor_strips_exif():
    """FR1.5 & T2.4: Selfie processor removes EXIF metadata and resizes."""
    # Create test image with dummy EXIF
    raw_img = Image.new("RGB", (1200, 1000), color="red")
    buf = io.BytesIO()
    raw_img.save(buf, format="JPEG")
    raw_bytes = buf.getvalue()

    processed_bytes = process_selfie(raw_bytes, max_dim=800)
    assert len(processed_bytes) > 0

    processed_img = Image.open(io.BytesIO(processed_bytes))
    assert processed_img.width <= 800
    assert processed_img.height <= 800
    # Verify no EXIF tag present
    assert processed_img.getexif() == {}


def test_aes_gcm_document_encryption():
    """FR2.3 & T2.5: Encrypt and decrypt masked identity documents with AES-256-GCM."""
    secret_doc = b"CONFIDENTIAL_ID_PROOF_MEMBER_4821"
    enc_path = save_encrypted_document(secret_doc, filename_prefix="test_proof")

    assert enc_path.endswith(".enc")

    # Read and decrypt
    decrypted = read_encrypted_document(enc_path)
    assert decrypted == secret_doc


@pytest.mark.asyncio
async def test_autosave_and_resume_flow():
    """FR1.4: Autosave answers on blur and resume."""
    phone = "+919847022222"
    sample_answers = {"full_name": "Comrade Interrupted", "primary_platform": "Swiggy"}

    async with AsyncTestClient(app=app) as client:
        # 1. Autosave draft
        save_res = await client.post(
            "/api/register/autosave",
            json={"phone": phone, "answers": sample_answers, "step": 2},
        )
        assert save_res.status_code == HTTP_200_OK

        # 2. Resume draft
        resume_res = await client.get(f"/api/register/resume?phone={phone}")
        assert resume_res.status_code == HTTP_200_OK
        data = resume_res.json()
        assert data["has_draft"] is True
        assert data["answers"]["full_name"] == "Comrade Interrupted"
        assert data["step"] == 2


@pytest.mark.asyncio
async def test_full_registration_submission():
    """FR2.1 & FR2.5: Submit full registration with valid 15 fields."""
    phone = "+919847033333"
    valid_answers = {
        "full_name": "Com. Rahul Krishnan",
        "current_address": "CITU Bhavan, High Court Road, Ernakulam",
        "permanent_address": "",
        "working_district": "KLEKM",
        "mobile_number": phone,
        "whatsapp_number": phone,
        "dob": "1998-05-14",
        "gender": "male",
        "mother_tongue": "Malayalam",
        "platforms": ["swiggy", "zomato"],
        "primary_platform": "swiggy",
        "vehicle_type": "motorcycle",
        "vehicle_reg_no": "KL-07-CC-4521",
        "id_doc_type": "aadhaar",
        "id_last4": "4821",
    }

    payload = {
        "phone": phone,
        "form_version_id": "v1.0",
        "working_district_code": "KLEKM",
        "answers": valid_answers,
        "id_doc_type": "aadhaar",
        "id_last4": "4821",
    }

    async with AsyncTestClient(app=app) as client:
        sub_res = await client.post("/api/register/submit", json=payload)
        assert sub_res.status_code == HTTP_200_OK
        sub_data = sub_res.json()
        assert sub_data["success"] is True
        assert sub_data["status"] == "pending_payment"
        assert sub_data["fee_due"] == 160
