import csv
import io
import uuid
from datetime import UTC, datetime
from typing import Annotated

import msgspec
from litestar import Controller, Request, get, post
from litestar.exceptions import NotFoundException, PermissionDeniedException
from litestar.params import Body
from litestar.response import Response

from app.api.admin import get_admin_context
from app.core.import_processor import (
    _MOCK_IMPORT_JOBS,
    _MOCK_IMPORT_ROWS,
    BulkImportProcessor,
)


class DirectImportPayload(msgspec.Struct):
    filename: str = "paper_members_pilot.csv"
    rows: list[dict] = []


class ImportController(Controller):
    path = "/api/admin/import"

    @get("/template", status_code=200)
    async def download_template(self, request: Request) -> Response[bytes]:
        """
        Download bilingual CSV template for bulk paper import (FR10.2).
        Generated with all confirmed form fields + optional paid_up_to and receipt_no.
        """
        await get_admin_context(request)
        csv_bytes = BulkImportProcessor.generate_csv_template()
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="citu_bulk_import_template.csv"'},
            status_code=200,
        )

    @post(status_code=200)
    async def create_import_job(
        self,
        request: Request,
        data: Annotated[DirectImportPayload, Body()],
    ) -> dict:
        """
        Submit a bulk import file / rows (FR10.1).
        Enforces server-side district scoping (FR10.9), phone deduplication (FR10.4),
        masked Aadhaar (FR10.7), and audit logging (FR10.11).
        """
        ctx = await get_admin_context(request)

        job_id = str(uuid.uuid4())
        job_record = {
            "id": job_id,
            "admin_id": ctx.admin_id,
            "admin_role": ctx.role,
            "admin_unit_id": ctx.unit_id,
            "filename": data.filename,
            "status": "processing",
            "total_rows": len(data.rows),
            "accepted_rows": 0,
            "rejected_rows": 0,
            "skipped_rows": 0,
            "created_at": datetime.now(UTC).isoformat(),
            "completed_at": None,
        }
        _MOCK_IMPORT_JOBS[job_id] = job_record

        # Process rows
        summary = await BulkImportProcessor.process_import_rows(
            job_id=job_id,
            rows=data.rows,
            admin_id=ctx.admin_id,
            admin_role=ctx.role,
            admin_unit_id=ctx.unit_id,
        )

        return {
            "success": True,
            "job_id": job_id,
            "filename": data.filename,
            "status": summary["status"],
            "total_rows": summary["total_rows"],
            "accepted_rows": summary["accepted_rows"],
            "rejected_rows": summary["rejected_rows"],
            "skipped_rows": summary["skipped_rows"],
        }

    @get(status_code=200)
    async def list_import_jobs(self, request: Request) -> dict:
        """List bulk import jobs scoped by admin role."""
        ctx = await get_admin_context(request)

        jobs = list(_MOCK_IMPORT_JOBS.values())
        if ctx.is_district_admin:
            jobs = [j for j in jobs if j.get("admin_unit_id") == ctx.unit_id]

        return {"total": len(jobs), "jobs": jobs}

    @get("/{job_id:str}", status_code=200)
    async def get_import_job_status(self, request: Request, job_id: str) -> dict:
        """
        Get import job status and counts (FR10.10, FR10.12).
        """
        ctx = await get_admin_context(request)

        job = _MOCK_IMPORT_JOBS.get(job_id)
        if not job:
            raise NotFoundException("Import job not found")

        if ctx.is_district_admin and job.get("admin_unit_id") != ctx.unit_id:
            raise PermissionDeniedException(
                "District admin cannot view import jobs of another district"
            )

        return {"success": True, "job": job}

    @get("/{job_id:str}/report", status_code=200)
    async def download_import_report(self, request: Request, job_id: str) -> Response[bytes]:
        """
        Download CSV report detailing total, accepted, rejected with reasons, and skipped duplicates (FR10.10).
        """
        ctx = await get_admin_context(request)

        job = _MOCK_IMPORT_JOBS.get(job_id)
        if not job:
            raise NotFoundException("Import job not found")

        if ctx.is_district_admin and job.get("admin_unit_id") != ctx.unit_id:
            raise PermissionDeniedException(
                "District admin cannot access report of another district"
            )

        rows = _MOCK_IMPORT_ROWS.get(job_id, [])

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Row Number", "Phone", "Status", "Membership Number", "Reason / Notes"])

        for r in rows:
            writer.writerow(
                [
                    r.get("row"),
                    r.get("phone"),
                    r.get("status"),
                    r.get("membership_number", ""),
                    r.get("reason", ""),
                ]
            )

        csv_bytes = output.getvalue().encode("utf-8")
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="citu_import_report_{job_id}.csv"'
            },
            status_code=200,
        )
