"""
Billing Service Module

This module handles all business logic related to invoice management,
including invoice creation, item management, and invoice retrieval.
"""

import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.billing_service.models import Invoice, InvoiceItem
from app.billing_service.schemas import InvoiceCreate, InvoiceItemCreate
from app.identity_service.models import GSTIN

# Configure logging
logger = logging.getLogger(__name__)


def create_invoice(db: Session, payload: InvoiceCreate) -> Invoice:
    """
    Create a new invoice in DRAFT status.

    If no GSTIN is provided, automatically assigns the first available GSTIN
    from the system.

    Args:
        db: Database session
        payload: Invoice creation data

    Returns:
        Invoice: Newly created invoice object

    Raises:
        ValueError: If no GSTIN exists in the system when auto-assignment is needed
        SQLAlchemyError: If database operation fails
    """
    try:
        gstin_id = payload.gstin_id

        # Auto-assign GSTIN if not provided (optional - allows None if no GSTIN available)
        if not gstin_id:
            logger.info("No GSTIN provided, attempting auto-assignment")
            first_gstin = db.query(GSTIN).first()
            if first_gstin:
                gstin_id = first_gstin.id
                logger.info(f"Auto-assigned GSTIN: {gstin_id}")
            else:
                logger.warning("No GSTIN found in system, creating invoice without GSTIN")
                gstin_id = None

        # Create invoice object
        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_date=payload.invoice_date,
            gstin_id=gstin_id,
            customer_id=payload.customer_id,
            status="DRAFT",
        )

        # Persist to database
        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        logger.info(f"Invoice created successfully: {invoice.id}")
        return invoice

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating invoice: {str(e)}")
        raise ValueError("Invalid customer_id or gstin_id provided")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating invoice: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating invoice: {str(e)}")
        raise


def add_invoice_item(
    db: Session,
    invoice: Invoice,
    payload: InvoiceItemCreate,
) -> InvoiceItem:
    """
    Add an item to an existing invoice.

    Automatically calculates the taxable value based on quantity and rate.

    Args:
        db: Database session
        invoice: Invoice object to add item to
        payload: Invoice item data

    Returns:
        InvoiceItem: Newly created invoice item

    Raises:
        ValueError: If product_id is invalid
        SQLAlchemyError: If database operation fails
    """
    try:
        # Calculate taxable value
        taxable_value = payload.quantity * payload.rate

        # Create invoice item
        item = InvoiceItem(
            id=uuid.uuid4(),
            invoice_id=invoice.id,
            product_id=payload.product_id,
            quantity=payload.quantity,
            rate=payload.rate,
            taxable_value=taxable_value,
        )

        # Persist to database
        db.add(item)
        db.commit()
        db.refresh(item)

        logger.info(f"Invoice item added: {item.id} to invoice: {invoice.id}")
        return item

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error adding invoice item: {str(e)}")
        raise ValueError("Invalid product_id provided")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error adding invoice item: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error adding invoice item: {str(e)}")
        raise


def get_invoice(db: Session, invoice_id):
    """
    Retrieve a single invoice by ID.

    Args:
        db: Database session
        invoice_id: UUID of the invoice

    Returns:
        Invoice or None: Invoice object if found, None otherwise

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            logger.info(f"Invoice retrieved: {invoice_id}")
        else:
            logger.warning(f"Invoice not found: {invoice_id}")
        return invoice

    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving invoice: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving invoice: {str(e)}")
        raise


def get_invoices(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of invoices with pagination.

    Args:
        db: Database session
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return

    Returns:
        list: List of Invoice objects

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        invoices = db.query(Invoice).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(invoices)} invoices (skip={skip}, limit={limit})")
        return invoices

    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving invoices: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving invoices: {str(e)}")
        raise


def get_invoice_items(db: Session, invoice_id):
    """
    Retrieve all items for a specific invoice.

    Args:
        db: Database session
        invoice_id: UUID of the invoice

    Returns:
        list: List of InvoiceItem objects

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        items = (
            db.query(InvoiceItem)
            .filter(InvoiceItem.invoice_id == invoice_id)
            .all()
        )
        logger.info(f"Retrieved {len(items)} items for invoice: {invoice_id}")
        return items

    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving invoice items: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving invoice items: {str(e)}")
        raise


def count_invoices(db: Session) -> int:
    """
    Get total count of invoices.

    Args:
        db: Database session

    Returns:
        int: Total number of invoices

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        total = db.query(Invoice).count()
        logger.info(f"Total invoices count: {total}")
        return total

    except SQLAlchemyError as e:
        logger.error(f"Database error counting invoices: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error counting invoices: {str(e)}")
        raise
