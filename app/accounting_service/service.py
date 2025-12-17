import uuid
from decimal import Decimal
from sqlalchemy.orm import Session

from app.accounting_service.models import (
    Ledger,
    Voucher,
    VoucherEntry,
)
from app.billing_service.models import Invoice
from app.tax_engine_service.models import InvoiceTax
from app.master_data_service.models import Customer


def get_ledger(db: Session, name: str):
    ledger = db.query(Ledger).filter(Ledger.name == name).first()
    if not ledger:
        raise ValueError(f"Ledger not found: {name}")
    return ledger


def create_sales_voucher(db: Session, invoice_id):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Invoice not found")

    if invoice.status != "FINAL":
        raise ValueError("Voucher can be created only for FINAL invoices")

    # Prevent duplicate voucher
    existing = (
        db.query(Voucher)
        .filter(Voucher.reference_invoice_id == invoice.id)
        .first()
    )
    if existing:
        return existing

    customer = db.query(Customer).filter(
        Customer.id == invoice.customer_id
    ).first()

    voucher = Voucher(
        id=uuid.uuid4(),
        reference_invoice_id=invoice.id,
        voucher_type="SALES",
        voucher_date=invoice.invoice_date,
    )
    db.add(voucher)
    db.flush()

    entries = []

    # 1. Customer Debit
    customer_ledger = get_ledger(db, customer.name)

    entries.append(
        VoucherEntry(
            id=uuid.uuid4(),
            voucher_id=voucher.id,
            ledger_id=customer_ledger.id,
            debit_amount=invoice.grand_total,
            credit_amount=Decimal("0.00"),
        )
    )

    # 2. Sales Credit
    sales_ledger = get_ledger(db, "Sales")

    entries.append(
        VoucherEntry(
            id=uuid.uuid4(),
            voucher_id=voucher.id,
            ledger_id=sales_ledger.id,
            debit_amount=Decimal("0.00"),
            credit_amount=invoice.taxable_total,
        )
    )

    # 3. Tax Credits
    taxes = (
        db.query(InvoiceTax)
        .filter(InvoiceTax.invoice_id == invoice.id)
        .all()
    )

    for tax in taxes:
        tax_ledger = get_ledger(db, f"Output {tax.tax_type}")
        entries.append(
            VoucherEntry(
                id=uuid.uuid4(),
                voucher_id=voucher.id,
                ledger_id=tax_ledger.id,
                debit_amount=Decimal("0.00"),
                credit_amount=tax.tax_amount,
            )
        )

    for entry in entries:
        db.add(entry)

    db.commit()
    db.refresh(voucher)

    return voucher
