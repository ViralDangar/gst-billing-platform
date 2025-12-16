import uuid
from sqlalchemy import Column, String, Text, Boolean, NUMERIC, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customer"
    __table_args__ = {"schema": "master_data"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    gstin = Column(String(15))
    state = Column(String(50), nullable=False)
    address = Column(Text, nullable=False)
    is_b2b = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Product(Base):
    __tablename__ = "product"
    __table_args__ = {"schema": "master_data"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    hsn_sac = Column(String(10))
    gst_rate = Column(NUMERIC(5, 2), nullable=False)
    unit = Column(String(20))
    base_price = Column(NUMERIC(12, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
