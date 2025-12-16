import uuid
from sqlalchemy.orm import Session
from app.billing_service.models import Invoice, InvoiceItem
from app.billing_service.schemas import InvoiceCreate, InvoiceItemCreate


def create_invoice(db: Session, payload: InvoiceCreate) -> Invoice:
    invoice = Invoice(
        id=uuid.uuid4(),
        invoice_date=payload.invoice_date,
        gstin_id=payload.gstin_id,
        customer_id=payload.customer_id,
        status="DRAFT",
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def add_invoice_item(
    db: Session,
    invoice: Invoice,
    payload: InvoiceItemCreate,
) -> InvoiceItem:
    taxable_value = payload.quantity * payload.rate

    item = InvoiceItem(
        id=uuid.uuid4(),
        invoice_id=invoice.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        rate=payload.rate,
        taxable_value=taxable_value,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_invoice(db: Session, invoice_id):
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()


def get_invoice_items(db: Session, invoice_id):
    return (
        db.query(InvoiceItem)
        .filter(InvoiceItem.invoice_id == invoice_id)
        .all()
    )
