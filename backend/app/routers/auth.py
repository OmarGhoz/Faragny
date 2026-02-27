from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from sqlalchemy.orm import Session
import hashlib
import secrets
import uuid

from ..database import get_db, User

router = APIRouter()

# In-memory sessions (token -> username)
SESSIONS: Dict[str, str] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    username: str


class MessageResponse(BaseModel):
    message: str


def hash_password(password: str) -> str:
    """Hash password using SHA256 with a random salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored hash."""
    try:
        salt, stored_hash = hashed_password.split("$")
        pwd_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return pwd_hash == stored_hash
    except ValueError:
        return False


def get_current_user(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        scheme, token = authorization.split(" ", 1)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Expected Bearer token")
    username = SESSIONS.get(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username


@router.post("/register", response_model=MessageResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user with hashed password
    new_user = User(
        username=payload.username,
        password_hash=hash_password(payload.password)
    )
    db.add(new_user)
    db.commit()
    
    return MessageResponse(message="User registered successfully")


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # Find user in database
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create session token
    token = uuid.uuid4().hex
    SESSIONS[token] = user.username
    
    return TokenResponse(token=token, username=user.username)
