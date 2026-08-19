"""
Password security and hashing utilities for AI-Enabled Smart Attendance System.
Uses NIST-recommended PBKDF2-HMAC-SHA256 with cryptographically random salt.
"""

import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2:sha256"
ITERATIONS = 100000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using PBKDF2-HMAC-SHA256.
    
    :param password: Plaintext password string.
    :return: Formatted hash string 'pbkdf2:sha256:100000$<salt_hex>$<hash_hex>'
    :raises ValueError: If password is empty or invalid.
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string.")

    salt = secrets.token_bytes(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS,
    )
    return f"{ALGORITHM}:{ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored PBKDF2 hash.
    
    :param password: Plaintext password to test.
    :param hashed_password: Formatted hash string from database.
    :return: True if password matches, False otherwise.
    """
    if not password or not hashed_password or not isinstance(password, str) or not isinstance(hashed_password, str):
        return False

    try:
        parts = hashed_password.split("$")
        if len(parts) != 3:
            return False
        header, salt_hex, hash_hex = parts
        
        header_parts = header.split(":")
        if len(header_parts) != 3:
            return False
        scheme, digest, iterations_str = header_parts

        if f"{scheme}:{digest}" != ALGORITHM:
            return False

        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)

        derived = hashlib.pbkdf2_hmac(
            digest,
            password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(derived, expected_hash)
    except Exception:
        return False
