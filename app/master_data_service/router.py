"""
Master Data Router Module

This module defines all API endpoints for master data management including
products and customers with full CRUD operations.
"""

import logging
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.master_data_service import service
from app.master_data_service.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)

# Configure logging
logger = logging.getLogger(__name__)

product_router = APIRouter(prefix="/masters/products", tags=["Product Master"])
customer_router = APIRouter(prefix="/masters/customer", tags=["Customer Master"])



# ========== PRODUCT ENDPOINTS ==========

@product_router.get("/health")
def masters_health():
    """Health check endpoint for master data service."""
    return {"service": "master-data", "status": "ok"}


@product_router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.

    Args:
        payload: Product creation data
        db: Database session

    Returns:
        ProductResponse: Created product

    Raises:
        HTTPException 400: If validation fails
        HTTPException 500: If database operation fails
    """
    try:
        logger.info("Creating new product")
        return service.create_product(db, payload)

    except ValueError as e:
        logger.error(f"Validation error creating product: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@product_router.get("")
def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all active products with pagination.

    Args:
        page: Page number (starts from 1)
        page_size: Number of items per page (max 100)
        db: Database session

    Returns:
        dict: Paginated product list with metadata

    Raises:
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Listing products (page={page}, page_size={page_size})")

        # Calculate offset
        skip = (page - 1) * page_size

        # Fetch products and total count
        products = service.list_products(db, skip=skip, limit=page_size)
        total = service.count_products(db)

        # Calculate total pages
        total_pages = ceil(total / page_size) if total > 0 else 0

        return {
            "items": products,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error listing products: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error listing products: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@product_router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single product by ID.

    Args:
        product_id: UUID of the product
        db: Database session

    Returns:
        ProductResponse: Product details

    Raises:
        HTTPException 404: If product not found
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Retrieving product: {product_id}")
        product = service.get_product(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving product: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error retrieving product: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@product_router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing product.

    Only updates fields provided in the request body.

    Args:
        product_id: UUID of the product to update
        payload: Product update data
        db: Database session

    Returns:
        ProductResponse: Updated product

    Raises:
        HTTPException 404: If product not found
        HTTPException 400: If validation fails
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Updating product: {product_id}")

        # Fetch product
        product = service.get_product(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return service.update_product(db, product, payload)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating product: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error updating product: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error updating product: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# ========== CUSTOMER ENDPOINTS ==========

@customer_router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer.

    Args:
        payload: Customer creation data
        db: Database session

    Returns:
        CustomerResponse: Created customer

    Raises:
        HTTPException 400: If validation fails
        HTTPException 500: If database operation fails
    """
    try:
        logger.info("Creating new customer")
        return service.create_customer(db, payload)

    except ValueError as e:
        logger.error(f"Validation error creating customer: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating customer: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error creating customer: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@customer_router.get("")
def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List all active customers with pagination.

    Args:
        page: Page number (starts from 1)
        page_size: Number of items per page (max 100)
        db: Database session

    Returns:
        dict: Paginated customer list with metadata

    Raises:
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Listing customers (page={page}, page_size={page_size})")

        # Calculate offset
        skip = (page - 1) * page_size

        # Fetch customers and total count
        customers = service.list_customers(db, skip=skip, limit=page_size)
        total = service.count_customers(db)

        # Calculate total pages
        total_pages = ceil(total / page_size) if total > 0 else 0

        return {
            "items": customers,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error listing customers: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error listing customers: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@customer_router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single customer by ID.

    Args:
        customer_id: UUID of the customer
        db: Database session

    Returns:
        CustomerResponse: Customer details

    Raises:
        HTTPException 404: If customer not found
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Retrieving customer: {customer_id}")
        customer = service.get_customer(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving customer: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error retrieving customer: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@customer_router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing customer.

    Only updates fields provided in the request body.

    Args:
        customer_id: UUID of the customer to update
        payload: Customer update data
        db: Database session

    Returns:
        CustomerResponse: Updated customer

    Raises:
        HTTPException 404: If customer not found
        HTTPException 400: If validation fails
        HTTPException 500: If database operation fails
    """
    try:
        logger.info(f"Updating customer: {customer_id}")

        # Fetch customer
        customer = service.get_customer(db, customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        return service.update_customer(db, customer, payload)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating customer: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error updating customer: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error updating customer: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")