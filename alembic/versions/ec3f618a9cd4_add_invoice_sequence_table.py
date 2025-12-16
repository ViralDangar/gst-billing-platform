"""add invoice sequence table

Revision ID: ec3f618a9cd4
Revises: 9ef13ee0fd51
Create Date: 2025-12-16 23:45:54.856179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'ec3f618a9cd4'
down_revision: Union[str, Sequence[str], None] = '9ef13ee0fd51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "invoice_sequence",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("gstin_id", UUID(as_uuid=True), nullable=False),
        sa.Column("financial_year", sa.String(9), nullable=False),
        sa.Column("last_sequence", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("gstin_id", "financial_year"),
        schema="billing",
    )


def downgrade():
    op.drop_table("invoice_sequence", schema="billing")

