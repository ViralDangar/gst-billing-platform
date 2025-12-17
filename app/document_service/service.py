from sqlalchemy.orm import Session
from uuid import UUID

from app.billing_service.models import Invoice, InvoiceItem
from app.tax_engine_service.models import InvoiceTax
from app.identity_service.models import GSTIN, Company
from app.master_data_service.models import Customer, Product


def get_invoice_preview(db: Session, invoice_id: UUID):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Invoice not found")

    if invoice.status != "FINAL":
        raise ValueError("Invoice must be finalized for preview")

    gstin = db.query(GSTIN).filter(GSTIN.id == invoice.gstin_id).first()
    company = db.query(Company).filter(Company.id == gstin.company_id).first()
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()

    items = (
        db.query(InvoiceItem, Product)
        .join(Product, Product.id == InvoiceItem.product_id)
        .filter(InvoiceItem.invoice_id == invoice.id)
        .all()
    )

    taxes = (
        db.query(InvoiceTax)
        .filter(InvoiceTax.invoice_id == invoice.id)
        .all()
    )

    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date,

        "seller_name": company.name,
        "seller_gstin": gstin.gst_number,

        "customer_name": customer.name,
        "customer_gstin": customer.gstin,
        "customer_address": customer.address,

        "items": [
            {
                "product_name": product.name,
                "hsn_sac": product.hsn_sac,
                "quantity": item.quantity,
                "rate": item.rate,
                "taxable_value": item.taxable_value,
            }
            for item, product in items
        ],

        "taxes": [
            {
                "tax_type": tax.tax_type,
                "tax_rate": tax.tax_rate,
                "tax_amount": tax.tax_amount,
            }
            for tax in taxes
        ],

        "taxable_total": invoice.taxable_total,
        "tax_total": invoice.tax_total,
        "round_off": invoice.round_off,
        "grand_total": invoice.grand_total,
    }
