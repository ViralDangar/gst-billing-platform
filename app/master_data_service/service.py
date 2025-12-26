"""
Master Data Service Module

This module handles all business logic for master data entities including
products and customers. It provides CRUD operations with proper error handling.
"""

import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.master_data_service.models import Product, Customer
from app.master_data_service.schemas import (
    ProductCreate,
    ProductUpdate,
    CustomerCreate,
    CustomerUpdate
)

# Configure logging
logger = logging.getLogger(__name__)


def create_product(db: Session, payload: ProductCreate) -> Product:
    """
    Create a new product in the system.

    Args:
        db: Database session
        payload: Product creation data

    Returns:
        Product: Newly created product object

    Raises:
        ValueError: If validation fails
        SQLAlchemyError: If database operation fails
    """
    try:
        logger.info(f"Creating product: {payload.name}")

        product = Product(
            id=uuid.uuid4(),
            name=payload.name,
            hsn_sac=payload.hsn_sac,
            gst_rate=payload.gst_rate,
            unit=payload.unit,
            base_price=payload.base_price,
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        logger.info(f"Product created successfully: {product.id}")
        return product

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating product: {str(e)}")
        raise ValueError("Product with similar details already exists")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating product: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating product: {str(e)}")
        raise


def list_products(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of active products with pagination.

    Args:
        db: Database session
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return

    Returns:
        list: List of active Product objects

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        products = (
            db.query(Product)
            .filter(Product.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.info(f"Retrieved {len(products)} products (skip={skip}, limit={limit})")
        return products

    except SQLAlchemyError as e:
        logger.error(f"Database error listing products: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing products: {str(e)}")
        raise


def get_product(db: Session, product_id):
    """
    Retrieve a single product by ID.

    Args:
        db: Database session
        product_id: UUID of the product

    Returns:
        Product or None: Product object if found, None otherwise

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            logger.info(f"Product retrieved: {product_id}")
        else:
            logger.warning(f"Product not found: {product_id}")
        return product

    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving product: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving product: {str(e)}")
        raise


def update_product(db: Session, product, payload: ProductUpdate):
    """
    Update an existing product.

    Only updates fields that are provided in the payload.

    Args:
        db: Database session
        product: Product object to update
        payload: Product update data

    Returns:
        Product: Updated product object

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        logger.info(f"Updating product: {product.id}")

        # Update only provided fields
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)

        logger.info(f"Product updated successfully: {product.id}")
        return product

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating product: {str(e)}")
        raise ValueError("Update failed due to constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating product: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating product: {str(e)}")
        raise


def count_products(db: Session) -> int:
    """
    Get total count of active products.

    Args:
        db: Database session

    Returns:
        int: Total number of active products

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        total = db.query(Product).filter(Product.is_active == True).count()
        logger.info(f"Total active products count: {total}")
        return total

    except SQLAlchemyError as e:
        logger.error(f"Database error counting products: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error counting products: {str(e)}")
        raise


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
    """
    Create a new customer in the system.

    Args:
        db: Database session
        payload: Customer creation data

    Returns:
        Customer: Newly created customer object

    Raises:
        ValueError: If validation fails
        SQLAlchemyError: If database operation fails
    """
    try:
        logger.info(f"Creating customer: {payload.name}")

        customer = Customer(
            id=uuid.uuid4(),
            name=payload.name,
            gstin=payload.gstin,
            state=payload.state,
            address=payload.address,
            is_b2b=payload.is_b2b,
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        logger.info(f"Customer created successfully: {customer.id}")
        return customer

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating customer: {str(e)}")
        raise ValueError("Customer with similar GSTIN already exists")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating customer: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating customer: {str(e)}")
        raise


def list_customers(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of active customers with pagination.

    Args:
        db: Database session
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return

    Returns:
        list: List of active Customer objects

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        customers = (
            db.query(Customer)
            .filter(Customer.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
        logger.info(f"Retrieved {len(customers)} customers (skip={skip}, limit={limit})")
        return customers

    except SQLAlchemyError as e:
        logger.error(f"Database error listing customers: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing customers: {str(e)}")
        raise


def get_customer(db: Session, customer_id):
    """
    Retrieve a single customer by ID.

    Args:
        db: Database session
        customer_id: UUID of the customer

    Returns:
        Customer or None: Customer object if found, None otherwise

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            logger.info(f"Customer retrieved: {customer_id}")
        else:
            logger.warning(f"Customer not found: {customer_id}")
        return customer

    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving customer: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving customer: {str(e)}")
        raise


def update_customer(db: Session, customer, payload: CustomerUpdate):
    """
    Update an existing customer.

    Only updates fields that are provided in the payload.

    Args:
        db: Database session
        customer: Customer object to update
        payload: Customer update data

    Returns:
        Customer: Updated customer object

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        logger.info(f"Updating customer: {customer.id}")

        # Update only provided fields
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(customer, field, value)

        db.commit()
        db.refresh(customer)

        logger.info(f"Customer updated successfully: {customer.id}")
        return customer

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating customer: {str(e)}")
        raise ValueError("Update failed due to constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating customer: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating customer: {str(e)}")
        raise


def count_customers(db: Session) -> int:
    """
    Get total count of active customers.

    Args:
        db: Database session

    Returns:
        int: Total number of active customers

    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        total = db.query(Customer).filter(Customer.is_active == True).count()
        logger.info(f"Total active customers count: {total}")
        return total

    except SQLAlchemyError as e:
        logger.error(f"Database error counting customers: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error counting customers: {str(e)}")
        raise