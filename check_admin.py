"""
Check if admin user exists and test password verification.
"""

import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

# Create database connection
engine = create_engine(settings.database_url)

with engine.connect() as conn:
    # Check if auth schema exists
    result = conn.execute(text("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name = 'auth'
    """))

    if result.fetchone():
        print("✓ Auth schema exists")

        # Check if users table exists
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'auth' AND table_name = 'users'
        """))

        if result.fetchone():
            print("✓ Users table exists")

            # Check for admin user
            result = conn.execute(text("""
                SELECT username, email, hashed_password, is_active, is_superuser
                FROM auth.users
                WHERE username = 'admin'
            """))

            admin = result.fetchone()
            if admin:
                print(f"\n✓ Admin user found:")
                print(f"  Username: {admin[0]}")
                print(f"  Email: {admin[1]}")
                print(f"  Password hash: {admin[2][:50]}...")
                print(f"  Is active: {admin[3]}")
                print(f"  Is superuser: {admin[4]}")

                # Test password verification
                from app.auth_service.security import verify_password

                test_password = "admin123456"
                is_valid = verify_password(test_password, admin[2])
                print(f"\n✓ Password verification for '{test_password}': {is_valid}")

            else:
                print("\n✗ Admin user NOT found")
                print("\nYou need to run: alembic upgrade head")
        else:
            print("✗ Users table does NOT exist")
            print("\nYou need to run: alembic upgrade head")
    else:
        print("✗ Auth schema does NOT exist")
        print("\nYou need to run: alembic upgrade head")
