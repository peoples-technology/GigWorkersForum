import io

from PIL import Image, ImageOps


def process_selfie(image_bytes: bytes, max_dim: int = 800, quality: int = 85) -> bytes:
    """
    Process in-app live selfie photograph:
    1. Transpose orientation based on EXIF (if present) before stripping
    2. Strip all EXIF metadata for privacy & security
    3. Resize to max dimension (default 800px) maintaining aspect ratio
    4. Compress as clean JPEG
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Transpose according to EXIF orientation tag before stripping
    img = ImageOps.exif_transpose(img)

    # Convert to RGB if needed (e.g. RGBA from canvas or PNG)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Resize if larger than max_dim
    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    output = io.BytesIO()
    # Save without EXIF metadata
    img.save(output, format="JPEG", quality=quality, optimize=True)
    return output.getvalue()
