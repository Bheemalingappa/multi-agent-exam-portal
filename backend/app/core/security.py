from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import bcrypt
import jwt
from app.core.config import settings

def _get_password_bytes(password: str) -> bytes:
    """
    Safely convert a password string to UTF-8 bytes capped at maximum 72 bytes.
    Ensures multi-byte UTF-8 character sequences are not truncated mid-byte.
    """
    pwd_bytes = password.encode('utf-8')
    if len(pwd_bytes) <= 72:
        return pwd_bytes
    
    truncated_str = pwd_bytes[:72].decode('utf-8', errors='ignore')
    return truncated_str.encode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain text password against bcrypt hashed password."""
    try:
        pwd_bytes = _get_password_bytes(plain_password)
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash safely capped at 72 UTF-8 bytes."""
    pwd_bytes = _get_password_bytes(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def create_access_token(subject: str | Any, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with user ID subject and role claim."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "iat": datetime.utcnow()
    }
    secret = settings.JWT_SECRET_KEY or settings.JWT_SECRET
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT access token."""
    try:
        secret = settings.JWT_SECRET_KEY or settings.JWT_SECRET
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
