"""change bank details to jsonb

Revision ID: 56e8341dcb73
Revises: ec3f618a9cd4
Create Date: 2025-12-17 22:41:57.759198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '56e8341dcb73'
down_revision: Union[str, Sequence[str], None] = 'ec3f618a9cd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        ALTER TABLE identity.company
        ALTER COLUMN default_bank_details
        TYPE JSONB
        USING default_bank_details::jsonb
    """)


def downgrade():
    op.execute("""
        ALTER TABLE identity.company
        ALTER COLUMN default_bank_details
        TYPE TEXT
        USING default_bank_details::text
    """)
