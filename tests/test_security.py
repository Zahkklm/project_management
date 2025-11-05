from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "test_password_123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_password_hashing_long_password():
    """Test password hashing with long password (bcrypt 72 char limit)"""
    long_password = "a" * 100
    hashed = get_password_hash(long_password)

    # Should verify with truncated version
    assert verify_password(long_password, hashed) is True
    assert verify_password("a" * 72, hashed) is True


def test_create_and_decode_token():
    """Test JWT token creation and decoding"""
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert token is not None
    decoded = decode_access_token(token)
    assert decoded["sub"] == "testuser"


def test_token_with_expiration():
    """Test token with custom expiration"""
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))

    decoded = decode_access_token(token)
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded


def test_token_with_integer_sub():
    """Test token creation with integer subject"""
    data = {"sub": 123}
    token = create_access_token(data)

    decoded = decode_access_token(token)
    assert decoded["sub"] == "123"  # Should be converted to string


def test_decode_invalid_token():
    """Test decoding invalid token"""
    result = decode_access_token("invalid_token_string")
    assert result is None


def test_decode_malformed_token():
    """Test decoding malformed JWT token"""
    result = decode_access_token("not.a.valid.jwt.token")
    assert result is None
