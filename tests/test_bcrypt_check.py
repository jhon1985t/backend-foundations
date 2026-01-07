import bcrypt
from app.auth.security import hash_password, verify_password

print(f"✓ bcrypt {bcrypt.__version__} installed")

h = hash_password("test")
print(f"✓ Hash created: {h[:30]}...")

v = verify_password("test", h)
print(f"✓ Verify works: {v}")

# Test with '1234'
h1234 = hash_password("1234")
v1234 = verify_password("1234", h1234)
print(f"✓ Password '1234' hashing works: {v1234}")
