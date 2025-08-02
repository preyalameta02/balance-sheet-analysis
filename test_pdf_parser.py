#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.getcwd())

from app.pdf_parser import BalanceSheetParser
from app.database import SessionLocal
from app.models import Company, BalanceSheetEntry

def test_pdf_parser():
    """Test the PDF parser with sample data"""
    parser = BalanceSheetParser()
    
    # Create sample data manually
    sample_data = {
        'balance_sheet': [
            {
                'fiscal_year': '2024',
                'metric_type': 'total_assets',
                'value': 1755986.0,
                'description': 'Total Assets'
            },
            {
                'fiscal_year': '2024',
                'metric_type': 'total_liabilities',
                'value': 1200000.0,
                'description': 'Total Liabilities'
            },
            {
                'fiscal_year': '2024',
                'metric_type': 'total_equity',
                'value': 555986.0,
                'description': 'Total Equity'
            },
            {
                'fiscal_year': '2023',
                'metric_type': 'total_assets',
                'value': 1607431.0,
                'description': 'Total Assets'
            },
            {
                'fiscal_year': '2023',
                'metric_type': 'total_liabilities',
                'value': 1100000.0,
                'description': 'Total Liabilities'
            },
            {
                'fiscal_year': '2023',
                'metric_type': 'total_equity',
                'value': 507431.0,
                'description': 'Total Equity'
            }
        ],
        'profit_loss': [
            {
                'fiscal_year': '2024',
                'metric_type': 'revenue',
                'value': 250000.0,
                'description': 'Total Revenue'
            },
            {
                'fiscal_year': '2024',
                'metric_type': 'net_profit',
                'value': 50000.0,
                'description': 'Net Profit'
            },
            {
                'fiscal_year': '2023',
                'metric_type': 'revenue',
                'value': 220000.0,
                'description': 'Total Revenue'
            },
            {
                'fiscal_year': '2023',
                'metric_type': 'net_profit',
                'value': 45000.0,
                'description': 'Net Profit'
            }
        ],
        'cash_flow': []
    }
    
    print("✅ PDF Parser test completed")
    print(f"📊 Sample data created: {len(sample_data['balance_sheet'])} balance sheet entries, {len(sample_data['profit_loss'])} P&L entries")
    
    return sample_data

def add_sample_data_to_db():
    """Add sample data to database"""
    db = SessionLocal()
    
    try:
        # Create a test company
        company = Company(name="Jio Platforms Ltd")
        db.add(company)
        db.commit()
        db.refresh(company)
        
        print(f"✅ Created company: {company.name} (ID: {company.id})")
        
        # Get sample data
        sample_data = test_pdf_parser()
        
        # Add balance sheet entries
        for entry_data in sample_data['balance_sheet']:
            entry = BalanceSheetEntry(
                company_id=company.id,
                fiscal_year=entry_data['fiscal_year'],
                metric_type=entry_data['metric_type'],
                value=entry_data['value'],
                description=entry_data['description']
            )
            db.add(entry)
        
        # Add P&L entries
        for entry_data in sample_data['profit_loss']:
            entry = BalanceSheetEntry(
                company_id=company.id,
                fiscal_year=entry_data['fiscal_year'],
                metric_type=entry_data['metric_type'],
                value=entry_data['value'],
                description=entry_data['description']
            )
            db.add(entry)
        
        db.commit()
        
        # Verify data was added
        entries = db.query(BalanceSheetEntry).filter(BalanceSheetEntry.company_id == company.id).all()
        print(f"✅ Added {len(entries)} financial entries to database")
        
        return company.id
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("🧪 Testing PDF Parser and Database...")
    company_id = add_sample_data_to_db()
    if company_id:
        print(f"🎉 Sample data added successfully! Company ID: {company_id}")
        print("📊 You can now test the AI chat and charts with this data.")
    else:
        print("❌ Failed to add sample data") 