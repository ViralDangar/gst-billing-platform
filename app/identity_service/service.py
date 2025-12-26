"""
Identity Service Module

This module handles all business logic for identity management including
company and GSTIN (Goods and Services Tax Identification Number) operations.
"""

import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.identity_service.models import Company, GSTIN
from app.identity_service.schemas import (
    CompanyCreate,
    CompanyUpdate,
    GSTINCreate,
)

# Configure logging
logger = logging.getLogger(__name__)


# ========== COMPANY OPERATIONS ==========

def create_company(db: Session, payload: CompanyCreate) -> Company:
    """
    Create a new company.

    Note: Only one company is allowed per system.

    Args:
        db: Database session
        payload: Company creation data

    Returns:
        Company: Newly created company object

    Raises:
        ValueError: If validation fails
        SQLAlchemyError: If database operation fails
    """
    try:
        logger.info(f"Creating company: {payload.name}")

        company = Company(
            id=uuid.uuid4(),
            name=payload.name,
            address=payload.address,
            logo_url=payload.logo_url,
            default_bank_details=payload.default_bank_details,
        )

        db.add(company)
        db.commit()
        db.refresh(company)

        logger.info(f"Company created successfully: {company.id}")
        return company

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating company: {str(e)}")
        raise ValueError("Company already exists or constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating company: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating company: {str(e)}")
        raise


def get_company(db: Session):
    """
    Retrieve the company (only one company per system).

    Args:
        db: Database session

    Returns:
        Company or None: Company object if exists, None otherwise

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        company = db.query(Company).first()
        if company:
            logger.info(f"Company retrieved: {company.id}")
        else:
            logger.warning("No company found in system")
        return company

    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving company: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving company: {str(e)}")
        raise


def update_company(db: Session, company: Company, payload: CompanyUpdate):
    """
    Update the existing company.

    Only updates fields that are provided in the payload.

    Args:
        db: Database session
        company: Company object to update
        payload: Company update data

    Returns:
        Company: Updated company object

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        logger.info(f"Updating company: {company.id}")

        # Update only provided fields
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(company, field, value)

        db.commit()
        db.refresh(company)

        logger.info(f"Company updated successfully: {company.id}")
        return company

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating company: {str(e)}")
        raise ValueError("Update failed due to constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating company: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating company: {str(e)}")
        raise


# ========== GSTIN OPERATIONS ==========

def create_gstin(db: Session, company_id, payload: GSTINCreate) -> GSTIN:
    """
    Create a new GSTIN for a company.

    A company can have multiple GSTINs for different states.

    Args:
        db: Database session
        company_id: UUID of the company
        payload: GSTIN creation data

    Returns:
        GSTIN: Newly created GSTIN object

    Raises:
        ValueError: If validation fails or GSTIN already exists
        SQLAlchemyError: If database operation fails
    """
    try:
        logger.info(f"Creating GSTIN: {payload.gst_number} for company: {company_id}")

        gstin = GSTIN(
            id=uuid.uuid4(),
            company_id=company_id,
            gst_number=payload.gst_number,
            state_code=payload.state_code,
        )

        db.add(gstin)
        db.commit()
        db.refresh(gstin)

        logger.info(f"GSTIN created successfully: {gstin.id}")
        return gstin

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating GSTIN: {str(e)}")
        raise ValueError("GSTIN number already exists or constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating GSTIN: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating GSTIN: {str(e)}")
        raise


def list_gstins(db: Session, company_id, skip: int = 0, limit: int = 100):
    """
    Retrieve all GSTINs for a company with pagination.

    Args:
        db: Database session
        company_id: UUID of the company
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return

    Returns:
        list: List of GSTIN objects

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        gstins = (
            db.query(GSTIN)
            .filter(GSTIN.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.info(f"Retrieved {len(gstins)} GSTINs for company {company_id} (skip={skip}, limit={limit})")
        return gstins

    except SQLAlchemyError as e:
        logger.error(f"Database error listing GSTINs: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing GSTINs: {str(e)}")
        raise


def count_gstins(db: Session, company_id) -> int:
    """
    Get total count of GSTINs for a company.

    Args:
        db: Database session
        company_id: UUID of the company

    Returns:
        int: Total number of GSTINs

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        total = db.query(GSTIN).filter(GSTIN.company_id == company_id).count()
        logger.info(f"Total GSTINs count for company {company_id}: {total}")
        return total

    except SQLAlchemyError as e:
        logger.error(f"Database error counting GSTINs: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error counting GSTINs: {str(e)}")
        raise
