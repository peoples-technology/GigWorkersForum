import io

import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND
from litestar.testing import AsyncTestClient
from PIL import Image

from app.core.card_renderer import render_membership_card_image, render_membership_card_pdf
from app.core.qr_generator import (
    generate_opaque_card_token,
    generate_verification_qr_data_uri,
    generate_verification_qr_png_bytes,
    generate_verification_qr_svg,
)
from app.main import app


def test_opaque_token_generation():
    """FR4.3: QR code must encode an opaque random token, never sequential ID or private data."""
    t1 = generate_opaque_card_token()
    t2 = generate_opaque_card_token()
    assert len(t1) >= 32
    assert t1 != t2
    # Ensure URL safe characters
    assert all(c.isalnum() or c in "-_" for c in t1)


def test_qr_generation():
    """FR4.2: Segno QR generation outputs valid SVG and PNG formats."""
    token = generate_opaque_card_token()

    svg_str = generate_verification_qr_svg(token)
    assert "<svg" in svg_str
    assert "</svg>" in svg_str

    png_bytes = generate_verification_qr_png_bytes(token)
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    data_uri = generate_verification_qr_data_uri(token)
    assert data_uri.startswith("data:image/png;base64,")


def test_card_image_and_pdf_rendering():
    """FR4.2: Typst/Pillow card generator renders valid PNG and PDF outputs."""
    token = generate_opaque_card_token()

    png_bytes = render_membership_card_image(
        member_name="Com. Sakhavu Krishnan",
        membership_number="KLEKM000042",
        district_name="Ernakulam",
        primary_platform="Swiggy",
        valid_thru="April 2027",
        token=token,
    )
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    # Verify PNG is readable by PIL
    img = Image.open(io.BytesIO(png_bytes))
    assert img.size == (1012, 638)

    pdf_bytes = render_membership_card_pdf(
        member_name="Com. Sakhavu Krishnan",
        membership_number="KLEKM000042",
        district_name="Ernakulam",
        primary_platform="Swiggy",
        valid_thru="April 2027",
        token=token,
    )
    assert pdf_bytes.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_card_preview_and_downloads():
    """FR4.2: Cards controller preview, image download, and PDF download endpoints."""
    async with AsyncTestClient(app=app) as client:
        # Preview
        preview_res = await client.get("/api/cards/member/test-mem-01/preview")
        assert preview_res.status_code == HTTP_200_OK
        pdata = preview_res.json()
        assert pdata["success"] is True
        card = pdata["card"]
        assert "membership_number" in card
        assert card["status"] == "active"
        assert card["qr_data_uri"].startswith("data:image/png;base64,")

        # Download PNG
        img_res = await client.get("/api/cards/member/test-mem-01/download/image")
        assert img_res.status_code == HTTP_200_OK
        assert img_res.headers["content-type"] == "image/png"
        assert img_res.content.startswith(b"\x89PNG\r\n\x1a\n")
        assert "attachment" in img_res.headers.get("content-disposition", "")

        # Download PDF
        pdf_res = await client.get("/api/cards/member/test-mem-01/download/pdf")
        assert pdf_res.status_code == HTTP_200_OK
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert pdf_res.content.startswith(b"%PDF")
        assert "attachment" in pdf_res.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_reissue_card_token():
    """FR4.4: Card token reissuance revokes existing token and generates new token."""
    async with AsyncTestClient(app=app) as client:
        # Initial preview to populate memory token
        p_res = await client.get("/api/cards/member/test-reissue-01/preview")
        assert p_res.status_code == HTTP_200_OK
        initial_token = p_res.json()["card"]["token"]

        # Reissue request
        reissue_res = await client.post(
            "/api/cards/reissue",
            json={
                "member_id": "test-reissue-01",
                "reason": "Lost physical card copy",
                "admin_id": "admin_ekm_01",
            },
        )
        assert reissue_res.status_code == HTTP_200_OK
        rdata = reissue_res.json()
        assert rdata["success"] is True
        new_token = rdata["new_token"]
        assert new_token != initial_token


@pytest.mark.asyncio
async def test_public_verification_privacy_and_security():
    """
    FR4.3: Public verification endpoint (/verify/{token}):
    - Zero auth required
    - Returns ONLY safe public fields: {name, number, district, status, union}
    - NEVER leaks phone, aadhaar, address, or payment records
    - Handles revoked tokens and invalid tokens safely
    """
    async with AsyncTestClient(app=app) as client:
        # Valid test token
        resp = await client.get("/verify/test_valid_worker_token")
        assert resp.status_code == HTTP_200_OK
        data = resp.json()
        assert data["valid"] is True
        assert data["membership_number"] == "KLTVC000001"
        assert "Com. Rahul Krishnan" in data["name"]
        assert data["district"] == "Thiruvananthapuram"
        assert data["status"] == "active"
        assert "Kerala State Gig & Platform Workers Union (CITU)" in data["union"]

        # CRITICAL PRIVACY ASSERTIONS (DPDP Act Compliance)
        assert "phone" not in data
        assert "aadhaar" not in data
        assert "masked_aadhaar" not in data
        assert "payment" not in data
        assert "amount" not in data
        assert "address" not in data
        assert "bank" not in data

        # Revoked test token
        revoked_resp = await client.get("/verify/test_revoked_worker_token")
        assert revoked_resp.status_code == HTTP_200_OK
        revoked_data = revoked_resp.json()
        assert revoked_data["valid"] is False
        assert revoked_data["status"] == "revoked"

        # Invalid token returns 404
        bad_resp = await client.get("/verify/totally_invalid_nonexistent_token_12345")
        assert bad_resp.status_code == HTTP_404_NOT_FOUND
