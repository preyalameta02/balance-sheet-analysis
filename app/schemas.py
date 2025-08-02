from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: str
    role: str
    assigned_companies: List[int] = []

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Login schemas
class LoginRequest(BaseModel):
    email: str
    password: str

# Company schemas
class CompanyBase(BaseModel):
    name: str

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Balance Sheet Entry schemas
class BalanceSheetEntryBase(BaseModel):
    company_id: int
    fiscal_year: str
    metric_type: str
    value: float
    description: Optional[str] = None

class BalanceSheetEntryCreate(BalanceSheetEntryBase):
    pass

class BalanceSheetEntry(BalanceSheetEntryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Raw Document schemas
class RawDocumentBase(BaseModel):
    company_id: int
    file_url: str
    file_name: str
    processed: str = "pending"

class RawDocumentCreate(RawDocumentBase):
    pass

class RawDocument(RawDocumentBase):
    id: int
    upload_time: datetime
    
    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[User] = None

class TokenData(BaseModel):
    email: Optional[str] = None

# Chat schemas
class ChatRequest(BaseModel):
    question: str
    company_id: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    data: Optional[dict] = None
    chart_data: Optional[dict] = None

# Data query schemas
class DataQuery(BaseModel):
    company: str
    metric: Optional[str] = None
    fiscal_year: Optional[str] = None

# Chart data schemas
class ChartDataRequest(BaseModel):
    company_id: int
    metric_type: str
    start_year: Optional[str] = None
    end_year: Optional[str] = None 