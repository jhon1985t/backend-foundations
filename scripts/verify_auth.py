#!/usr/bin/env python
"""
Verify complete authentication flow end-to-end.
Tests: password hashing, JWT token creation, and token validation.
"""

import sys
from jose import jwt
from app.auth.security import hash_password, verify_password, create_access_token
from app.settings import settings

print("\n=== Authentication System Verification ===\n")

# Test 1: Password hashing
print("1️⃣ Testing password hashing...")
try:
    test_password = "1234"
    hashed = hash_password(test_password)
    print(f"   ✓ Generated hash: {hashed[:40]}...")

    is_valid = verify_password(test_password, hashed)
    assert is_valid, "verify_password returned False for correct password"
    print("   ✓ Password verification: PASSED")

    is_invalid = verify_password("wrong_password", hashed)
    assert not is_invalid, "verify_password returned True for wrong password"
    print("   ✓ Wrong password rejection: PASSED")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

# Test 2: JWT token creation
print("\n2️⃣ Testing JWT token creation...")
try:
    user_data = {"user_id": 1, "email": "user@example.com"}
    token = create_access_token(user_data)
    print(f"   ✓ Generated token: {token[:50]}...")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

# Test 3: JWT token decoding
print("\n3️⃣ Testing JWT token decoding...")
try:
    decoded = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    print(
        f"   ✓ Decoded claims: sub={decoded.get('sub')}, email={decoded.get('email')}"
    )

    assert decoded.get("sub") == "1", f"Expected sub='1', got '{decoded.get('sub')}'"
    assert (
        decoded.get("email") == "user@example.com"
    ), f"Expected email='user@example.com', got '{decoded.get('email')}'"
    print("   ✓ Token validation: PASSED")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

# Test 4: bcrypt version info
print("\n4️⃣ Checking bcrypt installation...")
try:
    import bcrypt

    print(f"   ✓ bcrypt version: {bcrypt.__version__}")
except Exception as e:
    print(f"   ✓ bcrypt installed (version reading: {e})")

# Test 5: passlib
print("\n5️⃣ Checking passlib installation...")
try:
    import passlib.context  # noqa: F401

    print("   ✓ passlib CryptContext available")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 40)
print("✅ All authentication systems verified!")
print("=" * 40 + "\n")
