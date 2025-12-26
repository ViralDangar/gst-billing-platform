"""
Billing Router Module

This module defines all API endpoints for invoice management,
including CRUD operations and invoice finalization.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from typing import List
from math import ceil
import logging

from app.billing_service.finalize import finalize_invoice
from app.billing_service.schemas import InvoiceFinalizeResponse
from app.core.database import get_db
from app.billing_service import service
from app.billing_service.schemas import (
    InvoiceCreate,
    InvoiceItemCreate,
    InvoiceResponse,
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing/invoices", tags=["Invoices"])

@router.get("/health")
def billing_health():
    """Health check endpoint for billing service."""
    return {"service": "billing", "status": "ok"}


@router.post(
    "/",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    """
    Create a new invoice.

    Creates a new invoice in DRAFT status. If GSTIN is not provided,
    it automatically assigns the first available GSTIN from the system.

    Args:
        payload: Invoice creation data
        db: Database session

    Returns:
        InvoiceResponse: Created invoice with empty items list

    Raises:
        HTTPException 400: If validation fails or no GSTIN available
        HTTPException 500: If database operation fails
    """
    try:
        logger.info("Creating new invoice")
        invoice = service.create_invoice(db, payload)
        return {
            **invoice.__dict__,
            "items": [],
        }
    except ValueError as e:
        logger.error(f"Validation error creating invoice: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error creating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/{invoice_id}/items")
def add_invoice_item(
    invoice_id: UUID,
    payload: InvoiceItemCreate,
    db: Session = Depends(get_db),
):
    """
    Add an item to an existing invoice.

    Only DRAFT invoices can have items added. The taxable value is
    automatically calculated based on quantity and rate.

    Args:
        invoice_id: UUID of the invoice
        payload: Invoice item data
        db: Database session

    Returns:
        InvoiceItem: Created invoice item

    Raises:
        HTTPException 404: If invoice not found
        HTTPException 400: If invoice is not in DRAFT status or validation fails
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Adding item to invoice: {invoice_id}")

        # Fetch invoice
        invoice = service.get_invoice(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Validate invoice status
        if invoice.status != "DRAFT":
            raise HTTPException(
                status_code=400,
                detail="Cannot modify finalized invoice",
            )

        return service.add_invoice_item(db, invoice, payload)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error adding invoice item: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error adding invoice item: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error adding invoice item: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single invoice by ID.

    Fetches the invoice along with all its items.

    Args:
        invoice_id: UUID of the invoice
        db: Database session

    Returns:
        InvoiceResponse: Invoice with items

    Raises:
        HTTPException 404: If invoice not found
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Retrieving invoice: {invoice_id}")

        # Fetch invoice
        invoice = service.get_invoice(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Fetch invoice items
        items = service.get_invoice_items(db, invoice_id)

        return {
            **invoice.__dict__,
            "items": items,
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error retrieving invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/")
def list_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all invoices with pagination.

    Retrieves invoices in paginated format for better performance.

    Args:
        page: Page number (starts from 1)
        page_size: Number of items per page (max 100)
        db: Database session

    Returns:
        dict: Paginated invoice list with metadata

    Raises:
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Listing invoices (page={page}, page_size={page_size})")

        # Calculate offset
        skip = (page - 1) * page_size

        # Fetch invoices and total count
        invoices = service.get_invoices(db, skip=skip, limit=page_size)
        total = service.count_invoices(db)

        # Calculate total pages
        total_pages = ceil(total / page_size) if total > 0 else 0

        return {
            "items": invoices,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error listing invoices: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error listing invoices: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
@router.post(
    "/{invoice_id}/finalize",
    response_model=InvoiceFinalizeResponse,
)
def finalize_invoice_api(
    invoice_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Finalize an invoice.

    Changes the invoice status from DRAFT to FINALIZED and generates
    a unique invoice number. Once finalized, the invoice cannot be modified.

    Args:
        invoice_id: UUID of the invoice to finalize
        db: Database session

    Returns:
        InvoiceFinalizeResponse: Finalized invoice with invoice number

    Raises:
        HTTPException 400: If invoice cannot be finalized (validation error)
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Finalizing invoice: {invoice_id}")
        result = finalize_invoice(db, invoice_id)
        logger.info(f"Invoice finalized successfully: {invoice_id}")
        return result

    except ValueError as e:
        logger.error(f"Validation error finalizing invoice: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error finalizing invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error finalizing invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
