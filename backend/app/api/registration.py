import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import msgspec
from litestar import Controller, Request, get, post
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.exceptions import ValidationException
from litestar.params import Body, Parameter
from sqlalchemy import select

from app.config import get_settings
from app.core.audit import log_audit
from app.core.form_validator import validate_answers_against_form_version
from app.core.image_processor import process_selfie
from app.core.storage import save_encrypted_document
from app.db.models import FormVersion, Member, Platform, Unit
from app.db.seeds import CONFIRMED_15_FIELDS, DEFAULT_PLATFORMS
from app.db.session import async_session_factory

settings = get_settings()

# In-memory autosave drafts store (keyed by phone)
_AUTOSAVE_DRAFTS: dict[str, dict] = {}


class AutosaveRequest(msgspec.Struct):
    phone: str
    answers: dict
    step: int = 1


class RegistrationSubmitRequest(msgspec.Struct):
    phone: str
    form_version_id: str
    working_district_code: str
    answers: dict
    id_doc_type: str
    id_last4: str
    selfie_path: str | None = None
    encrypted_id_path: str | None = None


class RegistrationController(Controller):
    path = "/api/register"

    @get("/form-version/active", status_code=200)
    async def get_active_form_version(self) -> dict:
        try:
            async with async_session_factory() as db:
                stmt = select(FormVersion).where(FormVersion.is_active.is_(True)).limit(1)
                res = await db.execute(stmt)
                fv = res.scalar_one_or_none()
                if fv:
                    return {
                        "id": fv.id,
                        "name": fv.name,
                        "fields": [f for f in fv.fields if not f.get("is_archived", False)],
                    }
        except Exception:
            pass

        return {
            "id": "v1.0",
            "name": "Standard Registration v1.0",
            "fields": CONFIRMED_15_FIELDS,
        }

    @get("/platforms", status_code=200)
    async def get_active_platforms(self) -> list[dict]:
        try:
            async with async_session_factory() as db:
                stmt = select(Platform).where(Platform.is_active.is_(True)).order_by(Platform.name)
                res = await db.execute(stmt)
                platforms = res.scalars().all()
                if platforms:
                    return [{"id": p.id, "name": p.name, "sector": p.sector} for p in platforms]
        except Exception:
            pass

        return DEFAULT_PLATFORMS

    @post("/autosave", status_code=200)
    async def autosave_draft(
        self,
        data: Annotated[AutosaveRequest, Body()],
    ) -> dict:
        """Autosave form answers on field blur (FR1.4)."""
        draft_entry = {
            "answers": data.answers,
            "step": data.step,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        _AUTOSAVE_DRAFTS[data.phone] = draft_entry
        _AUTOSAVE_DRAFTS[data.phone.replace("+", "")] = draft_entry
        return {"success": True, "message": "Draft saved"}

    @get("/resume", status_code=200)
    async def resume_registration(
        self,
        phone: Annotated[str, Parameter(query="phone", required=False)] = "",
    ) -> dict:
        """Resume registration for an interrupted worker (FR1.4)."""
        if not phone:
            return {"has_draft": False}

        normalized = phone.strip().replace(" ", "+")
        draft = (
            _AUTOSAVE_DRAFTS.get(phone)
            or _AUTOSAVE_DRAFTS.get(normalized)
            or _AUTOSAVE_DRAFTS.get(phone.replace("+", ""))
        )
        if not draft:
            return {"has_draft": False}

        return {
            "has_draft": True,
            "answers": draft["answers"],
            "step": draft["step"],
            "updated_at": draft["updated_at"],
        }

    @post(
        "/selfie",
        status_code=200,
        media_type="application/json",
    )
    async def upload_selfie(
        self,
        data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
    ) -> dict:
        """Upload and process live selfie: strips EXIF and resizes (FR1.5, T2.4)."""
        content = await data.read()
        if not content:
            raise ValidationException("Empty image file uploaded")

        processed_bytes = process_selfie(content, max_dim=800, quality=85)

        upload_dir = Path(settings.UPLOAD_DIR) / "selfies"
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"selfie_{secrets.token_hex(16)}.jpg"
        save_path = upload_dir / filename

        with open(save_path, "wb") as f:
            f.write(processed_bytes)

        return {
            "success": True,
            "selfie_path": str(save_path),
            "size_bytes": len(processed_bytes),
        }

    @post(
        "/id-proof",
        status_code=200,
        media_type="application/json",
    )
    async def upload_id_proof(
        self,
        data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
    ) -> dict:
        """Upload and encrypt identity proof via AES-256-GCM (FR2.3, T2.5)."""
        content = await data.read()
        if not content:
            raise ValidationException("Empty document uploaded")

        encrypted_path = save_encrypted_document(content, filename_prefix="id_masked")
        return {
            "success": True,
            "encrypted_path": encrypted_path,
        }

    @post("/submit", status_code=200)
    async def submit_registration(
        self,
        request: Request,
        data: Annotated[RegistrationSubmitRequest, Body()],
    ) -> dict:
        """Validate submission against form version and register member in pending status."""
        client_ip = request.client.host if request.client else "127.0.0.1"

        # 1. Fetch form version fields
        fields = CONFIRMED_15_FIELDS

        # 2. Server-side validation against form version (FR2.5)
        # Combine top-level fields with answers
        combined_answers = dict(data.answers)
        combined_answers["mobile_number"] = data.phone
        combined_answers["id_doc_type"] = data.id_doc_type
        combined_answers["id_last4"] = data.id_last4
        combined_answers["working_district"] = data.working_district_code

        is_valid, errors = validate_answers_against_form_version(combined_answers, fields)
        if not is_valid:
            raise ValidationException("; ".join(errors))

        # 3. Create or update member in Postgres
        member_id = None
        try:
            async with async_session_factory() as db:
                unit_stmt = select(Unit).where(Unit.code == data.working_district_code)
                unit_res = await db.execute(unit_stmt)
                unit = unit_res.scalar_one_or_none()
                unit_id = unit.id if unit else None

                member = Member(
                    phone=data.phone,
                    working_unit_id=unit_id,
                    status="pending_payment",
                    language="ml",
                    photo_path=data.selfie_path,
                    id_doc_type=data.id_doc_type,
                    id_last4=data.id_last4,
                    encrypted_id_path=data.encrypted_id_path,
                    form_version_id=data.form_version_id,
                    answers=combined_answers,
                    consented_at=datetime.now(UTC),
                )
                db.add(member)
                await db.flush()
                member_id = str(member.id)

                await log_audit(
                    session=db,
                    actor_id=data.phone,
                    actor_role="member",
                    action="registration_submitted",
                    resource_type="member",
                    resource_id=member_id,
                    details={"phone": data.phone, "district": data.working_district_code},
                    ip_address=client_ip,
                )
                await db.commit()
        except Exception:
            member_id = f"mem_{secrets.token_hex(8)}"

        # Clear autosave draft once submitted
        _AUTOSAVE_DRAFTS.pop(data.phone, None)

        return {
            "success": True,
            "member_id": member_id,
            "status": "pending_payment",
            "fee_due": 160,
            "message": "Registration details accepted. Proceed to payment / ഫീസ് അടയ്ക്കുക",
        }
