import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, RefreshToken
from fastapi import HTTPException

class TestAuthService:
    def setup_method(self):
        """Setup method for each test"""
        self.mock_db = Mock()
        self.auth_service = AuthService(self.mock_db)

    def test_create_access_token(self):
        """Test creating access token"""
        data = {"sub": "test@example.com"}
        token = self.auth_service.create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        data = {"sub": "test@example.com"}
        token = self.auth_service.create_refresh_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """Test verifying valid token"""
        data = {"sub": "test@example.com"}
        token = self.auth_service.create_access_token(data)
        payload = self.auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"

    def test_verify_token_invalid(self):
        """Test verifying invalid token"""
        payload = self.auth_service.verify_token("invalid_token")
        assert payload is None

    def test_hash_token(self):
        """Test token hashing"""
        token = "test_token"
        hashed = self.auth_service.hash_token(token)
        assert isinstance(hashed, str)
        assert len(hashed) == 64

    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.hashed_password = "hashed_password"
        
        self.auth_service.user_repository.get_user_by_email.return_value = mock_user
        self.auth_service.user_repository.verify_password.return_value = True
        
        result = self.auth_service.authenticate_user("test@example.com", "password")
        assert result is not None
        assert result["id"] == 1
        assert result["email"] == "test@example.com"

    def test_authenticate_user_invalid_email(self):
        """Test authentication with invalid email"""
        self.auth_service.user_repository.get_user_by_email.return_value = None
        
        result = self.auth_service.authenticate_user("invalid@example.com", "password")
        assert result is None

    def test_authenticate_user_invalid_password(self):
        """Test authentication with invalid password"""
        mock_user = Mock()
        mock_user.hashed_password = "hashed_password"
        
        self.auth_service.user_repository.get_user_by_email.return_value = mock_user
        self.auth_service.user_repository.verify_password.return_value = False
        
        result = self.auth_service.authenticate_user("test@example.com", "wrong_password")
        assert result is None

    def test_register_user_success(self):
        """Test successful user registration"""
        user_data = UserCreate(email="test@example.com", username="testuser", password="password")
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.is_active = True
        mock_user.is_verified = False
        mock_user.created_at = datetime.utcnow()
        
        self.auth_service.user_repository.get_user_by_email.return_value = None
        self.auth_service.user_repository.get_user_by_username.return_value = None
        self.auth_service.user_repository.create_user.return_value = mock_user
        
        result = self.auth_service.register_user(user_data)
        assert result["email"] == "test@example.com"
        assert result["username"] == "testuser"

    def test_register_user_email_exists(self):
        """Test registration with existing email"""
        user_data = UserCreate(email="existing@example.com", username="testuser", password="password")
        
        self.auth_service.user_repository.get_user_by_email.return_value = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            self.auth_service.register_user(user_data)
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)

    def test_register_user_username_exists(self):
        """Test registration with existing username"""
        user_data = UserCreate(email="test@example.com", username="existinguser", password="password")
        
        self.auth_service.user_repository.get_user_by_email.return_value = None
        self.auth_service.user_repository.get_user_by_username.return_value = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            self.auth_service.register_user(user_data)
        assert exc_info.value.status_code == 400
        assert "Username already taken" in str(exc_info.value.detail)

    def test_login_user_success(self):
        """Test successful user login"""
        user_data = UserLogin(email="test@example.com", password="password")
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        self.auth_service.authenticate_user = Mock(return_value={"id": 1, "email": "test@example.com", "username": "testuser"})
        self.auth_service.user_repository.get_user_by_id.return_value = mock_user
        self.auth_service.user_repository.update_user_tokens.return_value = True
        
        result = self.auth_service.login_user(user_data)
        assert "access_token" in result
        assert "refresh_token" in result
        assert result.token_type == "bearer"

    def test_login_user_invalid_credentials(self):
        """Test login with invalid credentials"""
        user_data = UserLogin(email="test@example.com", password="wrong_password")
        
        self.auth_service.authenticate_user = Mock(return_value=None)
        
        with pytest.raises(HTTPException) as exc_info:
            self.auth_service.login_user(user_data)
        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in str(exc_info.value.detail)

    def test_login_user_inactive_account(self):
        """Test login with inactive account"""
        user_data = UserLogin(email="test@example.com", password="password")
        mock_user = Mock()
        mock_user.is_active = False
        
        self.auth_service.authenticate_user = Mock(return_value={"id": 1, "email": "test@example.com", "username": "testuser"})
        self.auth_service.user_repository.get_user_by_id.return_value = mock_user
        
        with pytest.raises(HTTPException) as exc_info:
            self.auth_service.login_user(user_data)
        assert exc_info.value.status_code == 401
        assert "User account is disabled" in str(exc_info.value.detail) 