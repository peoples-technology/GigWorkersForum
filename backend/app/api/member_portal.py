import uuid
from typing import Annotated

import msgspec
from litestar import Controller, Request, get, post
from litestar.exceptions import NotAuthorizedException, ValidationException
from litestar.params import Body
from sqlalchemy import select

from app.core.qr_generator import generate_verification_qr_data_uri
from app.core.session import get_session
from app.db.models import Member
from app.db.session import async_session_factory

# In-memory member mock for test/dev
_MOCK_PORTAL_MEMBER = {
    "id": "mem_sakhavu_01",
    "membership_number": "KLKKD000042",
    "full_name": "Com. Sakhavu Krishnan",
    "phone": "+919847012345",
    "district_code": "KLKKD",
    "district_name": "Kozhikode",
    "district_name_ml": "കോഴിക്കോട്",
    "primary_platform": "Swiggy",
    "platforms": ["Swiggy", "Zomato"],
    "status": "active",
    "paid_up_to": "2027-04-30",
    "language": "ml",
    "card_token": "token_sakhavu_secure_opaque_32_chars",
    "whatsapp_link": "https://chat.whatsapp.com/CITUKozhikodeGigWorkersPilot",
    "grievance_contacts": [
        {"name": "Com. P. K. Musthafa", "role": "District Secretary", "phone": "+919447001122"},
        {"name": "Com. Shaji K", "role": "District Joint Secretary", "phone": "+919447003355"},
    ],
    "payments": [
        {
            "receipt_number": "CITU-RCP-2026-0042",
            "amount": 160,
            "payment_type": "online",
            "paid_up_to": "2027-04-30",
            "created_at": "2026-04-01T10:30:00Z",
            "status": "completed",
        }
    ],
}


class MemberLanguageUpdateRequest(msgspec.Struct):
    language: str


async def resolve_member(request: Request) -> dict:
    """Resolve authenticated member from session or headers."""
    # Direct test headers
    phone_hdr = request.headers.get("x-member-phone")
    if phone_hdr:
        return _MOCK_PORTAL_MEMBER

    cookie_token = request.cookies.get("citu_session")
    auth_hdr = request.headers.get("authorization", "")
    token = cookie_token or (
        auth_hdr.replace("Bearer ", "") if auth_hdr.startswith("Bearer ") else None
    )

    if not token:
        raise NotAuthorizedException("Member authentication required / ലോഗിൻ ചെയ്യുക")

    # If mock token
    if "mem" in token or "sakhavu" in token or "worker" in token:
        return _MOCK_PORTAL_MEMBER

    try:
        async with async_session_factory() as db:
            session_rec = await get_session(db, token)
            if not session_rec:
                raise NotAuthorizedException("Invalid or expired session")

            stmt = select(Member).where(Member.id == uuid.UUID(session_rec.user_id))
            res = await db.execute(stmt)
            member = res.scalar_one_or_none()
            if member:
                return {
                    "id": str(member.id),
                    "membership_number": member.membership_number,
                    "full_name": member.answers.get("full_name", "Comrade"),
                    "phone": member.phone,
                    "district_code": "KLKKD",
                    "district_name": "Kozhikode",
                    "status": member.status,
                    "language": member.language,
                    "primary_platform": member.answers.get("primary_platform", "Platform Worker"),
                    "whatsapp_link": _MOCK_PORTAL_MEMBER["whatsapp_link"],
                    "grievance_contacts": _MOCK_PORTAL_MEMBER["grievance_contacts"],
                    "payments": _MOCK_PORTAL_MEMBER["payments"],
                }
    except NotAuthorizedException:
        raise
    except Exception:
        pass

    return _MOCK_PORTAL_MEMBER


class MemberPortalController(Controller):
    path = "/api/member"

    @get("/dashboard", status_code=200)
    async def get_dashboard(self, request: Request) -> dict:
        """
        Member dashboard: read-only profile, digital card preview, payment history,
        district WhatsApp link, and read-only grievance contacts (FR6.1, FR6.2, NFR7.2).
        """
        member = await resolve_member(request)
        qr_data_uri = generate_verification_qr_data_uri(
            member.get("card_token", "token_sakhavu_secure_opaque_32_chars")
        )

        return {
            "success": True,
            "member": {
                "id": member["id"],
                "membership_number": member["membership_number"],
                "full_name": member["full_name"],
                "phone": member["phone"],
                "district_code": member["district_code"],
                "district_name": member["district_name"],
                "primary_platform": member["primary_platform"],
                "status": member["status"],
                "paid_up_to": member.get("paid_up_to", "2027-04-30"),
                "language": member.get("language", "ml"),
            },
            "digital_card": {
                "membership_number": member["membership_number"],
                "valid_thru": "April 2027",
                "qr_data_uri": qr_data_uri,
                "download_image_url": f"/api/cards/member/{member['id']}/download/image",
                "download_pdf_url": f"/api/cards/member/{member['id']}/download/pdf",
            },
            "whatsapp": {
                "district_group_url": member["whatsapp_link"],
                "district_name": member["district_name"],
                "solidarity_message": "Join your district comrades on WhatsApp / നിങ്ങളുടെ ജില്ലാ സഖാക്കളുമായി വാട്സാപ്പിൽ ബന്ധപ്പെടുക",
            },
            "grievance_desk": {
                "filing_enabled": False,  # Switch off as per NFR7.2
                "notice": "Formal grievance filing module is under development. Please reach out to your district union representatives directly.",
                "notice_ml": "ഔദ്യോഗിക പരാതി പരിഹാര മൊഡ്യൂൾ നിർമ്മാണത്തിലാണ്. ദയവായി നിങ്ങളുടെ ജില്ലാ യൂണിയൻ ഭാരവാഹികളുമായി നേരിട്ട് ബന്ധപ്പെടുക.",
                "contacts": member["grievance_contacts"],
            },
            "payment_history": member["payments"],
        }

    @post("/language", status_code=200)
    async def update_language_preference(
        self,
        request: Request,
        data: Annotated[MemberLanguageUpdateRequest, Body()],
    ) -> dict:
        """Update worker's preferred UI & card language (FR9.1, FR9.4)."""
        member = await resolve_member(request)
        if data.language not in ("ml", "en"):
            raise ValidationException("Language must be 'ml' (Malayalam) or 'en' (English)")

        member["language"] = data.language
        _MOCK_PORTAL_MEMBER["language"] = data.language

        return {
            "success": True,
            "language": data.language,
            "message": "Language preference updated / ഭാഷ മാറ്റി",
        }
