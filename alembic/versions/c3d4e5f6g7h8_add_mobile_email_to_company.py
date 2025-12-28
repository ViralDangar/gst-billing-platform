"""add mobile_number and email_id to company

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2025-12-28 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Add mobile_number and email_id columns to company table."""
    op.add_column(
        'company',
        sa.Column('mobile_number', sa.String(length=200), nullable=True),
        schema='identity'
    )
    op.add_column(
        'company',
        sa.Column('email_id', sa.String(length=255), nullable=True),
        schema='identity'
    )


def downgrade():
    """Remove mobile_number and email_id columns from company table."""
    op.drop_column('company', 'email_id', schema='identity')
    op.drop_column('company', 'mobile_number', schema='identity')
