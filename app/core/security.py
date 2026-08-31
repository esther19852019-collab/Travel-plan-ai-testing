from datetime import datetime, timedelta, timezone
import os
import jwt
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
load_dotenv()

password_hash = PasswordHash.recommended()

# Set the expiration time for the access token (e.g., 1 hour)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

def hash_password(password:str)-> str:
    return password_hash.hash(password)

def verify_password(password:str, hashed_password:str)-> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


security = HTTPBearer()

def decode_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return email