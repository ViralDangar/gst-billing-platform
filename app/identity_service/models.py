import uuid
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Company(Base):
    __tablename__ = "company"
    __table_args__ = {"schema": "identity"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)  # State code (e.g., "27" for Maharashtra)
    pincode = Column(String(6), nullable=True)
    mobile_number = Column(String(200), nullable=True)  # Multiple numbers separated by / (phone in UI)
    email_id = Column(String(255), nullable=True)  # email in UI
    bank_name = Column(String(255), nullable=True)
    bank_branch = Column(String(255), nullable=True)
    account_holder_name = Column(String(255), nullable=True)
    account_number = Column(String(50), nullable=True)
    ifsc_code = Column(String(11), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class GSTIN(Base):
    __tablename__ = "gstin"
    __table_args__ = {"schema": "identity"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("identity.company.id"))
    gst_number = Column(String(15), unique=True, nullable=False)
    state_code = Column(String(2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
