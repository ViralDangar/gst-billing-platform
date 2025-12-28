from sqlalchemy.orm import Session
from uuid import UUID

from app.billing_service.models import Invoice, InvoiceItem
from app.tax_engine_service.models import InvoiceTax
from app.identity_service.models import GSTIN, Company
from app.master_data_service.models import Customer, Product


def get_invoice_preview(db: Session, invoice_id: UUID):
    """
    Get invoice preview data for PDF generation or display.

    Fetches complete invoice data including company, customer, items, and taxes.

    Args:
        db: Database session
        invoice_id: UUID of the invoice

    Returns:
        dict: Complete invoice data for preview/PDF generation

    Raises:
        ValueError: If invoice not found or not finalized
    """
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

    # Group taxes by type for easier access in PDF
    tax_map = {}
    for tax in taxes:
        if tax.tax_type not in tax_map:
            tax_map[tax.tax_type] = {"rate": tax.tax_rate, "amount": 0}
        tax_map[tax.tax_type]["amount"] += tax.tax_amount

    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date,
        "po_number": invoice.po_number or "",
        "seller_name": company.name,
        "seller_address": company.address,
        "seller_mobile": company.mobile_number or "",
        "seller_email": company.email_id or "",
        "seller_gstin": gstin.gst_number,
        "seller_state": gstin.state_code,
        "seller_bank_details": {
            "bank_name": company.bank_name,
            "bank_branch": company.bank_branch,
            "account_holder_name": company.account_holder_name,
            "account_number": company.account_number,
            "ifsc_code": company.ifsc_code,
        },


        "customer_name": customer.name,
        "customer_gstin": customer.gstin,
        "customer_address": customer.address,
        "customer_state": customer.state,

        "items": [
            {
                "product_name": product.name,
                "hsn_sac": product.hsn_sac,
                "quantity": float(item.quantity),
                "rate": float(item.rate),
                "taxable_value": float(item.taxable_value),
                "gst_rate": float(product.gst_rate),
            }
            for item, product in items
        ],

        "taxes": [
            {
                "tax_type": tax.tax_type,
                "tax_rate": float(tax.tax_rate),
                "tax_amount": float(tax.tax_amount),
            }
            for tax in taxes
        ],

        "tax_summary": {
            tax_type: {
                "rate": float(data["rate"]),
                "amount": float(data["amount"])
            }
            for tax_type, data in tax_map.items()
        },

        "taxable_total": float(invoice.taxable_total),
        "tax_total": float(invoice.tax_total),
        "round_off": float(invoice.round_off),
        "grand_total": float(invoice.grand_total),
    }
