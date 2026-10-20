import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from litestar.testing import AsyncTestClient

from app.main import app


@pytest.mark.asyncio
async def test_member_portal_auth_required():
    """Unauthenticated member cannot access dashboard."""
    async with AsyncTestClient(app=app) as client:
        resp = await client.get("/api/member/dashboard")
        assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_member_portal_dashboard_and_features():
    """
    FR6.1, FR6.2, NFR7.2:
    - Member dashboard with read-only profile
    - Digital card download links & QR
    - District WhatsApp invite link
    - Grievance contacts (filing disabled behind switch)
    - Payment history with receipts
    """
    headers = {"X-Member-Phone": "+919847012345"}

    async with AsyncTestClient(app=app) as client:
        resp = await client.get("/api/member/dashboard", headers=headers)
        assert resp.status_code == HTTP_200_OK
        data = resp.json()
        assert data["success"] is True

        # 1. Profile
        mem = data["member"]
        assert mem["membership_number"] == "KLKKD000042"
        assert "Sakhavu" in mem["full_name"]
        assert mem["district_name"] == "Kozhikode"

        # 2. Digital Card
        card = data["digital_card"]
        assert card["qr_data_uri"].startswith("data:image/png;base64,")
        assert "download_image_url" in card
        assert "download_pdf_url" in card

        # 3. WhatsApp Group Link (FR6.2)
        wa = data["whatsapp"]
        assert "chat.whatsapp.com" in wa["district_group_url"]
        assert "Kozhikode" in wa["district_name"]

        # 4. Grievance Desk (FR6.1, NFR7.2)
        grievance = data["grievance_desk"]
        assert grievance["filing_enabled"] is False  # Switch is OFF
        assert len(grievance["contacts"]) >= 1
        sec = grievance["contacts"][0]
        assert "District Secretary" in sec["role"]

        # 5. Payment History
        assert len(data["payment_history"]) >= 1
        p = data["payment_history"][0]
        assert p["receipt_number"] == "CITU-RCP-2026-0042"
        assert p["amount"] == 160


@pytest.mark.asyncio
async def test_member_language_preference_update():
    """FR9.1, FR9.4: Language switch updates preference between 'ml' and 'en'."""
    headers = {"X-Member-Phone": "+919847012345"}

    async with AsyncTestClient(app=app) as client:
        # Invalid language code
        bad_req = await client.post(
            "/api/member/language",
            json={"language": "fr"},
            headers=headers,
        )
        assert bad_req.status_code == HTTP_400_BAD_REQUEST

        # Valid switch to English
        res_en = await client.post(
            "/api/member/language",
            json={"language": "en"},
            headers=headers,
        )
        assert res_en.status_code == HTTP_200_OK
        assert res_en.json()["language"] == "en"

        # Valid switch back to Malayalam
        res_ml = await client.post(
            "/api/member/language",
            json={"language": "ml"},
            headers=headers,
        )
        assert res_ml.status_code == HTTP_200_OK
        assert res_ml.json()["language"] == "ml"
