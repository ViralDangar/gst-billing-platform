import uuid
from sqlalchemy import Column, String, DATE, NUMERIC, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Ledger(Base):
    __tablename__ = "ledger"
    __table_args__ = {"schema": "accounting"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    ledger_type = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.now())


class Voucher(Base):
    __tablename__ = "voucher"
    __table_args__ = {"schema": "accounting"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_invoice_id = Column(UUID(as_uuid=True), ForeignKey("billing.invoice.id"))
    voucher_type = Column(String(20))
    voucher_date = Column(DATE, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class VoucherEntry(Base):
    __tablename__ = "voucher_entry"
    __table_args__ = {"schema": "accounting"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    voucher_id = Column(UUID(as_uuid=True), ForeignKey("accounting.voucher.id", ondelete="CASCADE"))
    ledger_id = Column(UUID(as_uuid=True), ForeignKey("accounting.ledger.id"))
    debit_amount = Column(NUMERIC(14, 2), default=0)
    credit_amount = Column(NUMERIC(14, 2), default=0)
