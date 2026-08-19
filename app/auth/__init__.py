"""
Authentication package for AI-Enabled Smart Attendance System.
Exposes password hashing, session management, brute-force protection, and authentication services.
"""

from app.auth.password import hash_password, verify_password
from app.auth.session import get_session, SessionManager
from app.auth.protection import get_protector, LoginProtector
from app.auth.service import (
    is_first_run,
    setup_first_admin,
    login,
    logout,
    change_password,
)

__all__ = [
    "hash_password",
    "verify_password",
    "get_session",
    "SessionManager",
    "get_protector",
    "LoginProtector",
    "is_first_run",
    "setup_first_admin",
    "login",
    "logout",
    "change_password",
]
