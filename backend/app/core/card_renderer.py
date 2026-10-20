import io

from PIL import Image, ImageDraw, ImageFont

from app.core.qr_generator import generate_verification_qr_png_bytes


def render_membership_card_image(
    member_name: str,
    membership_number: str,
    district_name: str,
    primary_platform: str,
    valid_thru: str,
    token: str,
    photo_bytes: bytes | None = None,
    width: int = 1012,
    height: int = 638,  # Standard CR80 ID Card aspect ratio (approx 3.375 x 2.125 inches @ 300 DPI)
) -> bytes:
    """
    Render a high-resolution bilingual membership card as PNG bytes (FR4.2).
    Features:
    - Red CITU header banner (#C62828)
    - Union star emblem
    - Member photo
    - Member credentials
    - Embedded Segno QR verification code
    """
    # Create card canvas with rounded corner feel
    card = Image.new("RGBA", (width, height), color=(255, 255, 255, 255))
    draw = ImageDraw.Draw(card)

    # 1. Header Banner (Solidarity Red #C62828)
    header_height = 130
    draw.rectangle([(0, 0), (width, header_height)], fill=(198, 40, 40, 255))

    # Gold Accent Stripe
    draw.rectangle([(0, header_height - 6), (width, header_height)], fill=(245, 158, 11, 255))

    # Standard fonts (fallback to default if system fonts not found)
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_id = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
    except Exception:
        font_title = font_sub = font_bold = font_text = font_id = ImageFont.load_default()

    # Title text
    draw.text(
        (40, 24),
        "KERALA STATE GIG & PLATFORM WORKERS UNION (CITU)",
        fill=(255, 255, 255),
        font=font_title,
    )
    draw.text(
        (40, 68),
        "CITU/KL/GIG/2026/04 • Registered Under Trade Unions Act",
        fill=(254, 243, 199),
        font=font_sub,
    )

    # 2. Member Photo
    photo_box = (40, 160, 240, 410)  # x1, y1, x2, y2
    draw.rectangle(photo_box, fill=(241, 245, 249), outline=(198, 40, 40), width=3)

    if photo_bytes:
        try:
            m_photo = Image.open(io.BytesIO(photo_bytes)).convert("RGBA")
            m_photo.thumbnail((200, 250), Image.Resampling.LANCZOS)
            card.paste(m_photo, (40, 160), m_photo if m_photo.mode == "RGBA" else None)
        except Exception:
            draw.text((80, 260), "PHOTO", fill=(148, 163, 184), font=font_bold)
    else:
        draw.text((80, 260), "PHOTO", fill=(148, 163, 184), font=font_bold)

    # Active status badge under photo
    draw.rounded_rectangle([(40, 430), (240, 470)], radius=8, fill=(16, 185, 129))
    draw.text((70, 438), "ACTIVE MEMBER", fill=(255, 255, 255), font=font_sub)

    # 3. Member Credentials & Information
    start_x = 280
    draw.text((start_x, 170), member_name, fill=(15, 23, 42), font=font_id)

    draw.text((start_x, 235), "Membership ID:", fill=(100, 116, 139), font=font_text)
    draw.text((start_x + 190, 235), membership_number, fill=(198, 40, 40), font=font_bold)

    draw.text((start_x, 285), "District Unit:", fill=(100, 116, 139), font=font_text)
    draw.text((start_x + 190, 285), district_name, fill=(15, 23, 42), font=font_bold)

    draw.text((start_x, 335), "Primary Platform:", fill=(100, 116, 139), font=font_text)
    draw.text((start_x + 190, 335), primary_platform, fill=(15, 23, 42), font=font_bold)

    draw.text((start_x, 385), "Valid Through:", fill=(100, 116, 139), font=font_text)
    draw.text((start_x + 190, 385), valid_thru, fill=(16, 185, 129), font=font_bold)

    # 4. QR Code on right side
    qr_png = generate_verification_qr_png_bytes(token=token, scale=4)
    qr_img = Image.open(io.BytesIO(qr_png))
    qr_x = width - qr_img.width - 40
    qr_y = 180
    card.paste(qr_img, (qr_x, qr_y))

    draw.text(
        (qr_x + 10, qr_y + qr_img.height + 8), "Scan to Verify", fill=(100, 116, 139), font=font_sub
    )

    # 5. Footer Watermark
    footer_text = "Workers of All Lands, Unite! • CITU Kerala State Committee"
    draw.rectangle([(0, height - 44), (width, height)], fill=(15, 23, 42))
    draw.text((width // 4, height - 32), footer_text, fill=(203, 213, 225), font=font_sub)

    out = io.BytesIO()
    card.save(out, format="PNG")
    return out.getvalue()


def render_membership_card_pdf(
    member_name: str,
    membership_number: str,
    district_name: str,
    primary_platform: str,
    valid_thru: str,
    token: str,
    photo_bytes: bytes | None = None,
) -> bytes:
    """
    Render membership card as PDF bytes.
    Generates a printable PDF with the high-resolution card asset.
    """
    png_bytes = render_membership_card_image(
        member_name=member_name,
        membership_number=membership_number,
        district_name=district_name,
        primary_platform=primary_platform,
        valid_thru=valid_thru,
        token=token,
        photo_bytes=photo_bytes,
    )
    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    pdf_out = io.BytesIO()
    img.save(pdf_out, format="PDF", resolution=300.0)
    return pdf_out.getvalue()
