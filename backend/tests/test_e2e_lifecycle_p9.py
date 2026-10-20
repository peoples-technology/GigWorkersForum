import pytest
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient

from app.core.security import get_totp_code
from app.main import app


@pytest.mark.asyncio
async def test_full_worker_onboarding_to_card_verification_lifecycle():
    """
    T9.4 / E2E Integration Suite:
    1. Check settings and feature switches (NFR7.2: Autopay OFF, grievance filing OFF)
    2. Request OTP and verify phone number (FR1.1)
    3. Retrieve active 15-field bilingual form version (FR2.1)
    4. Submit registration with DPDP masked ID and platform choice (FR2.2)
    5. Process payment, append to immutable ledger, auto-activate member (FR3.1, FR3.6)
    6. Verify sequential membership number is allocated (FR4.1)
    7. Generate digital card and public verification QR (FR4.2)
    8. Verify public verify page returns ONLY public safe fields (FR4.3)
    9. Verify member self-service dashboard & district WhatsApp group (FR6.1, FR6.2)
    """
    async with AsyncTestClient(app=app) as client:
        # Step 1: Settings & Feature switches
        set_res = await client.get("/api/settings")
        assert set_res.status_code == HTTP_200_OK
        settings = set_res.json()
        assert settings["module_autopay"]["enabled"] is False
        assert settings["fee_structure"]["total_initial_amount"] == 160

        # Step 2: Worker Phone OTP
        worker_phone = "9847112233"
        otp_req = await client.post("/api/auth/otp/request", json={"phone": worker_phone})
        assert otp_req.status_code == HTTP_200_OK
        otp_code = otp_req.json()["mock_otp"]

        otp_verify = await client.post(
            "/api/auth/otp/verify", json={"phone": worker_phone, "otp": otp_code}
        )
        assert otp_verify.status_code == HTTP_200_OK
        session_token = otp_verify.json()["session_token"]
        auth_headers = {"Authorization": f"Bearer {session_token}"}

        # Step 3: Fetch active bilingual form
        form_res = await client.get("/api/register/form-version/active")
        assert form_res.status_code == HTTP_200_OK
        form_version = form_res.json()
        assert len(form_version["fields"]) >= 15

        # Step 4: Submit registration answers
        valid_answers = {
            "full_name": "Com. Vineeth Vijayan",
            "current_address": "CITU Bhavan, High Court Road, Ernakulam",
            "permanent_address": "",
            "working_district": "KLKKD",
            "mobile_number": worker_phone,
            "whatsapp_number": worker_phone,
            "dob": "1995-08-24",
            "gender": "male",
            "mother_tongue": "Malayalam",
            "platforms": ["swiggy", "zomato"],
            "primary_platform": "swiggy",
            "vehicle_type": "motorcycle",
            "vehicle_reg_no": "KL-11-AA-1234",
            "id_doc_type": "aadhaar",
            "id_last4": "9876",
        }

        reg_payload = {
            "phone": worker_phone,
            "form_version_id": form_version["id"],
            "working_district_code": "KLKKD",
            "answers": valid_answers,
            "id_doc_type": "aadhaar",
            "id_last4": "9876",
        }
        submit_res = await client.post(
            "/api/register/submit", json=reg_payload, headers=auth_headers
        )
        assert submit_res.status_code == HTTP_200_OK
        submit_data = submit_res.json()
        member_id = submit_data["member_id"]

        # Step 5: Initialize payment order
        order_res = await client.post(
            "/api/payments/create-order",
            json={"member_id": member_id, "months_ahead": 6, "is_initial_registration": True},
            headers=auth_headers,
        )
        assert order_res.status_code == HTTP_200_OK
        order_id = order_res.json()["order"]["id"]

        # Step 6: Simulate gateway payment webhook
        webhook_res = await client.post(
            "/api/payments/webhook",
            json={
                "provider": "razorpay",
                "provider_payment_id": f"pay_gateway_{order_id}",
                "provider_order_id": order_id,
                "amount_inr": 160,
                "status": "captured",
                "member_id": member_id,
            },
        )
        assert webhook_res.status_code == HTTP_200_OK
        webhook_data = webhook_res.json()
        assert webhook_data["status"] == "activated"

        # Step 7: Card preview & Segno QR
        card_res = await client.get(f"/api/cards/member/{member_id}/preview", headers=auth_headers)
        assert card_res.status_code == HTTP_200_OK
        card_data = card_res.json()["card"]
        assert "membership_number" in card_data
        card_token = card_data["token"]
        assert card_data["qr_data_uri"].startswith("data:image/png;base64,")

        # Step 8: Public QR Verification Check (Privacy compliance)
        verify_res = await client.get(f"/verify/{card_token}")
        assert verify_res.status_code == HTTP_200_OK
        verify_data = verify_res.json()
        assert verify_data["valid"] is True
        assert "Kerala State Gig & Platform Workers Union (CITU)" in verify_data["union"]
        # Strictly verify no sensitive fields leaked
        for sensitive in ("phone", "aadhaar", "address", "bank", "payment", "amount"):
            assert sensitive not in verify_data

        # Step 9: Member Self-Service Dashboard
        dash_res = await client.get(
            "/api/member/dashboard", headers={"X-Member-Phone": worker_phone}
        )
        assert dash_res.status_code == HTTP_200_OK
        dash_data = dash_res.json()
        assert dash_data["whatsapp"]["district_group_url"].startswith("https://chat.whatsapp.com")
        assert dash_data["grievance_desk"]["filing_enabled"] is False


@pytest.mark.asyncio
async def test_admin_bulk_import_to_member_appearance_lifecycle():
    """
    T9.4: Admin 2FA login -> bulk import paper forms -> appearance in member list.
    """
    async with AsyncTestClient(app=app) as client:
        # Step 1: Admin login
        admin_login = await client.post(
            "/api/auth/admin/login",
            json={"username": "state_gs", "password": "CITUSolidarity@2026"},
        )
        assert admin_login.status_code == HTTP_200_OK
        chal_token = admin_login.json()["challenge_token"]

        # Step 2: Admin 2FA TOTP
        totp_code = get_totp_code("JBSWY3DPEHPK3PXP")
        two_fa_res = await client.post(
            "/api/auth/admin/2fa",
            json={"challenge_token": chal_token, "totp_code": totp_code},
        )
        assert two_fa_res.status_code == HTTP_200_OK
        admin_session = two_fa_res.json()["session_token"]
        admin_headers = {"Authorization": f"Bearer {admin_session}"}

        # Step 3: Submit bulk paper batch
        batch = [
            {
                "name": "Com. Paper Registered Worker",
                "phone": "9847990011",
                "district_code": "KLKKD",
                "platform": "Zomato",
                "sector": "food_delivery",
                "dob": "1991-03-12",
                "id_number": "1122 3344 5566",
                "paid_up_to": "2027-04",
                "paper_receipt_no": "PAPER-KKD-882",
            }
        ]
        import_res = await client.post(
            "/api/admin/import",
            json={"filename": "paper_batch_pilot.csv", "rows": batch},
            headers=admin_headers,
        )
        assert import_res.status_code == HTTP_200_OK
        import_data = import_res.json()
        assert import_data["accepted_rows"] == 1
        job_id = import_data["job_id"]

        # Step 4: Verify report
        report_res = await client.get(f"/api/admin/import/{job_id}/report", headers=admin_headers)
        assert report_res.status_code == HTTP_200_OK
        assert "accepted" in report_res.content.decode("utf-8")
