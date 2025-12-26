"""
Tax Engine Service Module

This module handles all GST (Goods and Services Tax) calculations for invoices.
It determines whether to apply CGST+SGST (intra-state) or IGST (inter-state)
based on seller and customer locations.
"""

import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from uuid import UUID

from app.billing_service.models import Invoice, InvoiceItem
from app.tax_engine_service.models import InvoiceTax
from app.identity_service.models import GSTIN
from app.master_data_service.models import Customer, Product

# Configure logging
logger = logging.getLogger(__name__)


def calculate_gst(db: Session, invoice_id: UUID):
    """
    Calculate GST (Goods and Services Tax) for an invoice.

    Determines the applicable tax type based on transaction type:
    - Intra-state (same state): CGST + SGST (each half of total GST)
    - Inter-state (different states): IGST (full GST)

    The state is determined by comparing seller's GSTIN state code with
    customer's state code (first 2 characters).

    Args:
        db: Database session
        invoice_id: UUID of the invoice to calculate tax for

    Returns:
        dict: Contains invoice_id, taxable_total, tax_total, and grand_total

    Raises:
        ValueError: If validation fails (invoice not found, not in DRAFT status, etc.)
        SQLAlchemyError: If database operation fails
    """
    try:
        logger.info(f"Calculating GST for invoice: {invoice_id}")

        # Fetch invoice
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            logger.error(f"Invoice not found: {invoice_id}")
            raise ValueError("Invoice not found")

        # Validate invoice status
        if invoice.status != "DRAFT":
            logger.error(f"Invoice not in DRAFT status: {invoice.status}")
            raise ValueError("GST can be calculated only for DRAFT invoices")

        # Validate GSTIN assignment
        if not invoice.gstin_id:
            logger.error("Invoice does not have GSTIN associated")
            raise ValueError("Invoice does not have a GSTIN associated")

        # Fetch seller GSTIN
        seller_gstin = db.query(GSTIN).filter(GSTIN.id == invoice.gstin_id).first()
        if not seller_gstin:
            logger.error(f"Seller GSTIN not found: {invoice.gstin_id}")
            raise ValueError("Seller GSTIN not found")

        # Fetch customer
        customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
        if not customer:
            logger.error(f"Customer not found: {invoice.customer_id}")
            raise ValueError("Customer not found")

        # Fetch invoice items with products
        items = (
            db.query(InvoiceItem, Product)
            .join(Product, InvoiceItem.product_id == Product.id)
            .filter(InvoiceItem.invoice_id == invoice.id)
            .all()
        )

        if not items:
            logger.error(f"Invoice has no items: {invoice_id}")
            raise ValueError("Invoice has no items")

        # Cleanup old tax records (recalculate allowed in draft)
        deleted_count = db.query(InvoiceTax).filter(
            InvoiceTax.invoice_id == invoice.id
        ).delete()
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} existing tax records for recalculation")

        # Initialize totals
        taxable_total = Decimal("0.00")
        tax_total = Decimal("0.00")

        # Determine transaction type (intra-state vs inter-state)
        same_state = seller_gstin.state_code == customer.state[:2]
        logger.info(f"Transaction type: {'Intra-state (CGST+SGST)' if same_state else 'Inter-state (IGST)'}")

        # Calculate tax for each item
        for item, product in items:
            taxable_total += item.taxable_value

            # Get GST rate from product
            gst_rate = product.gst_rate
            logger.debug(f"Item {item.id}: Rate={gst_rate}%, Taxable={item.taxable_value}")

            # Calculate tax amount
            tax_amount = (item.taxable_value * gst_rate) / Decimal("100")

            if same_state:
                # Intra-state: Split into CGST and SGST
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
                # Inter-state: Apply IGST
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

        # Calculate grand total
        grand_total = taxable_total + tax_total

        # Update invoice with calculated totals
        invoice.taxable_total = taxable_total
        invoice.tax_total = tax_total
        invoice.round_off = Decimal("0.00")
        invoice.grand_total = grand_total

        # Persist changes
        db.commit()

        logger.info(f"GST calculation completed for invoice {invoice_id}: "
                   f"Taxable={taxable_total}, Tax={tax_total}, Grand Total={grand_total}")

        return {
            "invoice_id": invoice.id,
            "taxable_total": float(taxable_total),
            "tax_total": float(tax_total),
            "grand_total": float(grand_total),
        }

    except ValueError:
        # Re-raise validation errors as-is
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error calculating GST: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error calculating GST: {str(e)}")
        raise
