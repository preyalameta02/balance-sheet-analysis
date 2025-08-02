import fitz  # PyMuPDF
import pdfplumber
import re
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class BalanceSheetParser:
    def __init__(self):
        self.metric_mappings = {
            'total_assets': ['total assets', 'total asset'],
            'total_liabilities': ['total liabilities', 'total liability'],
            'total_equity': ['total equity', 'shareholders equity', 'shareholder equity'],
            'revenue': ['revenue', 'total revenue', 'sales'],
            'net_profit': ['net profit', 'net income', 'profit after tax'],
            'cash_flow': ['cash flow', 'net cash flow'],
            'current_assets': ['current assets'],
            'non_current_assets': ['non-current assets', 'non current assets'],
            'current_liabilities': ['current liabilities'],
            'non_current_liabilities': ['non-current liabilities', 'non current liabilities']
        }
    
    def clean_value(self, value_str: str) -> Optional[float]:
        """Clean and convert value string to float (₹ Crore)"""
        if not value_str:
            return None
        
        # Remove common prefixes and suffixes
        value_str = value_str.strip().lower()
        value_str = re.sub(r'[₹$,\s]', '', value_str)
        value_str = re.sub(r'\(.*?\)', '', value_str)  # Remove parentheses content
        
        # Handle negative values
        is_negative = False
        if value_str.startswith('-') or value_str.endswith(')'):
            is_negative = True
            value_str = value_str.replace('-', '').replace('(', '').replace(')', '')
        
        try:
            # Convert to float
            value = float(value_str)
            if is_negative:
                value = -value
            return value
        except ValueError:
            logger.warning(f"Could not convert value: {value_str}")
            return None
    
    def extract_table_data(self, pdf_path: str) -> Dict[str, List[Dict]]:
        """Extract balance sheet data from PDF"""
        extracted_data = {
            'balance_sheet': [],
            'profit_loss': [],
            'cash_flow': []
        }
        
        try:
            # Use pdfplumber for table extraction
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    # Identify section based on headers
                    if self._is_balance_sheet_page(text):
                        tables = page.extract_tables()
                        for table in tables:
                            data = self._process_balance_sheet_table(table)
                            extracted_data['balance_sheet'].extend(data)
                    
                    elif self._is_profit_loss_page(text):
                        tables = page.extract_tables()
                        for table in tables:
                            data = self._process_profit_loss_table(table)
                            extracted_data['profit_loss'].extend(data)
                    
                    elif self._is_cash_flow_page(text):
                        tables = page.extract_tables()
                        for table in tables:
                            data = self._process_cash_flow_table(table)
                            extracted_data['cash_flow'].extend(data)
        
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
        
        return extracted_data
    
    def _is_balance_sheet_page(self, text: str) -> bool:
        """Check if page contains balance sheet data"""
        balance_sheet_keywords = [
            'consolidated balance sheet',
            'balance sheet as at',
            'assets and liabilities'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in balance_sheet_keywords)
    
    def _is_profit_loss_page(self, text: str) -> bool:
        """Check if page contains profit & loss data"""
        pnl_keywords = [
            'consolidated statement of profit and loss',
            'profit and loss',
            'income statement'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in pnl_keywords)
    
    def _is_cash_flow_page(self, text: str) -> bool:
        """Check if page contains cash flow data"""
        cash_flow_keywords = [
            'consolidated statement of cash flow',
            'cash flow statement',
            'cash flows'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in cash_flow_keywords)
    
    def _process_balance_sheet_table(self, table: List[List]) -> List[Dict]:
        """Process balance sheet table data"""
        data = []
        
        for row in table:
            if len(row) < 2:
                continue
            
            # Look for metric name in first column
            metric_name = row[0].strip() if row[0] else ""
            if not metric_name:
                continue
            
            # Find matching metric type
            metric_type = self._find_metric_type(metric_name)
            if not metric_type:
                continue
            
            # Extract values from subsequent columns
            for i in range(1, len(row)):
                value = self.clean_value(row[i])
                if value is not None:
                    data.append({
                        'metric_type': metric_type,
                        'description': metric_name,
                        'value': value,
                        'fiscal_year': f"202{4-i}" if i <= 2 else "2023-24"  # Adjust based on actual data
                    })
        
        return data
    
    def _process_profit_loss_table(self, table: List[List]) -> List[Dict]:
        """Process profit & loss table data"""
        data = []
        
        for row in table:
            if len(row) < 2:
                continue
            
            metric_name = row[0].strip() if row[0] else ""
            if not metric_name:
                continue
            
            metric_type = self._find_metric_type(metric_name)
            if not metric_type:
                continue
            
            for i in range(1, len(row)):
                value = self.clean_value(row[i])
                if value is not None:
                    data.append({
                        'metric_type': metric_type,
                        'description': metric_name,
                        'value': value,
                        'fiscal_year': f"202{4-i}" if i <= 2 else "2023-24"
                    })
        
        return data
    
    def _process_cash_flow_table(self, table: List[List]) -> List[Dict]:
        """Process cash flow table data"""
        data = []
        
        for row in table:
            if len(row) < 2:
                continue
            
            metric_name = row[0].strip() if row[0] else ""
            if not metric_name:
                continue
            
            metric_type = self._find_metric_type(metric_name)
            if not metric_type:
                continue
            
            for i in range(1, len(row)):
                value = self.clean_value(row[i])
                if value is not None:
                    data.append({
                        'metric_type': metric_type,
                        'description': metric_name,
                        'value': value,
                        'fiscal_year': f"202{4-i}" if i <= 2 else "2023-24"
                    })
        
        return data
    
    def _find_metric_type(self, metric_name: str) -> Optional[str]:
        """Find the standardized metric type for a given metric name"""
        metric_name_lower = metric_name.lower()
        
        for metric_type, keywords in self.metric_mappings.items():
            if any(keyword in metric_name_lower for keyword in keywords):
                return metric_type
        
        return None
    
    def extract_fiscal_year(self, text: str) -> Optional[str]:
        """Extract fiscal year from text"""
        # Look for patterns like "2023-24", "FY 2023-24", etc.
        patterns = [
            r'(\d{4}-\d{2})',
            r'FY\s*(\d{4}-\d{2})',
            r'(\d{4}/\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None 