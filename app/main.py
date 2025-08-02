from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import timedelta
import uuid

from app.database import get_db, engine
from app.models import Base, User, Company, BalanceSheetEntry, RawDocument
from app.schemas import (
    UserCreate, User as UserSchema, Token, ChatRequest, ChatResponse,
    DataQuery, ChartDataRequest, BalanceSheetEntry as BalanceSheetEntrySchema,
    LoginRequest
)
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user, get_current_user
)
from app.pdf_parser import BalanceSheetParser
from app.ai_chat import BalanceSheetChat
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Balance Sheet Analyst API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_parser = BalanceSheetParser()
chat_service = BalanceSheetChat()

# Create upload directory
os.makedirs(settings.upload_dir, exist_ok=True)

@app.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        assigned_companies=user.assigned_companies
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.get("/users/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and process PDF balance sheet"""
    
    # Check file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Check file size
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large"
        )
    
    # Save file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{file_id}.pdf")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get or create company
    company = db.query(Company).filter(Company.name == company_name).first()
    if not company:
        company = Company(name=company_name)
        db.add(company)
        db.commit()
        db.refresh(company)
    
    # Create document record
    document = RawDocument(
        company_id=company.id,
        file_url=file_path,
        file_name=file.filename,
        processed="pending"
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    try:
        # Parse PDF
        extracted_data = pdf_parser.extract_table_data(file_path)
        
        # Save extracted data to database
        for section, entries in extracted_data.items():
            for entry_data in entries:
                entry = BalanceSheetEntry(
                    company_id=company.id,
                    fiscal_year=entry_data['fiscal_year'],
                    metric_type=entry_data['metric_type'],
                    value=entry_data['value'],
                    description=entry_data['description']
                )
                db.add(entry)
        
        # Update document status
        document.processed = "processed"
        db.commit()
        
        return {
            "message": "PDF processed successfully",
            "document_id": document.id,
            "company_id": company.id,
            "extracted_entries": len([entry for entries in extracted_data.values() for entry in entries])
        }
        
    except Exception as e:
        document.processed = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )

@app.get("/data")
def get_data(
    company: str,
    metric: Optional[str] = None,
    fiscal_year: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get balance sheet data with filters"""
    
    # Check user permissions
    company_obj = db.query(Company).filter(Company.name == company).first()
    if not company_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Role-based access control
    if current_user.role == "analyst":
        if company_obj.id not in current_user.assigned_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this company"
            )
    elif current_user.role == "ceo":
        # CEO can only access their company (assuming assigned_companies contains their company)
        if company_obj.id not in current_user.assigned_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this company"
            )
    # ambani_family role can access all companies
    
    # Build query
    query = db.query(BalanceSheetEntry).filter(
        BalanceSheetEntry.company_id == company_obj.id
    )
    
    if metric:
        query = query.filter(BalanceSheetEntry.metric_type == metric)
    
    if fiscal_year:
        query = query.filter(BalanceSheetEntry.fiscal_year == fiscal_year)
    
    entries = query.all()
    
    return [BalanceSheetEntrySchema.from_orm(entry) for entry in entries]

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Chat with AI about balance sheet data"""
    
    # Check permissions if company_id is specified
    if request.company_id:
        company = db.query(Company).filter(Company.id == request.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Role-based access control
        if current_user.role == "analyst":
            if company.id not in current_user.assigned_companies:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this company"
                )
        elif current_user.role == "ceo":
            if company.id not in current_user.assigned_companies:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this company"
                )
    
    # Process chat request
    response = await chat_service.chat(db, request.question, request.company_id)
    
    return ChatResponse(
        answer=response['answer'],
        data=response['data'],
        chart_data=response['chart_data']
    )

@app.get("/chart-data")
def get_chart_data(
    company_id: int,
    metric_type: str,
    start_year: Optional[str] = None,
    end_year: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chart data for visualization"""
    
    # Check permissions
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Role-based access control
    if current_user.role == "analyst":
        if company.id not in current_user.assigned_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this company"
            )
    elif current_user.role == "ceo":
        if company.id not in current_user.assigned_companies:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this company"
            )
    
    # Build query
    query = db.query(BalanceSheetEntry).filter(
        BalanceSheetEntry.company_id == company_id,
        BalanceSheetEntry.metric_type == metric_type
    )
    
    if start_year:
        query = query.filter(BalanceSheetEntry.fiscal_year >= start_year)
    
    if end_year:
        query = query.filter(BalanceSheetEntry.fiscal_year <= end_year)
    
    entries = query.order_by(BalanceSheetEntry.fiscal_year).all()
    
    # Prepare chart data
    chart_data = {
        'labels': [entry.fiscal_year for entry in entries],
        'datasets': [{
            'label': metric_type.replace('_', ' ').title(),
            'data': [entry.value for entry in entries],
            'borderColor': '#36A2EB',
            'backgroundColor': '#36A2EB',
            'fill': False
        }]
    }
    
    return chart_data

@app.get("/companies")
def get_companies(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of companies based on user role"""
    
    if current_user.role == "ambani_family":
        # Can see all companies
        companies = db.query(Company).all()
    else:
        # Can only see assigned companies
        companies = db.query(Company).filter(
            Company.id.in_(current_user.assigned_companies)
        ).all()
    
    return companies

@app.get("/metrics")
def get_metrics():
    """Get available metric types"""
    return [
        "total_assets",
        "total_liabilities", 
        "total_equity",
        "revenue",
        "net_profit",
        "cash_flow",
        "current_assets",
        "non_current_assets",
        "current_liabilities",
        "non_current_liabilities"
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 