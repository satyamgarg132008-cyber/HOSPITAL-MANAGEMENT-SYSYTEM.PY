"""
=============================================================================
MEDNOVA AI — INTELLIGENT HOSPITAL MANAGEMENT SYSTEM
Module: security.py
Description: Cryptographic password hashing (PBKDF2-HMAC-SHA256), authentication
             verification, and active user session state management.
=============================================================================
"""

import hashlib
import secrets
from typing import Optional, Tuple
import config


def generate_salt() -> str:
    """Generate a secure cryptographic 16-byte random hex salt."""
    return secrets.token_hex(16)


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hash a plain-text password using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    
    Args:
        password: Plain text password string.
        salt: Optional existing hex salt. If None, a new random salt is generated.
        
    Returns:
        Tuple of (hex_digest_hash, hex_salt)
    """
    if salt is None:
        salt = generate_salt()
        
    salt_bytes = bytes.fromhex(salt)
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt_bytes,
        100000
    )
    return hash_bytes.hex(), salt


def verify_password(plain_password: str, stored_hash: str, stored_salt: str) -> bool:
    """
    Verify whether the provided plain-text password matches the stored cryptographic hash.
    Uses secrets.compare_digest to prevent side-channel timing attacks.
    """
    try:
        calculated_hash, _ = hash_password(plain_password, stored_salt)
        return secrets.compare_digest(calculated_hash, stored_hash)
    except Exception:
        return False


class UserSession:
    """
    Singleton session container holding information about the currently logged-in user.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance.clear()
        return cls._instance

    def set_user(self, user_id: int, username: str, full_name: str, role: str, email: str = ""):
        """Store authenticated user session."""
        self.user_id = user_id
        self.username = username
        self.full_name = full_name
        self.role = role
        self.email = email
        self.is_authenticated = True

    def clear(self):
        """Clear user session upon logout."""
        self.user_id = None
        self.username = ""
        self.full_name = ""
        self.role = ""
        self.email = ""
        self.is_authenticated = False

    def has_permission(self, module_name: str) -> bool:
        """Check if active user's role is authorized to access the given module."""
        if not self.is_authenticated:
            return False
        allowed_modules = config.ROLE_PERMISSIONS.get(self.role, [])
        return module_name in allowed_modules


# Global singleton instance for application session
current_session = UserSession()
