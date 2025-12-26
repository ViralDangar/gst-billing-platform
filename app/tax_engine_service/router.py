"""
Tax Engine Router Module

This module defines API endpoints for GST (Goods and Services Tax) calculations.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.tax_engine_service.schemas import (
    TaxCalculationRequest,
    TaxCalculationResponse,
)
from app.tax_engine_service.service import calculate_gst

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tax", tags=["Tax Engine"])


@router.post(
    "/calculate",
    response_model=TaxCalculationResponse,
)
def calculate_tax(payload: TaxCalculationRequest, db: Session = Depends(get_db)):
    """
    Calculate GST for an invoice.

    Computes the applicable GST (CGST+SGST for intra-state or IGST for inter-state)
    and updates the invoice with tax totals.

    Args:
        payload: Contains invoice_id for tax calculation
        db: Database session

    Returns:
        TaxCalculationResponse: Calculated tax details

    Raises:
        HTTPException 400: If validation fails (invoice not found, not DRAFT, etc.)
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Tax calculation request for invoice: {payload.invoice_id}")
        result = calculate_gst(db, payload.invoice_id)
        logger.info(f"Tax calculation successful for invoice: {payload.invoice_id}")
        return result

    except ValueError as e:
        logger.error(f"Validation error in tax calculation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error in tax calculation: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error in tax calculation: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
