#!/usr/bin/env python3
"""
Sample data seeding script for Balance Sheet Analyst
This script creates sample companies and financial data for testing
"""

import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, User, Company, BalanceSheetEntry
from app.auth import get_password_hash

def seed_data():
    """Seed the database with sample data"""
    db = SessionLocal()
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        print("🌱 Seeding sample data...")
        
        # Create sample companies
        companies = [
            {"name": "Jio Platforms"},
            {"name": "Reliance Industries"},
            {"name": "Reliance Retail"},
            {"name": "Reliance Jio Infocomm"}
        ]
        
        created_companies = []
        for company_data in companies:
            company = Company(name=company_data["name"])
            db.add(company)
            db.flush()  # Get the ID
            created_companies.append(company)
            print(f"✅ Created company: {company.name}")
        
        # Create sample users
        users = [
            {
                "email": "analyst@example.com",
                "password": "password123",
                "role": "analyst",
                "assigned_companies": [created_companies[0].id, created_companies[1].id]
            },
            {
                "email": "ceo@example.com", 
                "password": "password123",
                "role": "ceo",
                "assigned_companies": [created_companies[0].id]
            },
            {
                "email": "ambani@example.com",
                "password": "password123", 
                "role": "ambani_family",
                "assigned_companies": [c.id for c in created_companies]
            }
        ]
        
        for user_data in users:
            user = User(
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                role=user_data["role"],
                assigned_companies=user_data["assigned_companies"]
            )
            db.add(user)
            print(f"✅ Created user: {user.email} ({user.role})")
        
        # Create sample financial data for Jio Platforms
        jio_company = created_companies[0]
        
        # Sample data for different metrics
        sample_data = [
            # Revenue data
            {"fiscal_year": "2022-23", "metric_type": "revenue", "value": 125000, "description": "Total Revenue"},
            {"fiscal_year": "2023-24", "metric_type": "revenue", "value": 145000, "description": "Total Revenue"},
            
            # Net Profit data
            {"fiscal_year": "2022-23", "metric_type": "net_profit", "value": 18500, "description": "Net Profit After Tax"},
            {"fiscal_year": "2023-24", "metric_type": "net_profit", "value": 22500, "description": "Net Profit After Tax"},
            
            # Total Assets data
            {"fiscal_year": "2022-23", "metric_type": "total_assets", "value": 450000, "description": "Total Assets"},
            {"fiscal_year": "2023-24", "metric_type": "total_assets", "value": 520000, "description": "Total Assets"},
            
            # Total Liabilities data
            {"fiscal_year": "2022-23", "metric_type": "total_liabilities", "value": 280000, "description": "Total Liabilities"},
            {"fiscal_year": "2023-24", "metric_type": "total_liabilities", "value": 320000, "description": "Total Liabilities"},
            
            # Total Equity data
            {"fiscal_year": "2022-23", "metric_type": "total_equity", "value": 170000, "description": "Shareholders Equity"},
            {"fiscal_year": "2023-24", "metric_type": "total_equity", "value": 200000, "description": "Shareholders Equity"},
            
            # Cash Flow data
            {"fiscal_year": "2022-23", "metric_type": "cash_flow", "value": 25000, "description": "Net Cash Flow"},
            {"fiscal_year": "2023-24", "metric_type": "cash_flow", "value": 32000, "description": "Net Cash Flow"},
        ]
        
        for data in sample_data:
            entry = BalanceSheetEntry(
                company_id=jio_company.id,
                fiscal_year=data["fiscal_year"],
                metric_type=data["metric_type"],
                value=data["value"],
                description=data["description"]
            )
            db.add(entry)
        
        # Add some data for Reliance Industries
        ril_company = created_companies[1]
        ril_data = [
            {"fiscal_year": "2022-23", "metric_type": "revenue", "value": 850000, "description": "Total Revenue"},
            {"fiscal_year": "2023-24", "metric_type": "revenue", "value": 920000, "description": "Total Revenue"},
            {"fiscal_year": "2022-23", "metric_type": "net_profit", "value": 75000, "description": "Net Profit After Tax"},
            {"fiscal_year": "2023-24", "metric_type": "net_profit", "value": 82000, "description": "Net Profit After Tax"},
        ]
        
        for data in ril_data:
            entry = BalanceSheetEntry(
                company_id=ril_company.id,
                fiscal_year=data["fiscal_year"],
                metric_type=data["metric_type"],
                value=data["value"],
                description=data["description"]
            )
            db.add(entry)
        
        db.commit()
        print("✅ Sample data seeded successfully!")
        print("")
        print("📋 Sample Users:")
        print("   Analyst: analyst@example.com / password123")
        print("   CEO: ceo@example.com / password123") 
        print("   Ambani Family: ambani@example.com / password123")
        print("")
        print("🏢 Sample Companies:")
        for company in created_companies:
            print(f"   - {company.name}")
        print("")
        print("📊 Sample Financial Data:")
        print("   - Jio Platforms: Revenue, Profit, Assets, Liabilities, Equity, Cash Flow")
        print("   - Reliance Industries: Revenue, Profit")
        print("")
        print("🚀 You can now start the application and test with this data!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data() 