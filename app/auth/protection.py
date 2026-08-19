"""
Brute-force protection and failed login attempt tracking for AI-Enabled Smart Attendance System.
Implements temporary lockouts after consecutive failed authentication attempts.
"""

import time
from typing import Dict, Tuple

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 30


class LoginProtector:
    """Tracks failed login attempts per username and enforces temporary lockouts."""

    def __init__(
        self,
        max_attempts: int = MAX_FAILED_ATTEMPTS,
        lockout_duration: int = LOCKOUT_DURATION_SECONDS,
    ):
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        # Dict[username, Tuple[failed_count, lockout_until_timestamp]]
        self._attempts: Dict[str, Tuple[int, float]] = {}

    def is_locked_out(self, username: str) -> Tuple[bool, int]:
        """
        Check if a username is currently locked out due to repeated failed logins.
        
        :param username: Username to check.
        :return: Tuple of (is_locked: bool, remaining_seconds: int)
        """
        username = (username or "").strip().lower()
        if not username or username not in self._attempts:
            return False, 0

        failed_count, lockout_until = self._attempts[username]
        now = time.time()

        if now < lockout_until:
            remaining = int(lockout_until - now) + 1
            return True, remaining
        elif failed_count >= self.max_attempts and now >= lockout_until:
            # Lockout period expired; reset counters
            del self._attempts[username]
            return False, 0

        return False, 0

    def record_failed_attempt(self, username: str) -> Tuple[int, bool]:
        """
        Record a failed authentication attempt for a username.
        
        :param username: Username of failed attempt.
        :return: Tuple of (current_failed_count: int, is_now_locked_out: bool)
        """
        username = (username or "").strip().lower()
        if not username:
            return 0, False

        failed_count, lockout_until = self._attempts.get(username, (0, 0.0))
        now = time.time()

        # If previous lockout expired, reset
        if lockout_until > 0 and now >= lockout_until:
            failed_count = 0
            lockout_until = 0.0

        failed_count += 1

        if failed_count >= self.max_attempts:
            lockout_until = now + self.lockout_duration
            self._attempts[username] = (failed_count, lockout_until)
            return failed_count, True
        else:
            self._attempts[username] = (failed_count, 0.0)
            return failed_count, False

    def reset_attempts(self, username: str) -> None:
        """Reset failed attempt counters upon successful authentication."""
        username = (username or "").strip().lower()
        if username in self._attempts:
            del self._attempts[username]


# Global protector instance
_protector = LoginProtector()


def get_protector() -> LoginProtector:
    """Return default LoginProtector instance."""
    return _protector
