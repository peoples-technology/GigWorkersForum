import os
import secrets
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import get_settings

settings = get_settings()


# 256-bit AES-GCM key derived or loaded from SECRET_KEY
def _get_encryption_key() -> bytes:
    key_material = settings.SECRET_KEY.encode("utf-8")
    if len(key_material) < 32:
        key_material = key_material.ljust(32, b"0")
    return key_material[:32]


def save_encrypted_document(
    file_bytes: bytes,
    filename_prefix: str = "id_proof",
) -> str:
    """
    Encrypt document bytes via AES-256-GCM and store outside web root.
    Returns relative safe file path.
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    aesgcm = AESGCM(_get_encryption_key())
    nonce = secrets.token_bytes(12)  # 96-bit nonce for AES-GCM
    encrypted_data = aesgcm.encrypt(nonce, file_bytes, None)

    # Store: [12-byte nonce] + [ciphertext + 16-byte tag]
    payload = nonce + encrypted_data

    random_name = f"{filename_prefix}_{secrets.token_hex(16)}.enc"
    safe_path = upload_dir / random_name

    with open(safe_path, "wb") as f:
        f.write(payload)

    return str(safe_path)


def read_encrypted_document(file_path: str) -> bytes:
    """
    Read and decrypt document bytes using AES-256-GCM.
    Raises ValueError if decryption or authentication tag fails.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "rb") as f:
        payload = f.read()

    if len(payload) < 28:  # 12 nonce + 16 tag minimum
        raise ValueError("Corrupted encrypted file")

    nonce = payload[:12]
    ciphertext = payload[12:]

    aesgcm = AESGCM(_get_encryption_key())
    return aesgcm.decrypt(nonce, ciphertext, None)
