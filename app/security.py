"""
Security helper functions:
  - password hashing (Argon2id)
  - JWT access token creation and verification
"""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings

# A password hasher using the recommended algorithm (Argon2id) with
# safe default settings. We create it once and reuse it everywhere.
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Turn a plain password into a secure, salted Argon2 hash."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plain password matches the stored hash."""
    return password_hasher.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Create a signed JWT that identifies the user and expires after a while."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    # The payload ("claims") stored inside the token. It is readable by anyone,
    # so it must NEVER contain secrets like passwords.
    payload = {
        "sub": str(user_id),  # "subject": who this token belongs to (must be a string)
        "iat": now,           # "issued at": when the token was created
        "exp": expire,        # "expires": after this time the token is rejected
    }

    # Sign the payload with our secret key. Anyone can read the token,
    # but only someone with the secret key can create a valid one.
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int | None:
    """
    Verify a JWT and return the user id stored in it.

    Returns None if the token is invalid for ANY reason:
    wrong signature (tampered/forged), expired, malformed, or missing claims.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            # Only accept the algorithm WE chose. Never trust the token's own
            # "alg" header (blocks attacks like "alg": "none").
            algorithms=[settings.jwt_algorithm],
            # Reject tokens that don't contain these claims
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        # Covers: bad signature, expired token, malformed token, missing claims
        return None

    try:
        return int(payload["sub"])
    except ValueError:
        return None
