from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # analyst, ceo, ambani_family
    assigned_companies = Column(JSON, default=list)  # List of company IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    balance_sheet_entries = relationship("BalanceSheetEntry", back_populates="company")
    raw_documents = relationship("RawDocument", back_populates="company")

class BalanceSheetEntry(Base):
    __tablename__ = "balance_sheet_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    fiscal_year = Column(String)  # e.g., "2023-24"
    metric_type = Column(String)  # e.g., "revenue", "assets", "liabilities", "equity"
    value = Column(Float)  # Value in ₹ Crore
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="balance_sheet_entries")

class RawDocument(Base):
    __tablename__ = "raw_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    file_url = Column(String)
    file_name = Column(String)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(String, default="pending")  # pending, processed, failed
    
    # Relationships
    company = relationship("Company", back_populates="raw_documents") 