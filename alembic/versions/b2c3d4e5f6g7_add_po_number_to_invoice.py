"""add po_number to invoice

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Add po_number column to invoice table."""
    op.add_column(
        'invoice',
        sa.Column('po_number', sa.String(length=50), nullable=True),
        schema='billing'
    )


def downgrade():
    """Remove po_number column from invoice table."""
    op.drop_column('invoice', 'po_number', schema='billing')
