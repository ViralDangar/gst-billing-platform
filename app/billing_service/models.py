import uuid
from sqlalchemy import Column, String, DATE, NUMERIC, TIMESTAMP, ForeignKey,Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base

class InvoiceSequence(Base):
    __tablename__ = "invoice_sequence"
    __table_args__ = {"schema": "billing"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gstin_id = Column(UUID(as_uuid=True), nullable=False)
    financial_year = Column(String(9), nullable=False)
    last_sequence = Column(Integer, default=0)


class Invoice(Base):
    __tablename__ = "invoice"
    __table_args__ = {"schema": "billing"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(30), unique=True)
    invoice_date = Column(DATE, nullable=False)
    gstin_id = Column(UUID(as_uuid=True), ForeignKey("identity.gstin.id"))
    customer_id = Column(UUID(as_uuid=True), ForeignKey("master_data.customer.id"))
    status = Column(String(10))
    taxable_total = Column(NUMERIC(14, 2))
    tax_total = Column(NUMERIC(14, 2))
    round_off = Column(NUMERIC(6, 2))
    grand_total = Column(NUMERIC(14, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())


class InvoiceItem(Base):
    __tablename__ = "invoice_item"
    __table_args__ = {"schema": "billing"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("billing.invoice.id", ondelete="CASCADE"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("master_data.product.id"))
    quantity = Column(NUMERIC(10, 2), nullable=False)
    rate = Column(NUMERIC(12, 2), nullable=False)
    taxable_value = Column(NUMERIC(14, 2), nullable=False)
