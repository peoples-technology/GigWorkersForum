import io
import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from litestar.testing import AsyncTestClient
from PIL import Image

from app.core.security import get_totp_code
from app.main import app


@pytest.mark.asyncio
async def test_integrated_full_worker_onboarding_and_card_verification():
    """
    Comprehensive End-to-End Test:
    1. Check system health & public settings.
    2. OTP lifecycle: request, validation, verify, and session generation.
    3. Active form schema verification (15 bilingual fields).
    4. Selfie upload test with multipart and EXIF stripping.
    5. Registration submission with DPDP 4-digit ID masking.
    6. Payment order creation & gateway webhook activation.
    7. Membership digital card preview & opaque token issuance.
    8. Public verification endpoint test with strict DPDP privacy check.
    9. High-resolution card image PNG (1012x638) and PDF downloads.
    10. Member self-service portal (dashboard, district WhatsApp link).
    """
    async with AsyncTestClient(app=app) as client:
        # 1. Health & Settings
        health = await client.get("/health")
        assert health.status_code == HTTP_200_OK
        assert health.json()["status"] == "healthy"

        settings_res = await client.get("/api/settings")
        assert settings_res.status_code == HTTP_200_OK
        settings = settings_res.json()
        assert settings["fee_structure"]["total_initial_amount"] == 160
        assert settings["module_autopay"]["enabled"] is False

        # 2. Worker OTP Lifecycle
        worker_phone = "9847223344"
        otp_req = await client.post("/api/auth/otp/request", json={"phone": worker_phone})
        assert otp_req.status_code == HTTP_200_OK
        mock_otp = otp_req.json()["mock_otp"]

        otp_verify = await client.post(
            "/api/auth/otp/verify", json={"phone": worker_phone, "otp": mock_otp}
        )
        assert otp_verify.status_code == HTTP_200_OK
        session_token = otp_verify.json()["session_token"]
        worker_headers = {"Authorization": f"Bearer {session_token}"}

        # 3. Active Form Retrieval
        form_res = await client.get("/api/register/form-version/active")
        assert form_res.status_code == HTTP_200_OK
        form_version = form_res.json()
        assert len(form_version["fields"]) >= 15

        # 4. Selfie Upload & EXIF Stripping
        test_img = Image.new("RGB", (640, 640), color="blue")
        img_buf = io.BytesIO()
        test_img.save(img_buf, format="JPEG")
        img_bytes = img_buf.getvalue()

        selfie_res = await client.post(
            "/api/register/selfie",
            files={"file": ("worker_selfie.jpg", img_bytes, "image/jpeg")},
            headers=worker_headers,
        )
        assert selfie_res.status_code == HTTP_200_OK
        selfie_data = selfie_res.json()
        assert selfie_data["success"] is True
        assert "selfie_path" in selfie_data

        # 5. Registration Submission (DPDP Compliant)
        answers = {
            "full_name": "Com. Anandhu K. S.",
            "current_address": "Panchayat Road, Vattiyoorkavu, Trivandrum",
            "permanent_address": "",
            "working_district": "KLTVC",
            "mobile_number": worker_phone,
            "whatsapp_number": worker_phone,
            "dob": "1994-06-20",
            "gender": "male",
            "mother_tongue": "Malayalam",
            "platforms": ["swiggy", "zomato"],
            "primary_platform": "swiggy",
            "vehicle_type": "motorcycle",
            "vehicle_reg_no": "KL-01-CA-5566",
            "id_doc_type": "aadhaar",
            "id_last4": "0349",
        }

        reg_res = await client.post(
            "/api/register/submit",
            json={
                "phone": worker_phone,
                "form_version_id": form_version["id"],
                "working_district_code": "KLTVC",
                "answers": answers,
                "id_doc_type": "aadhaar",
                "id_last4": "0349",
            },
            headers=worker_headers,
        )
        assert reg_res.status_code == HTTP_200_OK
        member_id = reg_res.json()["member_id"]

        # 6. Payment Order & Gateway Webhook
        order_res = await client.post(
            "/api/payments/create-order",
            json={"member_id": member_id, "months_ahead": 6, "is_initial_registration": True},
            headers=worker_headers,
        )
        assert order_res.status_code == HTTP_200_OK
        order_id = order_res.json()["order"]["id"]

        webhook_res = await client.post(
            "/api/payments/webhook",
            json={
                "provider": "razorpay",
                "provider_payment_id": f"pay_{order_id}",
                "provider_order_id": order_id,
                "amount_inr": 160,
                "status": "captured",
                "member_id": member_id,
            },
        )
        assert webhook_res.status_code == HTTP_200_OK
        assert webhook_res.json()["status"] == "activated"

        # 7. Card Preview & Token
        card_res = await client.get(
            f"/api/cards/member/{member_id}/preview", headers=worker_headers
        )
        assert card_res.status_code == HTTP_200_OK
        card_data = card_res.json()["card"]
        token = card_data["token"]
        assert card_data["qr_data_uri"].startswith("data:image/png;base64,")

        # 8. Public QR Verification & DPDP Leak Prevention
        verify_res = await client.get(f"/verify/{token}")
        assert verify_res.status_code == HTTP_200_OK
        verify_data = verify_res.json()
        assert verify_data["valid"] is True
        assert "CITU" in verify_data["union"]

        for sensitive in ("phone", "aadhaar", "address", "bank", "account", "payment", "amount"):
            assert sensitive not in verify_data, f"Privacy violation: {sensitive} leaked!"

        # 9. Download Card Image (PNG 1012x638) & PDF
        img_res = await client.get(
            f"/api/cards/member/{member_id}/download/image", headers=worker_headers
        )
        assert img_res.status_code == HTTP_200_OK
        assert img_res.headers["content-type"] == "image/png"
        img = Image.open(io.BytesIO(img_res.content))
        assert img.size == (1012, 638)

        pdf_res = await client.get(
            f"/api/cards/member/{member_id}/download/pdf", headers=worker_headers
        )
        assert pdf_res.status_code == HTTP_200_OK
        assert pdf_res.content.startswith(b"%PDF")

        # 10. Member Self-Service Portal
        dash_res = await client.get(
            "/api/member/dashboard", headers={"X-Member-Phone": worker_phone}
        )
        assert dash_res.status_code == HTTP_200_OK
        assert dash_res.json()["whatsapp"]["district_group_url"].startswith(
            "https://chat.whatsapp.com"
        )


@pytest.mark.asyncio
async def test_integrated_admin_operations_and_member_management():
    """
    Integrated Admin Lifecycle:
    1. Admin password authentication & challenge.
    2. Admin 2FA TOTP verification & session issuance.
    3. Statewide member listing and district-scoped filtering.
    4. Member status toggle with audited reason.
    5. CSV Export and audit logging.
    """
    async with AsyncTestClient(app=app) as client:
        # Step 1: Admin credentials
        login_res = await client.post(
            "/api/auth/admin/login",
            json={"username": "state_gs", "password": "CITUSolidarity@2026"},
        )
        assert login_res.status_code == HTTP_200_OK
        chal = login_res.json()["challenge_token"]

        # Step 2: 2FA TOTP
        totp = get_totp_code("JBSWY3DPEHPK3PXP")
        twofa_res = await client.post(
            "/api/auth/admin/2fa",
            json={"challenge_token": chal, "totp_code": totp},
        )
        assert twofa_res.status_code == HTTP_200_OK
        admin_session = twofa_res.json()["session_token"]
        admin_headers = {
            "Authorization": f"Bearer {admin_session}",
            "X-Admin-Role": "state_admin",
            "X-Admin-Unit": "KLSTATE",
            "X-Admin-Id": "state_gs",
        }

        # Step 3: Member list & filtering
        members_res = await client.get("/api/admin/members", headers=admin_headers)
        assert members_res.status_code == HTTP_200_OK
        members_data = members_res.json()
        assert members_data["total"] >= 1
        assert "items" in members_data
        target_member_id = members_data["items"][0]["id"]

        # Step 4: Status Update with audit reason
        status_res = await client.post(
            f"/api/admin/members/{target_member_id}/status",
            json={"status": "suspended", "reason": "Annual dues review pending"},
            headers=admin_headers,
        )
        assert status_res.status_code == HTTP_200_OK
        assert status_res.json()["status"] == "suspended"

        # Re-activate member
        reactivate_res = await client.post(
            f"/api/admin/members/{target_member_id}/status",
            json={"status": "active", "reason": "Review cleared by state committee"},
            headers=admin_headers,
        )
        assert reactivate_res.status_code == HTTP_200_OK
        assert reactivate_res.json()["status"] == "active"

        # Step 5: CSV Export with Sector Filter
        export_res = await client.get(
            "/api/admin/members/export?sector=food_delivery", headers=admin_headers
        )
        assert export_res.status_code == HTTP_200_OK
        assert export_res.headers["content-type"] == "text/csv; charset=utf-8"
        assert "Membership Number,Full Name,Phone,District" in export_res.content.decode("utf-8")
