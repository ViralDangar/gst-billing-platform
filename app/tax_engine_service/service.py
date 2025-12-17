from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import UUID

from app.billing_service.models import Invoice, InvoiceItem
from app.tax_engine_service.models import InvoiceTax
from app.identity_service.models import GSTIN
from app.master_data_service.models import Customer
import uuid


def calculate_gst(db: Session, invoice_id: UUID):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Invoice not found")

    if invoice.status != "DRAFT":
        raise ValueError("GST can be calculated only for DRAFT invoices")

    # Fetch seller GSTIN
    seller_gstin = db.query(GSTIN).filter(GSTIN.id == invoice.gstin_id).first()

    # Fetch customer
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()

    items = (
        db.query(InvoiceItem)
        .filter(InvoiceItem.invoice_id == invoice.id)
        .all()
    )

    if not items:
        raise ValueError("Invoice has no items")

    # Cleanup old tax records (recalculate allowed in draft)
    db.query(InvoiceTax).filter(
        InvoiceTax.invoice_id == invoice.id
    ).delete()

    taxable_total = Decimal("0.00")
    tax_total = Decimal("0.00")

    same_state = seller_gstin.state_code == customer.state[:2]

    for item in items:
        taxable_total += item.taxable_value

        # Fetch GST rate from product
        gst_rate = item.rate * Decimal("0")  # placeholder safeguard
        gst_rate = item.product.gst_rate

        tax_amount = (item.taxable_value * gst_rate) / Decimal("100")

        if same_state:
            half_tax = tax_amount / Decimal("2")

            for tax_type in ["CGST", "SGST"]:
                db.add(
                    InvoiceTax(
                        id=uuid.uuid4(),
                        invoice_id=invoice.id,
                        tax_type=tax_type,
                        tax_rate=gst_rate / 2,
                        tax_amount=half_tax,
                    )
                )
                tax_total += half_tax
        else:
            db.add(
                InvoiceTax(
                    id=uuid.uuid4(),
                    invoice_id=invoice.id,
                    tax_type="IGST",
                    tax_rate=gst_rate,
                    tax_amount=tax_amount,
                )
            )
            tax_total += tax_amount

    grand_total = taxable_total + tax_total

    invoice.taxable_total = taxable_total
    invoice.tax_total = tax_total
    invoice.round_off = Decimal("0.00")
    invoice.grand_total = grand_total

    db.commit()

    return {
        "invoice_id": invoice.id,
        "taxable_total": float(taxable_total),
        "tax_total": float(tax_total),
        "grand_total": float(grand_total),
    }
