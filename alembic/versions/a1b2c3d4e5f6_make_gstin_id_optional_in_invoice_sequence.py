"""make gstin_id optional in invoice_sequence

Revision ID: a1b2c3d4e5f6
Revises: 56e8341dcb73
Create Date: 2025-12-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '56e8341dcb73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop the unique constraint that includes gstin_id
    op.drop_constraint(
        "invoice_sequence_gstin_id_financial_year_key",
        "invoice_sequence",
        schema="billing",
        type_="unique"
    )

    # Make gstin_id nullable
    op.alter_column(
        "invoice_sequence",
        "gstin_id",
        existing_type=UUID(as_uuid=True),
        nullable=True,
        schema="billing"
    )

    # Add new unique constraint on financial_year only
    op.create_unique_constraint(
        "uq_invoice_sequence_financial_year",
        "invoice_sequence",
        ["financial_year"],
        schema="billing"
    )


def downgrade():
    # Drop the new unique constraint
    op.drop_constraint(
        "uq_invoice_sequence_financial_year",
        "invoice_sequence",
        schema="billing",
        type_="unique"
    )

    # Make gstin_id not nullable
    op.alter_column(
        "invoice_sequence",
        "gstin_id",
        existing_type=UUID(as_uuid=True),
        nullable=False,
        schema="billing"
    )

    # Restore original unique constraint
    op.create_unique_constraint(
        "invoice_sequence_gstin_id_financial_year_key",
        "invoice_sequence",
        ["gstin_id", "financial_year"],
        schema="billing"
    )
