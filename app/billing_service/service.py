import uuid
from sqlalchemy.orm import Session
from app.billing_service.models import Invoice, InvoiceItem
from app.billing_service.schemas import InvoiceCreate, InvoiceItemCreate
from app.identity_service.models import GSTIN


def create_invoice(db: Session, payload: InvoiceCreate) -> Invoice:
    gstin_id = payload.gstin_id

    # If no GSTIN provided, use the first available GSTIN
    if not gstin_id:
        first_gstin = db.query(GSTIN).first()
        if not first_gstin:
            raise ValueError("No GSTIN found in the system. Please create a GSTIN first.")
        gstin_id = first_gstin.id

    invoice = Invoice(
        id=uuid.uuid4(),
        invoice_date=payload.invoice_date,
        gstin_id=gstin_id,
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

def get_invoices(db: Session):
    return db.query(Invoice).all()

def get_invoice_items(db: Session, invoice_id):
    return (
        db.query(InvoiceItem)
        .filter(InvoiceItem.invoice_id == invoice_id)
        .all()
    )
