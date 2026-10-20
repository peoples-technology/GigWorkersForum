import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RateLimitBucket:
    timestamps: list[float] = field(default_factory=list)
    last_request: float = 0.0


class RateLimiter:
    def __init__(self):
        self._phone_buckets: dict[str, RateLimitBucket] = defaultdict(RateLimitBucket)
        self._ip_buckets: dict[str, RateLimitBucket] = defaultdict(RateLimitBucket)
        self._failed_logins: dict[str, list[float]] = defaultdict(list)

    def check_otp_rate_limit(
        self,
        phone: str,
        ip: str,
        cooldown_seconds: int = 45,
        max_per_phone: int = 3,
        phone_window_seconds: int = 600,
        max_per_ip: int = 10,
        ip_window_seconds: int = 600,
    ) -> tuple[bool, str | None]:
        """Check if an OTP request is allowed by phone & IP limits and cooldown."""
        now = time.time()

        # 1. Check cooldown per phone
        phone_bucket = self._phone_buckets[phone]
        if phone_bucket.last_request > 0:
            elapsed = now - phone_bucket.last_request
            if elapsed < cooldown_seconds:
                remaining = int(cooldown_seconds - elapsed)
                return (
                    False,
                    f"Please wait {remaining}s before requesting a new OTP / ദയവായി കാത്തിരിക്കുക",
                )

        # 2. Check window limits for phone
        phone_bucket.timestamps = [
            t for t in phone_bucket.timestamps if now - t < phone_window_seconds
        ]
        if len(phone_bucket.timestamps) >= max_per_phone:
            return False, "Too many OTP requests for this phone number. Try again later."

        # 3. Check window limits for IP
        ip_bucket = self._ip_buckets[ip]
        ip_bucket.timestamps = [t for t in ip_bucket.timestamps if now - t < ip_window_seconds]
        if len(ip_bucket.timestamps) >= max_per_ip:
            return False, "Too many requests from this IP address. Try again later."

        # Record request
        phone_bucket.timestamps.append(now)
        phone_bucket.last_request = now
        ip_bucket.timestamps.append(now)
        return True, None

    def record_login_attempt(
        self, identity: str, success: bool, max_failures: int = 5, lock_duration: int = 900
    ) -> tuple[bool, str | None]:
        """Track failed login attempts to lock out brute-force attacks."""
        now = time.time()
        attempts = self._failed_logins[identity]

        # Purge old attempts
        self._failed_logins[identity] = [t for t in attempts if now - t < lock_duration]

        if len(self._failed_logins[identity]) >= max_failures:
            return False, "Account locked due to too many failed attempts. Try in 15 mins."

        if not success:
            self._failed_logins[identity].append(now)
        else:
            self._failed_logins[identity].clear()

        return True, None


# Global instance
limiter = RateLimiter()
