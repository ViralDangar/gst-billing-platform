from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.master_data_service import service
from app.master_data_service.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)

from app.master_data_service.schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)


product_router = APIRouter(prefix="/masters/products", tags=["Product Master"])
customer_router = APIRouter(prefix="/masters/customer", tags=["Customer Master"])



@product_router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return service.create_product(db, payload)

@product_router.get("/health")
def masters_health():
    return {"service": "master-data", "status": "ok"}

@product_router.get("", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return service.list_products(db)

@product_router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    product = service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@product_router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return service.update_product(db, product, payload)

@customer_router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    return service.create_customer(db, payload)


@customer_router.get("", response_model=List[CustomerResponse])
def list_customers(db: Session = Depends(get_db)):
    return service.list_customers(db)


@customer_router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    customer = service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@customer_router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    customer = service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return service.update_customer(db, customer, payload)