import pytest
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)
from litestar.testing import AsyncTestClient

from app.main import app


@pytest.mark.asyncio
async def test_admin_auth_required():
    """Unauthenticated access to admin endpoints must be rejected with 401."""
    async with AsyncTestClient(app=app) as client:
        resp = await client.get("/api/admin/members")
        assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_district_admin_role_scoping():
    """
    FR7.1: District login sees only its own district.
    Attempting to view or filter another district returns 403 Forbidden.
    """
    headers_kkd = {
        "X-Admin-Role": "district_admin",
        "X-Admin-Unit": "KLKKD",
        "X-Admin-Id": "admin_kkd_01",
    }

    async with AsyncTestClient(app=app) as client:
        # 1. Own district succeeds
        resp = await client.get("/api/admin/members?unit_id=KLKKD", headers=headers_kkd)
        assert resp.status_code == HTTP_200_OK
        data = resp.json()
        assert data["total"] >= 2
        for item in data["items"]:
            assert item["district_code"] == "KLKKD"

        # 2. Querying without explicit unit_id is automatically scoped to own district
        resp_default = await client.get("/api/admin/members", headers=headers_kkd)
        assert resp_default.status_code == HTTP_200_OK
        for item in resp_default.json()["items"]:
            assert item["district_code"] == "KLKKD"

        # 3. Querying another district explicitly (e.g. KLEKM) is rejected with 403 Forbidden
        resp_forbidden = await client.get("/api/admin/members?unit_id=KLEKM", headers=headers_kkd)
        assert resp_forbidden.status_code == HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_state_admin_wide_access():
    """
    FR7.1: State office-bearers can view members across all districts.
    """
    headers_state = {
        "X-Admin-Role": "state_admin",
        "X-Admin-Unit": "KLSTATE",
        "X-Admin-Id": "state_gs",
    }

    async with AsyncTestClient(app=app) as client:
        # 1. Statewide query returns all members
        resp = await client.get("/api/admin/members", headers=headers_state)
        assert resp.status_code == HTTP_200_OK
        data = resp.json()
        assert data["total"] >= 5
        district_codes = {m["district_code"] for m in data["items"]}
        assert "KLKKD" in district_codes
        assert "KLEKM" in district_codes
        assert "KLTVC" in district_codes

        # 2. Filter by specific district succeeds
        resp_ekm = await client.get("/api/admin/members?unit_id=KLEKM", headers=headers_state)
        assert resp_ekm.status_code == HTTP_200_OK
        for item in resp_ekm.json()["items"]:
            assert item["district_code"] == "KLEKM"


@pytest.mark.asyncio
async def test_member_detail_and_id_viewing_audit():
    """
    FR7.5, FR7.8: Member detail view is role-scoped and ID viewing is audit-logged.
    """
    headers_kkd = {
        "X-Admin-Role": "district_admin",
        "X-Admin-Unit": "KLKKD",
        "X-Admin-Id": "admin_kkd_01",
    }
    headers_state = {
        "X-Admin-Role": "state_admin",
        "X-Admin-Unit": "KLSTATE",
        "X-Admin-Id": "state_gs",
    }

    async with AsyncTestClient(app=app) as client:
        # Kozhikode member ID
        kkd_member_id = "11111111-1111-1111-1111-111111111101"
        # Ernakulam member ID
        ekm_member_id = "11111111-1111-1111-1111-111111111103"

        # 1. KKD admin viewing KKD member succeeds
        res_kkd = await client.get(f"/api/admin/members/{kkd_member_id}", headers=headers_kkd)
        assert res_kkd.status_code == HTTP_200_OK
        assert res_kkd.json()["member"]["membership_number"] == "KLKKD000001"

        # 2. KKD admin viewing EKM member is forbidden
        res_ekm = await client.get(f"/api/admin/members/{ekm_member_id}", headers=headers_kkd)
        assert res_ekm.status_code == HTTP_403_FORBIDDEN

        # 3. State admin can view any member
        res_state = await client.get(f"/api/admin/members/{ekm_member_id}", headers=headers_state)
        assert res_state.status_code == HTTP_200_OK

        # 4. Check audit log for id_viewed
        audit_res = await client.get(
            "/api/admin/audit-logs?action=id_viewed", headers=headers_state
        )
        assert audit_res.status_code == HTTP_200_OK
        actions = [log["action"] for log in audit_res.json()["logs"]]
        assert "id_viewed" in actions


@pytest.mark.asyncio
async def test_suspend_reactivate_member_with_mandatory_reason():
    """
    FR7.5: Suspend or reactivate member requires recorded reason and is audit-logged.
    """
    headers_state = {
        "X-Admin-Role": "state_admin",
        "X-Admin-Unit": "KLSTATE",
        "X-Admin-Id": "state_gs",
    }
    target_id = "11111111-1111-1111-1111-111111111101"

    async with AsyncTestClient(app=app) as client:
        # 1. Status change without reason fails
        bad_req = await client.post(
            f"/api/admin/members/{target_id}/status",
            json={"status": "suspended", "reason": ""},
            headers=headers_state,
        )
        assert bad_req.status_code == HTTP_400_BAD_REQUEST

        # 2. Valid suspension succeeds
        res_suspend = await client.post(
            f"/api/admin/members/{target_id}/status",
            json={"status": "suspended", "reason": "Disciplinary review pending"},
            headers=headers_state,
        )
        assert res_suspend.status_code == HTTP_200_OK
        data = res_suspend.json()
        assert data["status"] == "suspended"
        assert data["reason"] == "Disciplinary review pending"

        # 3. Reactivation with reason succeeds
        res_reactivate = await client.post(
            f"/api/admin/members/{target_id}/status",
            json={"status": "active", "reason": "Review cleared by district committee"},
            headers=headers_state,
        )
        assert res_reactivate.status_code == HTTP_200_OK
        assert res_reactivate.json()["status"] == "active"


@pytest.mark.asyncio
async def test_csv_export_and_audit_trail():
    """
    FR7.3: Export to CSV records each export with user, time, and filters in audit log.
    """
    headers_state = {
        "X-Admin-Role": "state_admin",
        "X-Admin-Unit": "KLSTATE",
        "X-Admin-Id": "state_gs",
    }

    async with AsyncTestClient(app=app) as client:
        export_res = await client.get(
            "/api/admin/members/export?sector=food_delivery", headers=headers_state
        )
        assert export_res.status_code == HTTP_200_OK
        assert export_res.headers["content-type"] == "text/csv; charset=utf-8"
        csv_text = export_res.content.decode("utf-8")
        assert "Membership Number,Full Name,Phone,District" in csv_text
        assert "Com. Muhammed Basheer" in csv_text

        # Verify export was audit-logged
        audit_res = await client.get(
            "/api/admin/audit-logs?action=export_performed", headers=headers_state
        )
        assert audit_res.status_code == HTTP_200_OK
        logs = audit_res.json()["logs"]
        assert len(logs) > 0
        last_export = logs[-1]
        assert last_export["action"] == "export_performed"
        assert last_export["actor_id"] == "state_gs"


@pytest.mark.asyncio
async def test_master_data_permission_enforcement():
    """
    FR7.7: State office can manage master data (platforms, fees, contacts, WhatsApp).
    District admin is strictly forbidden from editing master data.
    """
    headers_kkd = {
        "X-Admin-Role": "district_admin",
        "X-Admin-Unit": "KLKKD",
        "X-Admin-Id": "admin_kkd_01",
    }
    headers_state = {
        "X-Admin-Role": "state_admin",
        "X-Admin-Unit": "KLSTATE",
        "X-Admin-Id": "state_gs",
    }

    async with AsyncTestClient(app=app) as client:
        # 1. District admin cannot update master data (403 Forbidden)
        res_forbidden = await client.patch(
            "/api/admin/master-data",
            json={"platforms": ["Swiggy", "Zomato", "NewPlatform"]},
            headers=headers_kkd,
        )
        assert res_forbidden.status_code == HTTP_403_FORBIDDEN

        # 2. State admin can update master data
        res_ok = await client.patch(
            "/api/admin/master-data",
            json={
                "whatsapp_links": {"KLKKD": "https://chat.whatsapp.com/UpdatedKozhikodeLink2026"},
            },
            headers=headers_state,
        )
        assert res_ok.status_code == HTTP_200_OK
        data = res_ok.json()
        assert (
            data["data"]["whatsapp_links"]["KLKKD"]
            == "https://chat.whatsapp.com/UpdatedKozhikodeLink2026"
        )


@pytest.mark.asyncio
async def test_summary_and_payment_reports():
    """
    FR7.4, FR7.6: Summary counts by district/sector, payment reconciliation, and refund tracking.
    """
    headers_state = {
        "X-Admin-Role": "state_admin",
        "X-Admin-Unit": "KLSTATE",
        "X-Admin-Id": "state_gs",
    }

    async with AsyncTestClient(app=app) as client:
        # Summary counts
        sum_res = await client.get("/api/admin/reports/summary", headers=headers_state)
        assert sum_res.status_code == HTTP_200_OK
        sdata = sum_res.json()
        assert sdata["total_members"] >= 5
        assert "food_delivery" in sdata["by_sector"]
        assert "Zomato" in sdata["by_platform"]

        # Payment report
        pay_res = await client.get("/api/admin/reports/payments", headers=headers_state)
        assert pay_res.status_code == HTTP_200_OK
        pdata = pay_res.json()
        assert pdata["total_collected"] > 0
        assert "admission_fee" in pdata["breakdown_by_fee"]
        assert "settled_amount" in pdata["reconciliation"]

        # Payment refund endpoint
        refund_res = await client.post(
            "/api/admin/payments/pay_test_001/refund",
            json="Accidental duplicate UPI entry",
            headers=headers_state,
        )
        assert refund_res.status_code == HTTP_200_OK
        assert refund_res.json()["status"] == "reversed"
