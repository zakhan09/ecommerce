from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_password_hash(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = self.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user_tokens(self, user_id: int, access_token_hash: str, refresh_token_hash: str, 
                          access_expires: datetime, refresh_expires: datetime) -> bool:
        """Update user's access and refresh tokens"""
        user = self.get_user_by_id(user_id)
        if user:
            user.access_token_hash = access_token_hash
            user.refresh_token_hash = refresh_token_hash
            user.access_token_expires_at = access_expires
            user.refresh_token_expires_at = refresh_expires
            self.db.commit()
            return True
        return False

    def clear_user_tokens(self, user_id: int) -> bool:
        """Clear user's access and refresh tokens"""
        user = self.get_user_by_id(user_id)
        if user:
            user.access_token_hash = None
            user.refresh_token_hash = None
            user.access_token_expires_at = None
            user.refresh_token_expires_at = None
            self.db.commit()
            return True
        return False

    def get_user_by_refresh_token(self, refresh_token_hash: str) -> Optional[User]:
        """Get user by refresh token hash"""
        return self.db.query(User).filter(
            User.refresh_token_hash == refresh_token_hash,
            User.refresh_token_expires_at > datetime.utcnow()
        ).first()

    def get_user_by_access_token(self, access_token_hash: str) -> Optional[User]:
        """Get user by access token hash"""
        return self.db.query(User).filter(
            User.access_token_hash == access_token_hash,
            User.access_token_expires_at > datetime.utcnow()
        ).first() 