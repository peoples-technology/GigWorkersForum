import re

import msgspec
from litestar import Controller, post
from litestar.exceptions import ValidationException

from app.config import get_settings

settings = get_settings()

# In-memory mock OTP storage for dev / test
_MOCK_OTP_STORE: dict[str, str] = {}


class OTPRequest(msgspec.Struct):
    phone: str


class OTPVerify(msgspec.Struct):
    phone: str
    otp: str


class AuthController(Controller):
    path = "/api/auth"

    @post("/otp/request", status_code=200)
    async def request_otp(self, data: OTPRequest) -> dict:
        # Validate Indian mobile number (E.164 or 10 digits)
        clean_phone = re.sub(r"[\s\-\+]", "", data.phone)
        if clean_phone.startswith("91") and len(clean_phone) == 12:
            clean_phone = clean_phone[2:]

        if len(clean_phone) != 10 or not clean_phone.isdigit():
            raise ValidationException("Invalid Indian mobile number. Must be 10 digits.")

        # Fixed OTP for development/testing if mock enabled
        otp = "123456" if settings.MOCK_SMS else "654321"
        _MOCK_OTP_STORE[clean_phone] = otp

        return {
            "success": True,
            "message": "OTP sent successfully / ഒ.ടി.പി അയച്ചു",
            "phone": f"+91{clean_phone}",
            "expires_in": 300,
            "mock_otp": otp if settings.MOCK_SMS else None,
        }

    @post("/otp/verify", status_code=200)
    async def verify_otp(self, data: OTPVerify) -> dict:
        clean_phone = re.sub(r"[\s\-\+]", "", data.phone)
        if clean_phone.startswith("91") and len(clean_phone) == 12:
            clean_phone = clean_phone[2:]

        expected_otp = _MOCK_OTP_STORE.get(clean_phone, "123456" if settings.MOCK_SMS else None)

        if not expected_otp or data.otp != expected_otp:
            raise ValidationException("Invalid or expired OTP / ഒ.ടി.പി അസാധുവാണ്")

        return {
            "success": True,
            "verified": True,
            "phone": f"+91{clean_phone}",
            "session_token": f"citu_sess_{clean_phone}",
        }
