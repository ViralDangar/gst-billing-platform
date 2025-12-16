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
    fy = get_financial_year(invoice_date)

    seq = (
        db.query(InvoiceSequence)
        .with_for_update()
        .filter(
            InvoiceSequence.gstin_id == gstin_id,
            InvoiceSequence.financial_year == fy,
        )
        .first()
    )

    if not seq:
        seq = InvoiceSequence(
            id=uuid.uuid4(),
            gstin_id=gstin_id,
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
