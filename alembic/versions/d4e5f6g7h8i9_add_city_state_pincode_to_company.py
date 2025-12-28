"""add city, state, pincode to company

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2025-12-28 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Add city, state, and pincode columns to company table."""
    op.add_column(
        'company',
        sa.Column('city', sa.String(length=100), nullable=True),
        schema='identity'
    )
    op.add_column(
        'company',
        sa.Column('state', sa.String(length=2), nullable=True),
        schema='identity'
    )
    op.add_column(
        'company',
        sa.Column('pincode', sa.String(length=6), nullable=True),
        schema='identity'
    )


def downgrade():
    """Remove city, state, and pincode columns from company table."""
    op.drop_column('company', 'pincode', schema='identity')
    op.drop_column('company', 'state', schema='identity')
    op.drop_column('company', 'city', schema='identity')
