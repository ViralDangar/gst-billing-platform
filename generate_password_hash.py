"""
Generate password hash for admin user.
Run this to get the correct bcrypt hash for the password.
"""

from passlib.context import CryptContext

# Password hashing configuration (same as in security.py)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False
)

password = "admin123456"
hashed = pwd_context.hash(password)

print(f"Password: {password}")
print(f"Hashed: {hashed}")

# Verify it works
is_valid = pwd_context.verify(password, hashed)
print(f"Verification test: {is_valid}")
