"""
Stage 2 authentication & user management test suite.
Verifies PBKDF2 password security, authentication workflow, role authorization,
session management, brute-force protection, and first-run setup using temporary databases.
"""

import pytest
from pathlib import Path

from app.database import (
    initialize_database,
    create_user,
    get_user_by_username,
    get_user_by_id,
    update_user_status,
)
from app.auth import (
    hash_password,
    verify_password,
    login,
    logout,
    change_password,
    is_first_run,
    setup_first_admin,
    get_session,
    get_protector,
)


@pytest.fixture
def auth_db_path(tmp_path: Path) -> Path:
    """Fixture providing a fresh temporary database with clear session and protector state."""
    db_file = tmp_path / "test_auth.db"
    initialize_database(db_file)
    get_session().clear_session()
    # Reset protector limits for tests
    protector = get_protector()
    protector._attempts.clear()
    return db_file


# 1. Password hashing works
def test_password_hashing():
    pw = "SecretPassword123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert hashed.startswith("pbkdf2:sha256:100000$")


# 2. Password verification succeeds for correct password
def test_password_verification_success():
    pw = "CorrectPassword123"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True


# 3. Incorrect password is rejected
def test_password_verification_failure():
    pw = "CorrectPassword123"
    hashed = hash_password(pw)
    assert verify_password("WrongPassword123", hashed) is False
    assert verify_password("", hashed) is False


# 4. Plaintext password is never stored
def test_plaintext_password_not_stored(auth_db_path: Path):
    pw = "MySecurePassword99"
    hashed = hash_password(pw)
    user = create_user("testuser_plain", hashed, role="teacher", db_path=auth_db_path)
    
    db_user = get_user_by_username("testuser_plain", db_path=auth_db_path)
    assert db_user["password_hash"] != pw
    assert db_user["password_hash"] == hashed


# 5. User creation works
def test_user_creation(auth_db_path: Path):
    hashed = hash_password("Password123")
    user = create_user("teacher_alice", hashed, role="teacher", db_path=auth_db_path)
    assert user["id"] is not None
    assert user["username"] == "teacher_alice"
    assert user["role"] == "teacher"


# 6. Duplicate username is rejected
def test_duplicate_username_rejected(auth_db_path: Path):
    hashed = hash_password("Password123")
    create_user("teacher_bob", hashed, role="teacher", db_path=auth_db_path)
    
    with pytest.raises(ValueError, match="already exists"):
        create_user("teacher_bob", hashed, role="teacher", db_path=auth_db_path)


# 7. User lookup works by username and ID
def test_user_lookup(auth_db_path: Path):
    hashed = hash_password("Password123")
    created = create_user("teacher_charlie", hashed, role="teacher", db_path=auth_db_path)
    
    by_name = get_user_by_username("teacher_charlie", db_path=auth_db_path)
    by_id = get_user_by_id(created["id"], db_path=auth_db_path)
    
    assert by_name is not None
    assert by_id is not None
    assert by_name["id"] == created["id"]
    assert by_id["username"] == "teacher_charlie"


# 8. Login succeeds with valid credentials
def test_login_success(auth_db_path: Path):
    hashed = hash_password("ValidPassword123")
    create_user("teacher_david", hashed, role="teacher", db_path=auth_db_path)
    
    logged_user = login("teacher_david", "ValidPassword123", db_path=auth_db_path)
    assert logged_user["username"] == "teacher_david"
    assert "password_hash" not in logged_user
    
    session = get_session()
    assert session.is_logged_in() is True
    assert session.get_current_username() == "teacher_david"


# 9. Login fails with invalid credentials
def test_login_failure(auth_db_path: Path):
    hashed = hash_password("ValidPassword123")
    create_user("teacher_eve", hashed, role="teacher", db_path=auth_db_path)
    
    with pytest.raises(ValueError, match="Invalid username or password"):
        login("teacher_eve", "WrongPassword123", db_path=auth_db_path)
    
    with pytest.raises(ValueError, match="Invalid username or password"):
        login("nonexistent_user", "ValidPassword123", db_path=auth_db_path)


# 10. Inactive users cannot log in
def test_inactive_user_login_prevented(auth_db_path: Path):
    hashed = hash_password("Password123")
    user = create_user("teacher_frank", hashed, role="teacher", db_path=auth_db_path)
    update_user_status(user["id"], "inactive", db_path=auth_db_path)
    
    with pytest.raises(ValueError, match="Account is inactive"):
        login("teacher_frank", "Password123", db_path=auth_db_path)


# 11. Role checking works
def test_role_checking(auth_db_path: Path):
    hashed = hash_password("AdminPass123")
    admin_user = create_user("admin_grace", hashed, role="admin", db_path=auth_db_path)
    
    login("admin_grace", "AdminPass123", db_path=auth_db_path)
    session = get_session()
    
    assert session.has_role("admin") is True
    assert session.has_role("teacher") is True  # Admin inherits teacher capabilities
    
    logout()
    
    teacher_user = create_user("teacher_hank", hashed, role="teacher", db_path=auth_db_path)
    login("teacher_hank", "AdminPass123", db_path=auth_db_path)
    
    assert session.has_role("teacher") is True
    assert session.has_role("admin") is False


# 12. Logout clears session
def test_logout_clears_session(auth_db_path: Path):
    hashed = hash_password("Password123")
    create_user("teacher_iris", hashed, role="teacher", db_path=auth_db_path)
    
    login("teacher_iris", "Password123", db_path=auth_db_path)
    session = get_session()
    assert session.is_logged_in() is True
    
    logout()
    assert session.is_logged_in() is False
    assert session.get_current_user() is None


# 13. Password change works
def test_password_change(auth_db_path: Path):
    hashed = hash_password("OldPassword123")
    user = create_user("teacher_jack", hashed, role="teacher", db_path=auth_db_path)
    
    result = change_password(user["id"], "OldPassword123", "NewPassword456", db_path=auth_db_path)
    assert result is True


# 14. Old password no longer works after password change
def test_old_password_invalidated(auth_db_path: Path):
    hashed = hash_password("OldPassword123")
    user = create_user("teacher_karen", hashed, role="teacher", db_path=auth_db_path)
    
    change_password(user["id"], "OldPassword123", "NewPassword456", db_path=auth_db_path)
    
    # Login with old password fails
    with pytest.raises(ValueError, match="Invalid username or password"):
        login("teacher_karen", "OldPassword123", db_path=auth_db_path)
        
    # Login with new password succeeds
    login("teacher_karen", "NewPassword456", db_path=auth_db_path)
    assert get_session().is_logged_in() is True


# 15. Failed-login brute-force protection works
def test_brute_force_lockout(auth_db_path: Path):
    hashed = hash_password("RealPassword123")
    create_user("target_user", hashed, role="teacher", db_path=auth_db_path)
    
    # 4 failed attempts
    for _ in range(4):
        with pytest.raises(ValueError, match="Invalid username or password"):
            login("target_user", "WrongPass", db_path=auth_db_path)
            
    # 5th attempt triggers lockout
    with pytest.raises(ValueError, match="locked"):
        login("target_user", "WrongPass", db_path=auth_db_path)
        
    # Even correct password is blocked while locked out
    with pytest.raises(ValueError, match="locked"):
        login("target_user", "RealPassword123", db_path=auth_db_path)


# 16. First-user setup works
def test_first_user_setup(auth_db_path: Path):
    assert is_first_run(db_path=auth_db_path) is True
    
    admin = setup_first_admin("sysadmin", "SuperAdminPass123", db_path=auth_db_path)
    assert admin["username"] == "sysadmin"
    assert admin["role"] == "admin"
    assert is_first_run(db_path=auth_db_path) is False
    
    # Second call fails
    with pytest.raises(ValueError, match="already been completed"):
        setup_first_admin("anotheradmin", "Password123", db_path=auth_db_path)
