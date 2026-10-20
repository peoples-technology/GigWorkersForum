import base64
import io
import secrets

import segno


def generate_opaque_card_token() -> str:
    """Generate a random 32-character opaque URL-safe token (FR4.3)."""
    return secrets.token_urlsafe(32)


def generate_verification_qr_svg(
    token: str,
    base_url: str = "https://gigworkers.citu.org.in",
    scale: int = 4,
) -> str:
    """Generate an SVG string for the QR code encoding the public verify URL."""
    verify_url = f"{base_url.rstrip('/')}/verify/{token}"
    qr = segno.make(verify_url, error="m")
    out = io.BytesIO()
    qr.save(out, kind="svg", scale=scale, dark="#1E293B", light="#FFFFFF")
    return out.getvalue().decode("utf-8")


def generate_verification_qr_png_bytes(
    token: str,
    base_url: str = "https://gigworkers.citu.org.in",
    scale: int = 5,
) -> bytes:
    """Generate PNG bytes for the QR code."""
    verify_url = f"{base_url.rstrip('/')}/verify/{token}"
    qr = segno.make(verify_url, error="m")
    out = io.BytesIO()
    qr.save(out, kind="png", scale=scale, dark="#1E293B", light="#FFFFFF")
    return out.getvalue()


def generate_verification_qr_data_uri(
    token: str,
    base_url: str = "https://gigworkers.citu.org.in",
) -> str:
    """Generate a base64 Data URI string for direct embedding in HTML/CSS."""
    png_bytes = generate_verification_qr_png_bytes(token, base_url=base_url)
    b64_str = base64.b64encode(png_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"
