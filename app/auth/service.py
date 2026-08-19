"""
Authentication Service for AI-Enabled Smart Attendance System.
Handles login verification, session initialization, password changes, and first-run admin setup.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from app.database import (
    create_user,
    get_user_by_username,
    get_user_by_id,
    update_user_password,
    count_users,
)
from app.auth.password import hash_password, verify_password
from app.auth.session import get_session
from app.auth.protection import get_protector

logger = logging.getLogger(__name__)

MIN_PASSWORD_LENGTH = 6


def is_first_run(db_path: Optional[Union[str, Path]] = None) -> bool:
    """Return True if no user accounts exist in the database."""
    return count_users(db_path=db_path) == 0


def setup_first_admin(
    username: str,
    password: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Perform first-run setup to create initial administrator account.
    
    :raises ValueError: If setup already completed or invalid credentials.
    """
    if not is_first_run(db_path=db_path):
        raise ValueError("First-run setup has already been completed.")

    username = (username or "").strip()
    password = (password or "").strip()

    if not username:
        raise ValueError("Admin username cannot be empty.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

    pw_hash = hash_password(password)
    user = create_user(username, pw_hash, role="admin", db_path=db_path)
    logger.info(f"First-run admin account '{username}' created successfully.")
    
    # Return user without password_hash
    safe_user = dict(user)
    safe_user.pop("password_hash", None)
    return safe_user


def login(
    username: str,
    password: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Authenticate user login credentials and initialize session.
    
    :raises ValueError: If authentication fails, account inactive, or locked out.
    """
    username = (username or "").strip()
    password = (password or "").strip()

    if not username or not password:
        raise ValueError("Username and password are required.")

    protector = get_protector()

    # Brute-force protection check
    locked, remaining = protector.is_locked_out(username)
    if locked:
        raise ValueError(f"Account temporarily locked due to failed attempts. Try again in {remaining} seconds.")

    user = get_user_by_username(username, db_path=db_path)
    if not user:
        protector.record_failed_attempt(username)
        raise ValueError("Invalid username or password.")

    # Account status check
    if user.get("status", "active").lower() != "active":
        raise ValueError("Account is inactive. Please contact system administrator.")

    # Password verification
    if not verify_password(password, user["password_hash"]):
        cnt, locked_now = protector.record_failed_attempt(username)
        if locked_now:
            raise ValueError(f"Too many failed login attempts. Account locked for 30 seconds.")
        raise ValueError("Invalid username or password.")

    # Success: reset failed attempt counter and start session
    protector.reset_attempts(username)
    session = get_session()
    session.start_session(user)

    logger.info(f"User '{username}' logged in successfully.")
    
    safe_user = dict(user)
    safe_user.pop("password_hash", None)
    return safe_user


def logout() -> None:
    """Terminate active user session."""
    session = get_session()
    username = session.get_current_username()
    session.clear_session()
    if username:
        logger.info(f"User '{username}' logged out.")


def change_password(
    user_id: int,
    old_password: str,
    new_password: str,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    """
    Change user password after verifying current password.
    
    :raises ValueError: If verification fails or new password invalid.
    """
    old_password = (old_password or "").strip()
    new_password = (new_password or "").strip()

    user = get_user_by_id(user_id, db_path=db_path)
    if not user:
        raise ValueError("User does not exist.")

    if not verify_password(old_password, user["password_hash"]):
        raise ValueError("Current password is incorrect.")

    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"New password must be at least {MIN_PASSWORD_LENGTH} characters long.")

    new_hash = hash_password(new_password)
    success = update_user_password(user_id, new_hash, db_path=db_path)
    if success:
        logger.info(f"Password changed successfully for user ID {user_id}.")
    return success
