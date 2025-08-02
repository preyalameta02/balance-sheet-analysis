#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.getcwd())

from app.pdf_parser import BalanceSheetParser
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pdf_parser():
    """Test PDF parser with a simple mock"""
    parser = BalanceSheetParser()
    
    # Test the parser methods
    print("🧪 Testing PDF Parser...")
    
    # Test balance sheet page detection
    test_text = "Consolidated Balance Sheet as at 31st March, 2024"
    is_bs = parser._is_balance_sheet_page(test_text)
    print(f"✅ Balance sheet detection: {is_bs}")
    
    # Test profit & loss page detection
    test_text_pnl = "Consolidated Statement of Profit and Loss"
    is_pnl = parser._is_profit_loss_page(test_text_pnl)
    print(f"✅ P&L detection: {is_pnl}")
    
    # Test cash flow page detection
    test_text_cf = "Consolidated Statement of Cash Flow"
    is_cf = parser._is_cash_flow_page(test_text_cf)
    print(f"✅ Cash flow detection: {is_cf}")
    
    # Test value cleaning
    test_values = ["₹1,755,986", "1,755,986", "1755986", "₹1,755,986 Cr", "(1,755,986)"]
    for val in test_values:
        cleaned = parser.clean_value(val)
        print(f"✅ Cleaned '{val}' -> {cleaned}")
    
    # Test metric type finding
    test_metrics = ["Total Assets", "Total Liabilities", "Revenue", "Net Profit"]
    for metric in test_metrics:
        metric_type = parser._find_metric_type(metric)
        print(f"✅ Metric '{metric}' -> {metric_type}")
    
    print("🎉 PDF Parser test completed!")

def create_sample_pdf_data():
    """Create sample data that would be extracted from a PDF"""
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
            }
        ],
        'cash_flow': []
    }
    
    print("📊 Sample PDF data created:")
    print(f"   - Balance Sheet entries: {len(sample_data['balance_sheet'])}")
    print(f"   - P&L entries: {len(sample_data['profit_loss'])}")
    print(f"   - Cash Flow entries: {len(sample_data['cash_flow'])}")
    
    return sample_data

if __name__ == "__main__":
    print("🔧 Testing PDF Upload Functionality...")
    test_pdf_parser()
    create_sample_pdf_data()
    print("\n💡 If PDF upload is not working, it might be because:")
    print("   1. PDF format doesn't match expected structure")
    print("   2. Tables are not being detected properly")
    print("   3. Text extraction is failing")
    print("   4. File permissions or path issues")
    print("\n🔧 To fix this, try:")
    print("   1. Upload a simple, well-formatted PDF")
    print("   2. Check the upload logs for errors")
    print("   3. Use the test data endpoint for now") 