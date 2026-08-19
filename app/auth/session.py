"""
Local application session management for AI-Enabled Smart Attendance System.
Tracks logged-in state, active user identity, and role authorization safely in memory.
"""

from typing import Any, Dict, Optional, Set

VALID_ROLES: Set[str] = {"admin", "teacher"}


class SessionManager:
    """In-memory session manager for local desktop application context."""

    def __init__(self):
        self._current_user: Optional[Dict[str, Any]] = None

    def start_session(self, user: Dict[str, Any]) -> None:
        """
        Initialize active session for authenticated user.
        
        :param user: Dictionary containing user fields (id, username, role).
        """
        role = (user.get("role") or "").strip().lower()
        self._current_user = {
            "user_id": user["id"],
            "username": user["username"],
            "role": role if role in VALID_ROLES else "teacher",
            "status": user.get("status", "active"),
        }

    def clear_session(self) -> None:
        """Clear active user session on logout."""
        self._current_user = None

    def is_logged_in(self) -> bool:
        """Return True if an active user session exists."""
        return self._current_user is not None

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Return copy of active user session dict or None."""
        if self._current_user:
            return dict(self._current_user)
        return None

    def get_current_username(self) -> Optional[str]:
        """Return username of active user session or None."""
        if self._current_user:
            return self._current_user.get("username")
        return None

    def get_current_role(self) -> Optional[str]:
        """Return role of active user session or None."""
        if self._current_user:
            return self._current_user.get("role")
        return None

    def has_role(self, required_role: str) -> bool:
        """
        Check if active user has the required role (or admin status).
        
        :param required_role: Role name to verify ('admin', 'teacher').
        :return: True if authorized.
        """
        if not self.is_logged_in():
            return False
        current_role = self.get_current_role()
        if current_role == "admin":
            return True
        return current_role == required_role.strip().lower()


# Global active session instance
_session = SessionManager()


def get_session() -> SessionManager:
    """Return active session instance."""
    return _session
