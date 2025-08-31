from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.repository.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, Token, RefreshToken
from fastapi import HTTPException, status
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_REFRESH_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None

    def hash_token(self, token: str) -> str:
        """Hash token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()

    def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate user with email and password"""
        user = self.user_repository.get_user_by_email(email)
        if not user:
            return None
        if not self.user_repository.verify_password(password, user.hashed_password):
            return None
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username
        }

    def register_user(self, user_data: UserCreate) -> dict:
        """Register a new user"""
        if self.user_repository.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if self.user_repository.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        user = self.user_repository.create_user(user_data)
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at
        }

    def login_user(self, user_data: UserLogin) -> Token:
        """Login user and return access and refresh tokens"""
        user_info = self.authenticate_user(user_data.email, user_data.password)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        user = self.user_repository.get_user_by_id(user_info["id"])
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )

        access_token = self.create_access_token(data={"sub": user.email})
        refresh_token = self.create_refresh_token(data={"sub": user.email})

        access_token_hash = self.hash_token(access_token)
        refresh_token_hash = self.hash_token(refresh_token)

        access_expires = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        refresh_expires = datetime.utcnow() + timedelta(minutes=settings.JWT_REFRESH_EXPIRE_MINUTES)

        self.user_repository.update_user_tokens(
            user.id, access_token_hash, refresh_token_hash, access_expires, refresh_expires
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    def refresh_access_token(self, refresh_token_data: RefreshToken) -> Token:
        """Refresh access token using refresh token"""
        payload = self.verify_token(refresh_token_data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        refresh_token_hash = self.hash_token(refresh_token_data.refresh_token)
        user = self.user_repository.get_user_by_refresh_token(refresh_token_hash)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        new_access_token = self.create_access_token(data={"sub": user.email})
        new_refresh_token = self.create_refresh_token(data={"sub": user.email})

        new_access_token_hash = self.hash_token(new_access_token)
        new_refresh_token_hash = self.hash_token(new_refresh_token)

        access_expires = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        refresh_expires = datetime.utcnow() + timedelta(minutes=settings.JWT_REFRESH_EXPIRE_MINUTES)

        self.user_repository.update_user_tokens(
            user.id, new_access_token_hash, new_refresh_token_hash, access_expires, refresh_expires
        )

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    def logout_user(self, access_token: str) -> bool:
        """Logout user by clearing tokens"""
        payload = self.verify_token(access_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )

        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return self.user_repository.clear_user_tokens(user.id)

    def get_current_user(self, access_token: str) -> Optional[dict]:
        """Get current user from access token"""
        payload = self.verify_token(access_token)
        if not payload:
            return None

        email = payload.get("sub")
        if not email:
            return None

        access_token_hash = self.hash_token(access_token)
        user = self.user_repository.get_user_by_access_token(access_token_hash)
        
        if not user:
            return None

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        } 