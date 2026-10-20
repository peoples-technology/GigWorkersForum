import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from litestar.testing import AsyncTestClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/health")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "CITU Kerala" in data["app"]


@pytest.mark.asyncio
async def test_public_settings():
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/api/settings")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "fee_structure" in data
        assert data["fee_structure"]["total_initial_amount"] == 160
        assert data["module_autopay"]["enabled"] is False


@pytest.mark.asyncio
async def test_units_districts_list():
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/api/units")
        assert response.status_code == HTTP_200_OK
        districts = response.json()
        assert len(districts) == 14
        tvm = next(d for d in districts if d["code"] == "KLTVC")
        assert tvm["name"] == "Thiruvananthapuram"
        assert "തിരുവനന്തപുരം" in tvm["name_ml"]


@pytest.mark.asyncio
async def test_otp_flow():
    async with AsyncTestClient(app=app) as client:
        # 1. Request OTP with invalid phone
        bad_req = await client.post("/api/auth/otp/request", json={"phone": "123"})
        assert bad_req.status_code == HTTP_400_BAD_REQUEST

        # 2. Request OTP with valid Kerala phone
        req = await client.post("/api/auth/otp/request", json={"phone": "9847012345"})
        assert req.status_code == HTTP_200_OK
        otp_data = req.json()
        assert otp_data["success"] is True
        mock_otp = otp_data["mock_otp"]
        assert mock_otp == "123456"

        # 3. Verify with wrong OTP
        wrong = await client.post(
            "/api/auth/otp/verify", json={"phone": "9847012345", "otp": "000000"}
        )
        assert wrong.status_code == HTTP_400_BAD_REQUEST

        # 4. Verify with correct OTP
        good = await client.post(
            "/api/auth/otp/verify", json={"phone": "9847012345", "otp": mock_otp}
        )
        assert good.status_code == HTTP_200_OK
        good_data = good.json()
        assert good_data["verified"] is True
        assert "citu_sess_" in good_data["session_token"]

