"""replace JSONB bank with individual columns

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2025-12-28 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h8i9j0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Replace JSONB default_bank_details with individual bank columns and remove logo_url."""
    # Add new individual bank columns
    op.add_column(
        'company',
        sa.Column('bank_name', sa.String(length=255), nullable=True),
        schema='identity'
    )
    op.add_column(
        'company',
        sa.Column('bank_branch', sa.String(length=255), nullable=True),
        schema='identity'
    )
    op.add_column(
        'company',
        sa.Column('account_holder_name', sa.String(length=255), nullable=True),
        schema='identity'
    )
    op.add_column(
        'company',
        sa.Column('account_number', sa.String(length=50), nullable=True),
        schema='identity'
    )
    op.add_column(
        'company',
        sa.Column('ifsc_code', sa.String(length=11), nullable=True),
        schema='identity'
    )

    # Migrate data from JSONB to individual columns
    op.execute("""
        UPDATE identity.company
        SET
            bank_name = default_bank_details->>'bank_name',
            bank_branch = COALESCE(default_bank_details->>'bank_branch', default_bank_details->>'branch'),
            account_holder_name = default_bank_details->>'account_name',
            account_number = default_bank_details->>'account_number',
            ifsc_code = default_bank_details->>'ifsc_code'
        WHERE default_bank_details IS NOT NULL
    """)

    # Drop the old JSONB column
    op.drop_column('company', 'default_bank_details', schema='identity')

    # Drop logo_url column
    op.drop_column('company', 'logo_url', schema='identity')


def downgrade():
    """Restore JSONB default_bank_details from individual columns and restore logo_url."""
    # Add back logo_url column
    op.add_column(
        'company',
        sa.Column('logo_url', sa.Text, nullable=True),
        schema='identity'
    )

    # Add back the JSONB column
    op.add_column(
        'company',
        sa.Column('default_bank_details', JSONB, nullable=True),
        schema='identity'
    )

    # Migrate data back to JSONB
    op.execute("""
        UPDATE identity.company
        SET default_bank_details = jsonb_build_object(
            'bank_name', bank_name,
            'bank_branch', bank_branch,
            'account_name', account_holder_name,
            'account_number', account_number,
            'ifsc_code', ifsc_code
        )
        WHERE bank_name IS NOT NULL
           OR bank_branch IS NOT NULL
           OR account_holder_name IS NOT NULL
           OR account_number IS NOT NULL
           OR ifsc_code IS NOT NULL
    """)

    # Drop individual bank columns
    op.drop_column('company', 'ifsc_code', schema='identity')
    op.drop_column('company', 'account_number', schema='identity')
    op.drop_column('company', 'account_holder_name', schema='identity')
    op.drop_column('company', 'bank_branch', schema='identity')
    op.drop_column('company', 'bank_name', schema='identity')
