import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.repository.user_repository import UserRepository
from app.schemas.user import UserCreate

class TestUserRepository:
    def setup_method(self):
        """Setup method for each test"""
        self.mock_db = Mock()
        self.user_repository = UserRepository(self.mock_db)

    def test_get_password_hash(self):
        """Test password hashing"""
        password = "test_password"
        hashed = self.user_repository.get_password_hash(password)
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "test_password"
        hashed = self.user_repository.get_password_hash(password)
        result = self.user_repository.verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test_password"
        hashed = self.user_repository.get_password_hash(password)
        result = self.user_repository.verify_password("wrong_password", hashed)
        assert result is False

    def test_get_user_by_email_found(self):
        """Test getting user by email when user exists"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.user_repository.get_user_by_email("test@example.com")
        assert result == mock_user

    def test_get_user_by_email_not_found(self):
        """Test getting user by email when user doesn't exist"""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.user_repository.get_user_by_email("nonexistent@example.com")
        assert result is None

    def test_get_user_by_username_found(self):
        """Test getting user by username when user exists"""
        mock_user = Mock()
        mock_user.username = "testuser"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.user_repository.get_user_by_username("testuser")
        assert result == mock_user

    def test_get_user_by_username_not_found(self):
        """Test getting user by username when user doesn't exist"""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.user_repository.get_user_by_username("nonexistentuser")
        assert result is None

    def test_get_user_by_id_found(self):
        """Test getting user by ID when user exists"""
        mock_user = Mock()
        mock_user.id = 1
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.user_repository.get_user_by_id(1)
        assert result == mock_user

    def test_get_user_by_id_not_found(self):
        """Test getting user by ID when user doesn't exist"""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.user_repository.get_user_by_id(999)
        assert result is None

    def test_create_user_success(self):
        """Test successful user creation"""
        user_data = UserCreate(email="test@example.com", username="testuser", password="password")
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        with patch('app.repository.user_repository.User') as mock_user_class:
            mock_user_class.return_value = mock_user
            result = self.user_repository.create_user(user_data)
            
            assert result == mock_user
            self.mock_db.add.assert_called_once()
            self.mock_db.commit.assert_called_once()
            self.mock_db.refresh.assert_called_once_with(mock_user)

    def test_update_user_tokens_success(self):
        """Test successful token update"""
        user_id = 1
        access_token_hash = "access_hash"
        refresh_token_hash = "refresh_hash"
        access_expires = datetime.utcnow()
        refresh_expires = datetime.utcnow()
        
        mock_user = Mock()
        mock_user.id = user_id
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_db.commit.return_value = None
        
        result = self.user_repository.update_user_tokens(
            user_id, access_token_hash, refresh_token_hash, access_expires, refresh_expires
        )
        
        assert result is True
        assert mock_user.access_token_hash == access_token_hash
        assert mock_user.refresh_token_hash == refresh_token_hash
        assert mock_user.access_token_expires_at == access_expires
        assert mock_user.refresh_token_expires_at == refresh_expires
        self.mock_db.commit.assert_called_once()

    def test_update_user_tokens_user_not_found(self):
        """Test token update when user doesn't exist"""
        user_id = 999
        access_token_hash = "access_hash"
        refresh_token_hash = "refresh_hash"
        access_expires = datetime.utcnow()
        refresh_expires = datetime.utcnow()
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.user_repository.update_user_tokens(
            user_id, access_token_hash, refresh_token_hash, access_expires, refresh_expires
        )
        
        assert result is False

    def test_clear_user_tokens_success(self):
        """Test successful token clearing"""
        user_id = 1
        mock_user = Mock()
        mock_user.id = user_id
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_db.commit.return_value = None
        
        result = self.user_repository.clear_user_tokens(user_id)
        
        assert result is True
        assert mock_user.access_token_hash is None
        assert mock_user.refresh_token_hash is None
        assert mock_user.access_token_expires_at is None
        assert mock_user.refresh_token_expires_at is None
        self.mock_db.commit.assert_called_once()

    def test_clear_user_tokens_user_not_found(self):
        """Test token clearing when user doesn't exist"""
        user_id = 999
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.user_repository.clear_user_tokens(user_id)
        
        assert result is False

    def test_get_user_by_refresh_token_found(self):
        """Test getting user by refresh token when user exists"""
        refresh_token_hash = "refresh_hash"
        mock_user = Mock()
        mock_user.refresh_token_hash = refresh_token_hash
        mock_user.refresh_token_expires_at = datetime.utcnow()
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.user_repository.get_user_by_refresh_token(refresh_token_hash)
        assert result == mock_user

    def test_get_user_by_refresh_token_not_found(self):
        """Test getting user by refresh token when user doesn't exist"""
        refresh_token_hash = "refresh_hash"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.user_repository.get_user_by_refresh_token(refresh_token_hash)
        assert result is None

    def test_get_user_by_access_token_found(self):
        """Test getting user by access token when user exists"""
        access_token_hash = "access_hash"
        mock_user = Mock()
        mock_user.access_token_hash = access_token_hash
        mock_user.access_token_expires_at = datetime.utcnow()
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.user_repository.get_user_by_access_token(access_token_hash)
        assert result == mock_user

    def test_get_user_by_access_token_not_found(self):
        """Test getting user by access token when user doesn't exist"""
        access_token_hash = "access_hash"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.user_repository.get_user_by_access_token(access_token_hash)
        assert result is None 