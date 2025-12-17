from sqlalchemy.orm import Session
from uuid import UUID

from app.billing_service.models import Invoice, InvoiceItem
from app.tax_engine_service.models import InvoiceTax
from app.billing_service.numbering import generate_invoice_number


def finalize_invoice(db: Session, invoice_id: UUID):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Invoice not found")

    if invoice.status != "DRAFT":
        raise ValueError("Invoice already finalized")

    items = (
        db.query(InvoiceItem)
        .filter(InvoiceItem.invoice_id == invoice.id)
        .count()
    )

    if items == 0:
        raise ValueError("Invoice has no items")

    tax_count = (
        db.query(InvoiceTax)
        .filter(InvoiceTax.invoice_id == invoice.id)
        .count()
    )

    if tax_count == 0:
        raise ValueError("GST not calculated for invoice")

    # Generate invoice number (ONLY HERE)
    invoice.invoice_number = generate_invoice_number(
        db=db,
        gstin_id=invoice.gstin_id,
        invoice_date=invoice.invoice_date,
    )

    invoice.status = "FINAL"
    db.commit()
    db.refresh(invoice)

    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "status": invoice.status,
    }
