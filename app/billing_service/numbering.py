import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from datetime import date

from app.billing_service.models import InvoiceSequence


def get_financial_year(invoice_date: date) -> str:
    year = invoice_date.year
    if invoice_date.month >= 4:
        return f"{year}-{str(year+1)[-2:]}"
    return f"{year-1}-{str(year)[-2:]}"


def generate_invoice_number(
    db: Session,
    gstin_id,
    invoice_date: date,
    prefix: str = "GST",
):
    """
    Generate a unique invoice number based on financial year.

    Format: PREFIX/FY/NNNNNN (e.g., GST/2025-26/000001)

    Args:
        db: Database session
        gstin_id: GSTIN ID (not used currently, kept for backward compatibility)
        invoice_date: Date of the invoice
        prefix: Prefix for invoice number (default: "GST")

    Returns:
        str: Generated invoice number
    """
    fy = get_financial_year(invoice_date)

    # Fetch or create sequence for the financial year
    # Note: Not filtering by gstin_id as it's optional
    seq = (
        db.query(InvoiceSequence)
        .with_for_update()
        .filter(InvoiceSequence.financial_year == fy)
        .first()
    )

    if not seq:
        seq = InvoiceSequence(
            id=uuid.uuid4(),
            financial_year=fy,
            last_sequence=1,
        )
        db.add(seq)
        sequence_number = 1
    else:
        seq.last_sequence += 1
        sequence_number = seq.last_sequence

    db.commit()

    return f"{prefix}/{fy}/{sequence_number:06d}"
