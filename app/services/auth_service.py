

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """
    Turns "mypassword123" into "$2b$12$randomsaltXXXXXXXXXXXXhashed"
    The hash is different every time even for same password (due to salt)
    Salt = random data added before hashing to prevent rainbow table attacks
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if plain password matches the hash
    bcrypt extracts the salt from the hash and re-hashes to compare
    Returns True if match, False if not
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Creates a short-lived JWT access token (30 minutes)
    JWT = 3 parts: header.payload.signature
    header = algorithm info
    payload = our data (user_id, role, expiry)
    signature = cryptographic proof it hasn't been tampered with
    """
    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({
        "exp": expire,      
        "type": "access"    
    })
    
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """
    Creates a long-lived JWT refresh token (7 days)
    Used ONLY to get new access tokens — not for API access
    This is the standard pattern used by Google, GitHub, etc.
    """
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload.update({
        "exp": expire,
        "type": "refresh"
    })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    """
    Decodes and VERIFIES a JWT token
    Returns the payload dict if valid, None if invalid/expired
    jose automatically checks:
    - signature is valid (not tampered)
    - token hasn't expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None