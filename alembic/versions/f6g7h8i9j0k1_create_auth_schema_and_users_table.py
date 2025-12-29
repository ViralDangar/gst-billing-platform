"""create auth schema and users table

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2025-12-28 04:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'f6g7h8i9j0k1'
down_revision: Union[str, Sequence[str], None] = 'e5f6g7h8i9j0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Create auth schema and users table."""
    # Create auth schema
    op.execute('CREATE SCHEMA IF NOT EXISTS auth')

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        schema='auth'
    )

    # Create unique constraints
    op.create_unique_constraint('uq_users_email', 'users', ['email'], schema='auth')
    op.create_unique_constraint('uq_users_username', 'users', ['username'], schema='auth')

    # Create indexes for better query performance
    op.create_index('ix_users_email', 'users', ['email'], schema='auth')
    op.create_index('ix_users_username', 'users', ['username'], schema='auth')

    # Insert a default admin user (password: admin123456)
    # Hashed password for 'admin123456' using bcrypt
    op.execute("""
        INSERT INTO auth.users (id, email, username, hashed_password, full_name, is_active, is_superuser)
        VALUES (
            gen_random_uuid(),
            'admin@example.com',
            'admin',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQzKRt8pe',
            'System Administrator',
            true,
            true
        )
    """)


def downgrade():
    """Drop users table and auth schema."""
    # Drop indexes
    op.drop_index('ix_users_username', table_name='users', schema='auth')
    op.drop_index('ix_users_email', table_name='users', schema='auth')

    # Drop unique constraints
    op.drop_constraint('uq_users_username', 'users', schema='auth', type_='unique')
    op.drop_constraint('uq_users_email', 'users', schema='auth', type_='unique')

    # Drop users table
    op.drop_table('users', schema='auth')

    # Drop auth schema
    op.execute('DROP SCHEMA IF EXISTS auth CASCADE')
