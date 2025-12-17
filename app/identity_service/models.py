import uuid
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID , JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class Company(Base):
    __tablename__ = "company"
    __table_args__ = {"schema": "identity"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    logo_url = Column(Text)
    default_bank_details = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())


class GSTIN(Base):
    __tablename__ = "gstin"
    __table_args__ = {"schema": "identity"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("identity.company.id"))
    gst_number = Column(String(15), unique=True, nullable=False)
    state_code = Column(String(2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
