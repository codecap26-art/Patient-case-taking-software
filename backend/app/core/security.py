import hmac
import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import bcrypt
import jwt
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # bcrypt requires bytes; max 72 bytes
        password_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.PyJWTError:
        return None


def generate_signed_qr_token(patient_id: str, expiry_seconds: int = 300) -> str:
    """
    Generates a cryptographically signed, short-lived QR token for bedside patient identification.
    Format: PCT:v1:<patient_id>:<expires_at>:<signature>
    """
    expires_at = int(time.time()) + expiry_seconds
    data = f"PCT:v1:{patient_id}:{expires_at}"
    signature = hmac.new(
        settings.QR_SIGNING_SECRET.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:16]
    return f"{data}:{signature}"


def verify_signed_qr_token(qr_token: str) -> Optional[str]:
    """
    Verifies the signed QR token and returns patient_id if valid and not expired.
    """
    try:
        parts = qr_token.split(":")
        if len(parts) != 5 or parts[0] != "PCT" or parts[1] != "v1":
            return None
        _, _, patient_id, expires_at_str, sig = parts
        expires_at = int(expires_at_str)
        if time.time() > expires_at:
            return None  # Expired

        data = f"PCT:v1:{patient_id}:{expires_at_str}"
        expected_sig = hmac.new(
            settings.QR_SIGNING_SECRET.encode("utf-8"),
            data.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()[:16]

        if hmac.compare_digest(sig, expected_sig):
            return patient_id
        return None
    except Exception:
        return None
