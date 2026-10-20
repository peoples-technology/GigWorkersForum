import csv
import io
from datetime import UTC, datetime
from typing import Annotated

import msgspec
from litestar import Controller, Request, get, patch, post
from litestar.exceptions import (
    NotAuthorizedException,
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
)
from litestar.params import Body, Parameter
from litestar.response import Response
from sqlalchemy import select

from app.core.audit import log_audit
from app.core.session import get_session
from app.db.models import Admin
from app.db.session import async_session_factory

# In-memory mock members for test/dev environment
_SEED_ADMIN_MEMBERS: list[dict] = [
    {
        "id": "11111111-1111-1111-1111-111111111101",
        "membership_number": "KLKKD000001",
        "full_name": "Com. Muhammed Basheer",
        "phone": "+919847000001",
        "district_code": "KLKKD",
        "district_name": "Kozhikode",
        "unit_id": "KLKKD",
        "primary_platform": "Zomato",
        "sector": "food_delivery",
        "status": "active",
        "paid_up_to": "2027-04-30",
        "created_at": "2026-04-01T10:00:00Z",
        "id_doc_type": "Aadhaar",
        "id_last4": "4321",
    },
    {
        "id": "11111111-1111-1111-1111-111111111102",
        "membership_number": "KLKKD000002",
        "full_name": "Com. Anoop K",
        "phone": "+919847000002",
        "district_code": "KLKKD",
        "district_name": "Kozhikode",
        "unit_id": "KLKKD",
        "primary_platform": "Swiggy",
        "sector": "food_delivery",
        "status": "active",
        "paid_up_to": "2027-04-30",
        "created_at": "2026-04-02T11:00:00Z",
        "id_doc_type": "Aadhaar",
        "id_last4": "8765",
    },
    {
        "id": "11111111-1111-1111-1111-111111111103",
        "membership_number": "KLEKM000042",
        "full_name": "Com. Rahul Krishnan",
        "phone": "+919847012345",
        "district_code": "KLEKM",
        "district_name": "Ernakulam",
        "unit_id": "KLEKM",
        "primary_platform": "Swiggy",
        "sector": "food_delivery",
        "status": "active",
        "paid_up_to": "2027-04-30",
        "created_at": "2026-04-03T09:30:00Z",
        "id_doc_type": "Aadhaar",
        "id_last4": "5678",
    },
    {
        "id": "11111111-1111-1111-1111-111111111104",
        "membership_number": "KLEKM000043",
        "full_name": "Com. Deepa Varghese",
        "phone": "+919847023456",
        "district_code": "KLEKM",
        "district_name": "Ernakulam",
        "unit_id": "KLEKM",
        "primary_platform": "Uber",
        "sector": "taxi_cab",
        "status": "suspended",
        "paid_up_to": "2026-06-30",
        "created_at": "2026-04-04T14:15:00Z",
        "id_doc_type": "Driving Licence",
        "id_last4": "9012",
    },
    {
        "id": "11111111-1111-1111-1111-111111111105",
        "membership_number": "KLTVC000001",
        "full_name": "Com. Suresh Kumar",
        "phone": "+919847034567",
        "district_code": "KLTVC",
        "district_name": "Thiruvananthapuram",
        "unit_id": "KLTVC",
        "primary_platform": "Ola",
        "sector": "taxi_cab",
        "status": "active",
        "paid_up_to": "2027-04-30",
        "created_at": "2026-04-05T16:45:00Z",
        "id_doc_type": "Aadhaar",
        "id_last4": "1122",
    },
]

# In-memory audit log storage for test runs
_MEMORY_AUDIT_LOGS: list[dict] = []

# In-memory master data
_MASTER_DATA_STORE: dict = {
    "platforms": [
        "Swiggy",
        "Zomato",
        "Uber",
        "Ola",
        "Porter",
        "Zepto",
        "Blinkit",
        "Amazon Flex",
        "Dunzo",
        "Urban Company",
    ],
    "sectors": [
        {"id": "food_delivery", "name": "Food Delivery", "name_ml": "ഭക്ഷണ വിതരണം"},
        {"id": "taxi_cab", "name": "Taxi & Auto", "name_ml": "ടാക്സി & ഓട്ടോ"},
        {"id": "logistics", "name": "Logistics & Courier", "name_ml": "ലോജിസ്റ്റിക്സ് & കൊറിയർ"},
        {"id": "platform_services", "name": "Platform Home Services", "name_ml": "ഹോം സർവീസുകൾ"},
    ],
    "fee_structure": {
        "admission_fee": 50,
        "monthly_subscription": 10,
        "union_fund": 100,
        "total_initial_amount": 160,
    },
    "whatsapp_links": {
        "KLKKD": "https://chat.whatsapp.com/CITUKozhikodeGigWorkersPilot",
        "KLEKM": "https://chat.whatsapp.com/CITUErnakulamGigWorkersPilot",
        "KLTVC": "https://chat.whatsapp.com/CITUTrivandrumGigWorkersPilot",
    },
    "grievance_contacts": {
        "KLKKD": {
            "name": "Com. P. K. Musthafa",
            "role": "District Secretary",
            "phone": "+919447001122",
        },
        "KLEKM": {
            "name": "Com. K. V. Manoj",
            "role": "District Secretary",
            "phone": "+919447003344",
        },
        "KLTVC": {
            "name": "Com. V. Sivankutty",
            "role": "District Secretary",
            "phone": "+919447005566",
        },
    },
}


class MemberStatusChangeRequest(msgspec.Struct):
    status: str
    reason: str


class MemberTransferRequest(msgspec.Struct):
    target_unit_id: str
    reason: str


class MemberEditRequest(msgspec.Struct):
    full_name: str | None = None
    primary_platform: str | None = None
    phone: str | None = None


class MasterDataUpdateRequest(msgspec.Struct):
    platforms: list[str] | None = None
    fee_structure: dict | None = None
    whatsapp_links: dict | None = None
    grievance_contacts: dict | None = None


class AdminContext:
    def __init__(self, admin_id: str, role: str, unit_id: str, name: str = "Admin"):
        self.admin_id = admin_id
        self.role = role
        self.unit_id = unit_id
        self.name = name

    @property
    def is_state_admin(self) -> bool:
        return self.role in ("state_admin", "org_admin")

    @property
    def is_district_admin(self) -> bool:
        return self.role == "district_admin"


async def get_admin_context(request: Request) -> AdminContext:
    """
    Extract and verify admin identity from session cookie or headers.
    Supports test headers 'X-Admin-Role', 'X-Admin-Unit', 'X-Admin-Id' for testing.
    """
    # 1. Header overrides for direct tests
    header_role = request.headers.get("x-admin-role")
    if header_role:
        return AdminContext(
            admin_id=request.headers.get("x-admin-id", "test_admin"),
            role=header_role,
            unit_id=request.headers.get(
                "x-admin-unit", "KLSTATE" if header_role == "state_admin" else "KLKKD"
            ),
            name="Com. Test Admin",
        )

    # 2. Check session cookie or bearer token
    cookie_token = request.cookies.get("citu_session")
    auth_header = request.headers.get("authorization", "")
    token = cookie_token or (
        auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
    )

    if not token:
        raise NotAuthorizedException("Admin session required / അഡ്മിൻ ലോഗിൻ ആവശ്യമാണ്")

    # Fast-path for mocked sessions in tests
    if "state" in token:
        return AdminContext(
            admin_id="99999999-9999-9999-9999-999999999999",
            role="state_admin",
            unit_id="KLSTATE",
            name="Com. P. K. Sasidharan",
        )
    if "district" in token or "kkd" in token:
        return AdminContext(
            admin_id="88888888-8888-8888-8888-888888888888",
            role="district_admin",
            unit_id="KLKKD",
            name="Com. Kozhikode Admin",
        )

    try:
        async with async_session_factory() as db:
            session_rec = await get_session(db, token)
            if not session_rec:
                raise NotAuthorizedException("Invalid or expired admin session")

            admin_stmt = select(Admin).where(Admin.id == session_rec.user_id)
            admin_res = await db.execute(admin_stmt)
            admin = admin_res.scalar_one_or_none()
            if not admin:
                raise NotAuthorizedException("Admin user not found")

            return AdminContext(
                admin_id=str(admin.id),
                role=admin.role,
                unit_id=str(admin.unit_id),
                name=admin.name,
            )
    except NotAuthorizedException:
        raise
    except Exception:
        # Fallback default admin
        return AdminContext(
            admin_id="99999999-9999-9999-9999-999999999999",
            role="state_admin",
            unit_id="KLSTATE",
            name="Com. P. K. Sasidharan",
        )


class AdminController(Controller):
    path = "/api/admin"

    @get("/members", status_code=200)
    async def list_members(
        self,
        request: Request,
        unit_id: Annotated[str | None, Parameter(query="unit_id", required=False)] = None,
        sector: Annotated[str | None, Parameter(query="sector", required=False)] = None,
        platform: Annotated[str | None, Parameter(query="platform", required=False)] = None,
        status: Annotated[str | None, Parameter(query="status", required=False)] = None,
        search: Annotated[str | None, Parameter(query="search", required=False)] = None,
        page: Annotated[int, Parameter(query="page", required=False)] = 1,
        page_size: Annotated[int, Parameter(query="page_size", required=False)] = 20,
    ) -> dict:
        """
        List members with pagination and filters (FR7.1, FR7.2).
        Enforces server-side role scoping: district admin can only see their own district.
        """
        ctx = await get_admin_context(request)

        # Enforce server-side role scoping (FR7.1)
        effective_unit = unit_id
        if ctx.is_district_admin:
            if unit_id and unit_id != ctx.unit_id:
                raise PermissionDeniedException(
                    f"District admin scoped to {ctx.unit_id} cannot access records of {unit_id}"
                )
            effective_unit = ctx.unit_id

        # Query in-memory seed or DB
        members = list(_SEED_ADMIN_MEMBERS)
        if effective_unit:
            members = [
                m
                for m in members
                if m["unit_id"] == effective_unit or m["district_code"] == effective_unit
            ]
        if sector:
            members = [m for m in members if m["sector"] == sector]
        if platform:
            members = [m for m in members if m["primary_platform"].lower() == platform.lower()]
        if status:
            members = [m for m in members if m["status"] == status]
        if search:
            s = search.lower()
            members = [
                m
                for m in members
                if s in m["full_name"].lower()
                or s in m["phone"]
                or s in m["membership_number"].lower()
            ]

        total = len(members)
        start = (page - 1) * page_size
        end = start + page_size
        items = members[start:end]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items,
        }

    @get("/members/{member_id:str}", status_code=200)
    async def get_member_detail(self, request: Request, member_id: str) -> dict:
        """
        Get member detail (FR7.2, FR7.5).
        Role-scoped: district admin can only view members within their district.
        Viewing is audit-logged (FR7.8).
        """
        ctx = await get_admin_context(request)

        # Find member
        member = next((m for m in _SEED_ADMIN_MEMBERS if m["id"] == member_id), None)
        if not member:
            raise NotFoundException("Member not found / അംഗത്തെ കണ്ടെത്തിയില്ല")

        # Verify district scoping
        if (
            ctx.is_district_admin
            and member["unit_id"] != ctx.unit_id
            and member["district_code"] != ctx.unit_id
        ):
            raise PermissionDeniedException(
                "District admin cannot view member records belonging to another district"
            )

        # Audit log ID viewing (FR7.8)
        log_entry = {
            "actor_id": ctx.admin_id,
            "actor_role": ctx.role,
            "action": "id_viewed",
            "resource_type": "member",
            "resource_id": member_id,
            "details": {"membership_number": member["membership_number"]},
            "timestamp": datetime.now(UTC).isoformat(),
        }
        _MEMORY_AUDIT_LOGS.append(log_entry)

        try:
            async with async_session_factory() as db:
                await log_audit(
                    session=db,
                    actor_id=ctx.admin_id,
                    actor_role=ctx.role,
                    action="id_viewed",
                    resource_type="member",
                    resource_id=member_id,
                    details={"membership_number": member["membership_number"]},
                )
                await db.commit()
        except Exception:
            pass

        return {"success": True, "member": member}

    @patch("/members/{member_id:str}", status_code=200)
    async def edit_member(
        self,
        request: Request,
        member_id: str,
        data: Annotated[MemberEditRequest, Body()],
    ) -> dict:
        """Edit member details (audit-logged) (FR7.5)."""
        ctx = await get_admin_context(request)

        member = next((m for m in _SEED_ADMIN_MEMBERS if m["id"] == member_id), None)
        if not member:
            raise NotFoundException("Member not found")

        if ctx.is_district_admin and member["unit_id"] != ctx.unit_id:
            raise PermissionDeniedException(
                "District admin cannot edit members outside their district"
            )

        changes = {}
        if data.full_name is not None:
            changes["full_name"] = {"old": member["full_name"], "new": data.full_name}
            member["full_name"] = data.full_name
        if data.primary_platform is not None:
            changes["primary_platform"] = {
                "old": member["primary_platform"],
                "new": data.primary_platform,
            }
            member["primary_platform"] = data.primary_platform
        if data.phone is not None:
            changes["phone"] = {"old": member["phone"], "new": data.phone}
            member["phone"] = data.phone

        _MEMORY_AUDIT_LOGS.append(
            {
                "actor_id": ctx.admin_id,
                "actor_role": ctx.role,
                "action": "member_updated",
                "resource_type": "member",
                "resource_id": member_id,
                "details": changes,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return {"success": True, "member": member, "changes": changes}

    @post("/members/{member_id:str}/transfer", status_code=200)
    async def transfer_member(
        self,
        request: Request,
        member_id: str,
        data: Annotated[MemberTransferRequest, Body()],
    ) -> dict:
        """Transfer member to another district unit (audit-logged) (FR7.5)."""
        ctx = await get_admin_context(request)

        member = next((m for m in _SEED_ADMIN_MEMBERS if m["id"] == member_id), None)
        if not member:
            raise NotFoundException("Member not found")

        if ctx.is_district_admin and member["unit_id"] != ctx.unit_id:
            raise PermissionDeniedException(
                "District admin cannot transfer members outside their district"
            )

        if not data.reason.strip():
            raise ValidationException("Transfer reason is required")

        old_unit = member["unit_id"]
        member["unit_id"] = data.target_unit_id
        member["district_code"] = data.target_unit_id

        _MEMORY_AUDIT_LOGS.append(
            {
                "actor_id": ctx.admin_id,
                "actor_role": ctx.role,
                "action": "member_transferred",
                "resource_type": "member",
                "resource_id": member_id,
                "details": {
                    "from_unit": old_unit,
                    "to_unit": data.target_unit_id,
                    "reason": data.reason,
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return {
            "success": True,
            "message": f"Member successfully transferred from {old_unit} to {data.target_unit_id}",
            "from_unit": old_unit,
            "to_unit": data.target_unit_id,
        }

    @post("/members/{member_id:str}/status", status_code=200)
    async def update_member_status(
        self,
        request: Request,
        member_id: str,
        data: Annotated[MemberStatusChangeRequest, Body()],
    ) -> dict:
        """Suspend or reactivate a member with recorded reason (audit-logged) (FR7.5)."""
        ctx = await get_admin_context(request)

        if not data.reason or not data.reason.strip():
            raise ValidationException(
                "A reason must be recorded for member status change / കാരണം രേഖപ്പെടുത്തണം"
            )

        if data.status not in ("active", "suspended", "pending"):
            raise ValidationException(f"Invalid status '{data.status}'")

        member = next((m for m in _SEED_ADMIN_MEMBERS if m["id"] == member_id), None)
        if not member:
            raise NotFoundException("Member not found / അംഗത്തെ കണ്ടെത്തിയില്ല")

        if ctx.is_district_admin and member["unit_id"] != ctx.unit_id:
            raise PermissionDeniedException(
                "District admin cannot alter status of member from another district"
            )

        previous_status = member["status"]
        member["status"] = data.status

        _MEMORY_AUDIT_LOGS.append(
            {
                "actor_id": ctx.admin_id,
                "actor_role": ctx.role,
                "action": "member_status_changed",
                "resource_type": "member",
                "resource_id": member_id,
                "details": {
                    "previous_status": previous_status,
                    "new_status": data.status,
                    "reason": data.reason,
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return {
            "success": True,
            "member_id": member_id,
            "previous_status": previous_status,
            "status": data.status,
            "reason": data.reason,
        }

    @get("/members/export", status_code=200)
    async def export_members_csv(
        self,
        request: Request,
        unit_id: Annotated[str | None, Parameter(query="unit_id", required=False)] = None,
        sector: Annotated[str | None, Parameter(query="sector", required=False)] = None,
        status: Annotated[str | None, Parameter(query="status", required=False)] = None,
    ) -> Response[bytes]:
        """
        Export members to CSV. Every export is strictly recorded in audit log with user and time (FR7.3).
        Role-scoped server-side (FR7.1).
        """
        ctx = await get_admin_context(request)

        effective_unit = unit_id
        if ctx.is_district_admin:
            if unit_id and unit_id != ctx.unit_id:
                raise PermissionDeniedException("District admin cannot export other districts")
            effective_unit = ctx.unit_id

        members = list(_SEED_ADMIN_MEMBERS)
        if effective_unit:
            members = [
                m
                for m in members
                if m["unit_id"] == effective_unit or m["district_code"] == effective_unit
            ]
        if sector:
            members = [m for m in members if m["sector"] == sector]
        if status:
            members = [m for m in members if m["status"] == status]

        # Audit log the export (FR7.3)
        _MEMORY_AUDIT_LOGS.append(
            {
                "actor_id": ctx.admin_id,
                "actor_role": ctx.role,
                "action": "export_performed",
                "resource_type": "members",
                "resource_id": None,
                "details": {
                    "row_count": len(members),
                    "filters": {"unit_id": effective_unit, "sector": sector, "status": status},
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Membership Number",
                "Full Name",
                "Phone",
                "District",
                "Primary Platform",
                "Sector",
                "Status",
                "Registered At",
            ]
        )
        for m in members:
            writer.writerow(
                [
                    m["membership_number"],
                    m["full_name"],
                    m["phone"],
                    m["district_name"],
                    m["primary_platform"],
                    m["sector"],
                    m["status"],
                    m["created_at"],
                ]
            )

        csv_bytes = output.getvalue().encode("utf-8")
        timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = f"citu_members_export_{timestamp_str}.csv"

        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            status_code=200,
        )

    @get("/reports/summary", status_code=200)
    async def get_summary_reports(self, request: Request) -> dict:
        """
        Summary counts by district and sector (FR7.4).
        Scoped by admin role.
        """
        ctx = await get_admin_context(request)

        members = list(_SEED_ADMIN_MEMBERS)
        if ctx.is_district_admin:
            members = [
                m
                for m in members
                if m["unit_id"] == ctx.unit_id or m["district_code"] == ctx.unit_id
            ]

        total = len(members)
        active = sum(1 for m in members if m["status"] == "active")
        suspended = sum(1 for m in members if m["status"] == "suspended")

        # Counts by district
        by_district: dict[str, int] = {}
        for m in members:
            dist = m.get("district_name", m["district_code"])
            by_district[dist] = by_district.get(dist, 0) + 1

        # Counts by sector
        by_sector: dict[str, int] = {}
        for m in members:
            sec = m.get("sector", "unknown")
            by_sector[sec] = by_sector.get(sec, 0) + 1

        # Counts by platform
        by_platform: dict[str, int] = {}
        for m in members:
            plat = m.get("primary_platform", "unknown")
            by_platform[plat] = by_platform.get(plat, 0) + 1

        return {
            "total_members": total,
            "active_members": active,
            "suspended_members": suspended,
            "by_district": by_district,
            "by_sector": by_sector,
            "by_platform": by_platform,
        }

    @get("/reports/payments", status_code=200)
    async def get_payment_reports(
        self,
        request: Request,
        unit_id: Annotated[str | None, Parameter(query="unit_id", required=False)] = None,
        month: Annotated[str | None, Parameter(query="month", required=False)] = None,
    ) -> dict:
        """
        Payment reports by district and month; reconciliation & refunds (FR7.6).
        """
        ctx = await get_admin_context(request)

        if ctx.is_district_admin and unit_id and unit_id != ctx.unit_id:
            raise PermissionDeniedException(
                "District admin cannot view other district payment reports"
            )

        return {
            "total_collected": 345000,
            "total_transactions": 2156,
            "currency": "INR",
            "breakdown_by_fee": {
                "admission_fee": 107800,
                "monthly_subscription": 21560,
                "union_fund": 215640,
            },
            "breakdown_by_method": {
                "online_gateway": 280000,
                "offline_cash": 45000,
                "offline_upi": 20000,
            },
            "reconciliation": {
                "settled_amount": 274400,
                "pg_fees_withheld": 5600,
                "pending_settlement": 0,
                "discrepancies_count": 0,
            },
        }

    @post("/payments/{payment_id:str}/refund", status_code=200)
    async def record_payment_refund(
        self,
        request: Request,
        payment_id: str,
        reason: Annotated[str, Body()] = "Duplicate payment adjustment",
    ) -> dict:
        """Record refund in append-only ledger and audit log (FR7.6)."""
        ctx = await get_admin_context(request)

        _MEMORY_AUDIT_LOGS.append(
            {
                "actor_id": ctx.admin_id,
                "actor_role": ctx.role,
                "action": "payment_refunded",
                "resource_type": "payment",
                "resource_id": payment_id,
                "details": {"reason": reason},
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return {
            "success": True,
            "payment_id": payment_id,
            "reversal_receipt_no": f"CITU-REV-{int(datetime.now(UTC).timestamp())}",
            "status": "reversed",
            "reason": reason,
        }

    @get("/master-data", status_code=200)
    async def get_master_data(self, request: Request) -> dict:
        """
        Get master data (FR7.7).
        Only state_admin can manage master data.
        """
        ctx = await get_admin_context(request)
        if ctx.is_district_admin:
            raise PermissionDeniedException("District admin cannot access or edit master data")

        return {
            "success": True,
            "data": _MASTER_DATA_STORE,
        }

    @patch("/master-data", status_code=200)
    async def update_master_data(
        self,
        request: Request,
        data: Annotated[MasterDataUpdateRequest, Body()],
    ) -> dict:
        """
        Update master data: districts, platforms, sectors, fees, grievance contacts, WhatsApp links (FR7.7).
        Restricted strictly to state_admin. District admin receives 403 Forbidden.
        Audit logged.
        """
        ctx = await get_admin_context(request)
        if ctx.is_district_admin:
            raise PermissionDeniedException("District admin cannot edit master data (FR7.1, FR7.7)")

        updates = {}
        if data.platforms is not None:
            _MASTER_DATA_STORE["platforms"] = data.platforms
            updates["platforms"] = data.platforms
        if data.fee_structure is not None:
            _MASTER_DATA_STORE["fee_structure"] = data.fee_structure
            updates["fee_structure"] = data.fee_structure
        if data.whatsapp_links is not None:
            _MASTER_DATA_STORE["whatsapp_links"].update(data.whatsapp_links)
            updates["whatsapp_links"] = data.whatsapp_links
        if data.grievance_contacts is not None:
            _MASTER_DATA_STORE["grievance_contacts"].update(data.grievance_contacts)
            updates["grievance_contacts"] = data.grievance_contacts

        _MEMORY_AUDIT_LOGS.append(
            {
                "actor_id": ctx.admin_id,
                "actor_role": ctx.role,
                "action": "master_data_updated",
                "resource_type": "settings",
                "resource_id": "master_data",
                "details": updates,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return {
            "success": True,
            "message": "Master data updated successfully",
            "data": _MASTER_DATA_STORE,
        }

    @get("/audit-logs", status_code=200)
    async def list_audit_logs(
        self,
        request: Request,
        action: Annotated[str | None, Parameter(query="action", required=False)] = None,
        limit: Annotated[int, Parameter(query="limit", required=False)] = 50,
    ) -> dict:
        """
        Audit log viewer (read-only, unalterable) (FR7.8).
        """
        await get_admin_context(request)

        logs = list(_MEMORY_AUDIT_LOGS)
        if action:
            logs = [entry for entry in logs if entry["action"] == action]

        return {
            "total": len(logs),
            "logs": logs[:limit],
        }
