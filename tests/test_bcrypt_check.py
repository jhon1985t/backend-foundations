from app.auth.security import hash_password, verify_password


def test_argon2_hash_and_verify():
    """Test that argon2 password hashing and verification works correctly."""
    # Test basic hashing
    h = hash_password("test")
    assert h.startswith("$argon2")
    assert verify_password("test", h)
    assert not verify_password("wrong", h)


def test_argon2_with_specific_password():
    """Test hashing with specific password '1234'."""
    h1234 = hash_password("1234")
    assert h1234.startswith("$argon2")
    assert verify_password("1234", h1234)
    assert not verify_password("wrong", h1234)
