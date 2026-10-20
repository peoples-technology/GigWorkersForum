import base64
import hashlib
import hmac
import secrets
import struct
import time

import argon2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Argon2id password hasher per FR8.1
_ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MB
    parallelism=4,
    hash_len=32,
    type=argon2.Type.ID,
)


def hash_password(password: str) -> str:
    """Hash password using argon2id."""
    return _ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against argon2id hash."""
    try:
        return _ph.verify(hashed, password)
    except (VerifyMismatchError, Exception):
        return False


# TOTP RFC 6238 Implementation for 2FA
def generate_totp_secret() -> str:
    """Generate a random base32 TOTP secret key."""
    random_bytes = secrets.token_bytes(20)
    return base64.b32encode(random_bytes).decode("utf-8").replace("=", "")


def get_totp_code(secret: str, time_step: int = 30, t0: int = 0) -> str:
    """Generate a 6-digit TOTP code for the current time step."""
    # Ensure proper base32 padding
    missing_padding = len(secret) % 8
    if missing_padding:
        secret += "=" * (8 - missing_padding)

    key = base64.b32decode(secret, casefold=True)
    counter = int((time.time() - t0) // time_step)
    msg = struct.pack(">Q", counter)

    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    code_int = struct.unpack(">I", h[offset : offset + 4])[0] & 0x7FFFFFFF
    code = code_int % 1000000
    return f"{code:06d}"


def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
    """Verify a TOTP code with an allowable clock skew window."""
    if not code or len(code) != 6 or not code.isdigit():
        return False

    missing_padding = len(secret) % 8
    if missing_padding:
        secret += "=" * (8 - missing_padding)

    try:
        key = base64.b32decode(secret, casefold=True)
    except Exception:
        return False

    current_counter = int(time.time() // 30)

    for offset in range(-window, window + 1):
        counter = current_counter + offset
        msg = struct.pack(">Q", counter)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        idx = h[-1] & 0x0F
        code_int = struct.unpack(">I", h[idx : idx + 4])[0] & 0x7FFFFFFF
        computed = f"{(code_int % 1000000):06d}"
        if hmac.compare_digest(computed, code):
            return True

    return False


def generate_recovery_codes(count: int = 8) -> list[str]:
    """Generate single-use backup recovery codes."""
    return [secrets.token_hex(4).upper() for _ in range(count)]
