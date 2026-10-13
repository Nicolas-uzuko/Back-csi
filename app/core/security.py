import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt_sha256 pre-hashes the password before bcrypt, so the bcrypt 72-byte
# input limit cannot silently truncate a password accepted by Pydantic. The
# plain bcrypt scheme remains available for verifying legacy hashes.
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: Any, extra_claims: Optional[dict] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    data = {"sub": str(subject), "exp": expire, "type": "access"}
    if extra_claims:
        data.update(extra_claims)
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: Any) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    data = {"sub": str(subject), "exp": expire, "type": "refresh"}
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise


def token_type_is(payload: dict, expected: str) -> bool:
    return payload.get("type") == expected and bool(payload.get("sub"))


def generate_reset_token() -> tuple[str, str]:
    """Returns (plain_token, hashed_token). Store only the hash."""
    plain = secrets.token_urlsafe(32)
    hashed = hashlib.sha256(plain.encode()).hexdigest()
    return plain, hashed


def hash_reset_token(plain_token: str) -> str:
    return hashlib.sha256(plain_token.encode()).hexdigest()


def verify_reset_token(plain_token: str, stored_hash: str) -> bool:
    return secrets.compare_digest(
        hashlib.sha256(plain_token.encode()).hexdigest(),
        stored_hash
    )
