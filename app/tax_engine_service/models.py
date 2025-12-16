import uuid
from sqlalchemy import Column, String, NUMERIC, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class InvoiceTax(Base):
    __tablename__ = "invoice_tax"
    __table_args__ = {"schema": "tax"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("billing.invoice.id", ondelete="CASCADE"))
    tax_type = Column(String(10))
    tax_rate = Column(NUMERIC(5, 2))
    tax_amount = Column(NUMERIC(14, 2))
