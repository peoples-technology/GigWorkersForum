import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_403_FORBIDDEN
from litestar.testing import AsyncTestClient

from app.core.import_processor import mask_aadhaar_input, normalize_phone
from app.main import app


def test_phone_normalisation_and_dpdp_masking():
    """Verify E.164 phone normalisation and DPDP last-4 masking."""
    assert normalize_phone("9847123456") == "+919847123456"
    assert normalize_phone("+91 9847-123456") == "+919847123456"
    assert normalize_phone("12345") is None

    # DPDP Act: 12-digit Aadhaar input must be reduced to last 4 only
    assert mask_aadhaar_input("9988 7766 5544") == "5544"
    assert mask_aadhaar_input("123456781234") == "1234"
    assert mask_aadhaar_input("8765") == "8765"


@pytest.mark.asyncio
async def test_import_template_download():
    """FR10.2: Downloadable CSV template generated with bilingual headers."""
    headers_state = {
        "X-Admin-Role": "state_admin",
        "X-Admin-Unit": "KLSTATE",
        "X-Admin-Id": "state_gs",
    }

    async with AsyncTestClient(app=app) as client:
        resp = await client.get("/api/admin/import/template", headers=headers_state)
        assert resp.status_code == HTTP_200_OK
        assert resp.headers["content-type"] == "text/csv; charset=utf-8"
        content = resp.content.decode("utf-8")
        assert "Full Name (പൂർണ്ണ നാമം)" in content
        assert "Phone (ഫോൺ നമ്പർ)" in content
        assert "Paid Up To (അടച്ച കാലാവധി YYYY-MM)" in content


@pytest.mark.asyncio
async def test_bulk_import_processing_and_scoping():
    """
    FR10.1, FR10.3, FR10.4, FR10.5, FR10.6, FR10.7, FR10.9:
    - Kozhikode district admin submits batch
    - Valid row for KLKKD is accepted and assigned number
    - Row for KLEKM is rejected due to district scope violation
    - Duplicate phone is skipped
    - Under-18 worker is rejected
    """
    headers_kkd = {
        "X-Admin-Role": "district_admin",
        "X-Admin-Unit": "KLKKD",
        "X-Admin-Id": "admin_kkd_01",
    }

    test_rows = [
        # 1. Valid row with paid_up_to -> should be accepted as active
        {
            "name": "Com. Shaji Kozhikode",
            "phone": "9847055501",
            "district_code": "KLKKD",
            "platform": "Swiggy",
            "sector": "food_delivery",
            "dob": "1992-05-10",
            "id_number": "9988 7766 1234",
            "paid_up_to": "2027-04",
            "paper_receipt_no": "KKD-2026-001",
        },
        # 2. Duplicate phone (already registered in system) -> should be skipped
        {
            "name": "Com. Existing Worker",
            "phone": "9847000001",  # Existing phone in seed
            "district_code": "KLKKD",
            "platform": "Zomato",
            "sector": "food_delivery",
            "dob": "1990-01-01",
            "id_number": "4321",
        },
        # 3. Out-of-district row for a district admin -> should be rejected (FR10.9)
        {
            "name": "Com. Ernakulam Worker In KKD Batch",
            "phone": "9847055503",
            "district_code": "KLEKM",  # Outside KLKKD
            "platform": "Uber",
            "sector": "taxi_cab",
            "dob": "1988-08-20",
            "id_number": "5678",
        },
        # 4. Underage worker (< 18 years) -> should be rejected
        {
            "name": "Young Worker",
            "phone": "9847055504",
            "district_code": "KLKKD",
            "platform": "Swiggy",
            "sector": "food_delivery",
            "dob": "2015-01-01",  # 11 years old
            "id_number": "9999",
        },
    ]

    async with AsyncTestClient(app=app) as client:
        # Submit batch
        submit_res = await client.post(
            "/api/admin/import",
            json={"filename": "kozhikode_pilot_paper_records.csv", "rows": test_rows},
            headers=headers_kkd,
        )
        assert submit_res.status_code == HTTP_200_OK
        data = submit_res.json()
        assert data["success"] is True
        job_id = data["job_id"]
        assert data["total_rows"] == 4
        assert data["accepted_rows"] == 1
        assert data["skipped_rows"] == 1
        assert data["rejected_rows"] == 2

        # Check job status endpoint (FR10.12)
        status_res = await client.get(f"/api/admin/import/{job_id}", headers=headers_kkd)
        assert status_res.status_code == HTTP_200_OK
        job_status = status_res.json()["job"]
        assert job_status["accepted_rows"] == 1

        # Check report download endpoint (FR10.10)
        report_res = await client.get(f"/api/admin/import/{job_id}/report", headers=headers_kkd)
        assert report_res.status_code == HTTP_200_OK
        assert report_res.headers["content-type"] == "text/csv; charset=utf-8"
        report_csv = report_res.content.decode("utf-8")
        assert "Row Number,Phone,Status" in report_csv
        assert "accepted" in report_csv
        assert "duplicate_phone" in report_csv
        assert "outside admin scope" in report_csv


@pytest.mark.asyncio
async def test_district_admin_cannot_access_other_district_import():
    """FR10.9: District admin cannot view or download import jobs belonging to another district."""
    headers_kkd = {
        "X-Admin-Role": "district_admin",
        "X-Admin-Unit": "KLKKD",
        "X-Admin-Id": "admin_kkd_01",
    }
    headers_ekm = {
        "X-Admin-Role": "district_admin",
        "X-Admin-Unit": "KLEKM",
        "X-Admin-Id": "admin_ekm_01",
    }

    async with AsyncTestClient(app=app) as client:
        # 1. KKD creates a job
        create_res = await client.post(
            "/api/admin/import",
            json={"filename": "kkd_batch.csv", "rows": []},
            headers=headers_kkd,
        )
        job_id = create_res.json()["job_id"]

        # 2. EKM admin tries to access KKD job -> 403 Forbidden
        bad_access = await client.get(f"/api/admin/import/{job_id}", headers=headers_ekm)
        assert bad_access.status_code == HTTP_403_FORBIDDEN
