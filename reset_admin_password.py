"""
Reset admin password with correct bcrypt hash.
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.auth_service.security import get_password_hash

# Create database connection
engine = create_engine(settings.database_url)

# Generate new hash for admin123456
password = "admin123456"
new_hash = get_password_hash(password)

print(f"Generating new password hash for: {password}")
print(f"New hash: {new_hash}")

# Update admin user password
with engine.connect() as conn:
    result = conn.execute(
        text("""
            UPDATE auth.users
            SET hashed_password = :new_hash
            WHERE username = 'admin'
            RETURNING username, email
        """),
        {"new_hash": new_hash}
    )
    conn.commit()

    updated_user = result.fetchone()
    if updated_user:
        print(f"\n✓ Password updated successfully for user: {updated_user[0]} ({updated_user[1]})")

        # Verify the new password works
        from app.auth_service.security import verify_password

        # Fetch the updated hash
        result = conn.execute(
            text("SELECT hashed_password FROM auth.users WHERE username = 'admin'")
        )
        stored_hash = result.fetchone()[0]

        is_valid = verify_password(password, stored_hash)
        print(f"✓ Password verification test: {is_valid}")

        if is_valid:
            print("\n✓ SUCCESS! You can now login with:")
            print(f"  Username: admin")
            print(f"  Password: {password}")
        else:
            print("\n✗ WARNING: Password verification still fails!")
    else:
        print("\n✗ Failed to update password - admin user not found")
