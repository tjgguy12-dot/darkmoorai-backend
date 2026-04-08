"""
Authentication Routes with Email OTP Verification
Uses pbkdf2_sha256 – no password length limit.
Login uses OAuth2PasswordRequestForm (works with Swagger UI).
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import secrets
import jwt
import random
import string
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.config import config
from app.database.repositories.user_repo import UserRepository
from app.database.repositories.otp_repo import OTPRepository
from app.services.email_service import email_service
from app.utils.validators import validate_password, validate_username
from app.utils.logger import logger

router = APIRouter()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

user_repo = UserRepository()
otp_repo = OTPRepository()
security = HTTPBearer(auto_error=False)


def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))


def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(seconds=config.JWT_EXPIRES_IN)
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        # Test user for development
        return {
            "id": "test-user-123",
            "email": "test@darkmoor.ai",
            "username": "testuser",
            "role": "user",
            "is_active": True,
            "is_verified": True
        }
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        return {
            "id": payload.get("sub", "test-user"),
            "email": payload.get("email", "test@darkmoor.ai"),
            "role": payload.get("role", "user"),
            "is_active": True,
            "is_verified": True
        }
    except jwt.PyJWTError:
        return {
            "id": "test-user-123",
            "email": "test@darkmoor.ai",
            "username": "testuser",
            "role": "user",
            "is_active": True,
            "is_verified": True
        }


# ============================================================================
# Request/Response Models
# ============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str
    username: str
    password: str
    full_name: Optional[str] = None


class ResendOTPRequest(BaseModel):
    email: EmailStr


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# ============================================================================
# Password helpers
# ============================================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ============================================================================
# OTP Endpoints
# ============================================================================

@router.post("/request-otp")
async def request_otp(request: OTPRequest):
    email = request.email
    existing_user = await user_repo.get_by_email(email)
    if existing_user and existing_user.get("is_verified"):
        raise HTTPException(status_code=400, detail="Email already registered and verified")

    otp_code = generate_otp()
    await otp_repo.invalidate_old_otps(email)
    await otp_repo.create({
        "email": email,
        "code": otp_code,
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
        "is_used": False,
        "attempt_count": 0
    })

    success = await email_service.send_otp_email(email, otp_code)
    if not success and config.ENV == "production":
        raise HTTPException(status_code=500, detail="Failed to send OTP email")

    if config.ENV == "development":
        print(f"\n📧 [DEV] OTP for {email}: {otp_code}\n")

    return {"message": "OTP sent", "expires_in": 600}


@router.post("/verify-otp")
async def verify_otp(request: OTPVerifyRequest):
    # Validate password strength
    is_valid, error = validate_password(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    is_valid, error = validate_username(request.username)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Check if email already verified
    existing_user = await user_repo.get_by_email(request.email)
    if existing_user and existing_user.get("is_verified"):
        raise HTTPException(status_code=400, detail="Email already registered and verified")

    # Check if username already taken (by any user, verified or not)
    existing_username = await user_repo.get_by_username(request.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    valid_otp = await otp_repo.get_valid_otp(request.email, request.otp_code)
    if not valid_otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    if valid_otp.get("attempt_count", 0) >= 5:
        await otp_repo.mark_otp_used(valid_otp["id"])
        raise HTTPException(status_code=400, detail="Too many failed attempts")

    hashed_password = hash_password(request.password)

    if existing_user:
        # Update existing unverified user
        user = await user_repo.update(existing_user["id"], {
            "username": request.username,
            "full_name": request.full_name,
            "hashed_password": hashed_password,
            "is_verified": True,
            "is_active": True
        })
    else:
        # Create new user
        user = await user_repo.create({
            "email": request.email,
            "username": request.username,
            "full_name": request.full_name,
            "hashed_password": hashed_password,
            "role": "user",
            "is_active": True,
            "is_verified": True,
            "settings": {"theme": "dark", "language": "en", "notifications_enabled": True}
        })

    await otp_repo.mark_otp_used(valid_otp["id"])
    access_token = create_access_token(user["id"], user["email"], user["role"])
    refresh_token = secrets.token_urlsafe(32)

    logger.info(f"User registered with email: {user['id']}")
    return {
        "message": "Registration successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": config.JWT_EXPIRES_IN,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "is_verified": True
        }
    }


@router.post("/resend-otp")
async def resend_otp(request: ResendOTPRequest):
    email = request.email
    otp_code = generate_otp()
    await otp_repo.invalidate_old_otps(email)
    await otp_repo.create({
        "email": email,
        "code": otp_code,
        "expires_at": datetime.utcnow() + timedelta(minutes=10),
        "is_used": False,
        "attempt_count": 0
    })
    success = await email_service.send_otp_email(email, otp_code)
    if config.ENV == "development":
        print(f"\n📧 [DEV] New OTP for {email}: {otp_code}\n")
    return {"message": "New OTP sent", "expires_in": 600}


# ============================================================================
# Legacy Registration (with username uniqueness)
# ============================================================================

@router.post("/register")
async def register(user_data: UserCreate):
    # Check if email already exists
    existing_email = await user_repo.get_by_email(user_data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username already exists
    existing_username = await user_repo.get_by_username(user_data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Validate password and username
    is_valid, error = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    is_valid, error = validate_username(user_data.username)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Hash password
    hashed_password = hash_password(user_data.password)

    user = await user_repo.create({
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "role": "user",
        "is_active": True,
        "is_verified": False,
        "settings": {"theme": "dark", "language": "en", "notifications_enabled": True}
    })

    logger.info(f"User registered (legacy): {user['id']}")
    return {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "full_name": user.get("full_name"),
        "role": user["role"],
        "is_active": user["is_active"],
        "is_verified": user["is_verified"]
    }


# ============================================================================
# Login – Works with Swagger UI (OAuth2PasswordRequestForm)
# ============================================================================

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with email and password.
    Uses OAuth2PasswordRequestForm – compatible with Swagger UI.
    """
    email = form_data.username  # Swagger sends 'username' field
    password = form_data.password

    if not email or not password:
        raise HTTPException(status_code=422, detail="Missing email or password")

    user = await user_repo.get_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account disabled")

    await user_repo.update_last_login(user["id"])
    access_token = create_access_token(user["id"], user["email"], user["role"])
    refresh_token = secrets.token_urlsafe(32)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=config.JWT_EXPIRES_IN
    )


@router.post("/logout")
async def logout():
    return {"message": "Logged out"}


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    # Simplified – in production validate against DB
    access_token = create_access_token("test-user", "test@darkmoor.ai", "user")
    return TokenResponse(
        access_token=access_token,
        refresh_token=secrets.token_urlsafe(32),
        expires_in=config.JWT_EXPIRES_IN
    )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    user = await user_repo.get(current_user["id"])
    if not verify_password(request.old_password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect old password")

    is_valid, error = validate_password(request.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    hashed = hash_password(request.new_password)
    await user_repo.update(current_user["id"], {"hashed_password": hashed})
    return {"message": "Password changed"}