"""
Identity Router Module

This module defines all API endpoints for identity management including
company and GSTIN operations.
"""

import logging
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.identity_service import service
from app.identity_service.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    GSTINCreate,
    GSTINResponse,
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/identity", tags=["Company & GSTIN"])


# ========== COMPANY ENDPOINTS ==========

@router.get("/health")
def identity_health():
    """Health check endpoint for identity service."""
    return {"service": "identity", "status": "ok"}


@router.post(
    "/company",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    """
    Create a new company.

    Note: Only one company is allowed per system.

    Args:
        payload: Company creation data
        db: Database session

    Returns:
        CompanyResponse: Created company

    Raises:
        HTTPException 400: If company already exists or validation fails
        HTTPException 500: If database operation fails
    """
    try:
        logger.info("Creating company")

        # Check if company already exists
        existing = service.get_company(db)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Company already exists. Only one company is allowed per system.",
            )

        return service.create_company(db, payload)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error creating company: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating company: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error creating company: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/company", response_model=CompanyResponse)
def get_company(db: Session = Depends(get_db)):
    """
    Retrieve the company.

    Args:
        db: Database session

    Returns:
        CompanyResponse: Company details

    Raises:
        HTTPException 404: If company not found
        HTTPException 500: If database operation fails
    """
    try:
        logger.info("Retrieving company")
        company = service.get_company(db)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving company: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error retrieving company: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.put("/company", response_model=CompanyResponse)
def update_company(
    payload: CompanyUpdate,
    db: Session = Depends(get_db),
):
    """
    Update the existing company.

    Only updates fields provided in the request body.

    Args:
        payload: Company update data
        db: Database session

    Returns:
        CompanyResponse: Updated company

    Raises:
        HTTPException 404: If company not found
        HTTPException 400: If validation fails
        HTTPException 500: If database operation fails
    """
    try:
        logger.info("Updating company")

        # Fetch company
        company = service.get_company(db)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        return service.update_company(db, company, payload)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating company: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error updating company: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error updating company: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# ========== GSTIN ENDPOINTS ==========

@router.post(
    "/company/{company_id}/gstins",
    response_model=GSTINResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_gstin(
    company_id: UUID,
    payload: GSTINCreate,
    db: Session = Depends(get_db),
):
    """
    Add a new GSTIN for a company.

    A company can have multiple GSTINs for different states.

    Args:
        company_id: UUID of the company
        payload: GSTIN creation data
        db: Database session

    Returns:
        GSTINResponse: Created GSTIN

    Raises:
        HTTPException 400: If validation fails or GSTIN already exists
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Adding GSTIN to company: {company_id}")
        return service.create_gstin(db, company_id, payload)

    except ValueError as e:
        logger.error(f"Validation error creating GSTIN: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating GSTIN: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error creating GSTIN: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/company/{company_id}/gstins")
def list_gstins(
    company_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all GSTINs for a company with pagination.

    Args:
        company_id: UUID of the company
        page: Page number (starts from 1)
        page_size: Number of items per page (max 100)
        db: Database session

    Returns:
        dict: Paginated GSTIN list with metadata

    Raises:
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Listing GSTINs for company {company_id} (page={page}, page_size={page_size})")

        # Calculate offset
        skip = (page - 1) * page_size

        # Fetch GSTINs and total count
        gstins = service.list_gstins(db, company_id, skip=skip, limit=page_size)
        total = service.count_gstins(db, company_id)

        # Calculate total pages
        total_pages = ceil(total / page_size) if total > 0 else 0

        return {
            "items": gstins,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error listing GSTINs: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error listing GSTINs: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
