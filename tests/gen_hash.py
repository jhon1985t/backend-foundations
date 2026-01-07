from app.auth.security import hash_password, verify_password

# Generar hash para '1234'
password = "1234"
hash_result = hash_password(password)

print(f"Password: {password}")
print(f"Hash: {hash_result}")

# Verificar que funcione
is_valid = verify_password(password, hash_result)
print(f"Verification: {is_valid}")
