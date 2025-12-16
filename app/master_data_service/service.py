import uuid
from sqlalchemy.orm import Session
from app.master_data_service.models import Product
from app.master_data_service.schemas import ProductCreate, ProductUpdate
from app.master_data_service.models import Customer
from app.master_data_service.schemas import CustomerCreate, CustomerUpdate


def create_product(db: Session, payload: ProductCreate) -> Product:
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
    return product


def list_products(db: Session):
    return db.query(Product).filter(Product.is_active == True).all()


def get_product(db: Session, product_id):
    return db.query(Product).filter(Product.id == product_id).first()


def update_product(db: Session, product, payload: ProductUpdate):
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
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
    return customer


def list_customers(db: Session):
    return db.query(Customer).filter(Customer.is_active == True).all()


def get_customer(db: Session, customer_id):
    return db.query(Customer).filter(Customer.id == customer_id).first()


def update_customer(db: Session, customer, payload: CustomerUpdate):
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer