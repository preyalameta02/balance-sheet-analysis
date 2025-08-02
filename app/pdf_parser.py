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
                total_pages = len(pdf.pages)
                
                # Search entire PDF for financial statements
                for page_num in range(total_pages):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if not text:
                        continue
                    
                    # Look for actual financial statement headers (not auditor reports)
                    if self._is_actual_balance_sheet_page(text):
                        tables = page.extract_tables()
                        for table in tables:
                            data = self._process_balance_sheet_table(table)
                            extracted_data['balance_sheet'].extend(data)
                    
                    elif self._is_actual_profit_loss_page(text):
                        tables = page.extract_tables()
                        for table in tables:
                            data = self._process_profit_loss_table(table)
                            extracted_data['profit_loss'].extend(data)
                    
                    elif self._is_actual_cash_flow_page(text):
                        tables = page.extract_tables()
                        for table in tables:
                            data = self._process_cash_flow_table(table)
                            extracted_data['cash_flow'].extend(data)
                    
                    # Stop if we found significant data
                    total_found = sum(len(entries) for entries in extracted_data.values())
                    if total_found > 10:  # Found enough data
                        break
        
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
        
        return extracted_data
    
    def _is_actual_balance_sheet_page(self, text: str) -> bool:
        """Check if page contains actual balance sheet data (not auditor reports)"""
        text_lower = text.lower()
        
        # Skip auditor reports and other non-financial content
        skip_keywords = [
            'auditor', 'audit', 'opinion', 'report', 'independent',
            'basis for opinion', 'key audit matter', 'material misstatement',
            'fraud or error', 'audit procedures', 'audit evidence'
        ]
        
        if any(word in text_lower for word in skip_keywords):
            return False
        
        # Look for actual balance sheet headers
        balance_sheet_keywords = [
            'consolidated balance sheet as at',
            'balance sheet as at',
            'assets and liabilities',
            'total assets',
            'total liabilities',
            'shareholders equity',
            'equity and liabilities',
            'non-current assets',
            'current assets',
            'non-current liabilities',
            'current liabilities'
        ]
        
        return any(keyword in text_lower for keyword in balance_sheet_keywords)
    
    def _is_actual_profit_loss_page(self, text: str) -> bool:
        """Check if page contains actual profit & loss data (not auditor reports)"""
        text_lower = text.lower()
        
        # Skip auditor reports and other non-financial content
        skip_keywords = [
            'auditor', 'audit', 'opinion', 'report', 'independent',
            'basis for opinion', 'key audit matter', 'material misstatement',
            'fraud or error', 'audit procedures', 'audit evidence'
        ]
        
        if any(word in text_lower for word in skip_keywords):
            return False
        
        # Look for actual P&L headers
        pnl_keywords = [
            'consolidated statement of profit and loss',
            'profit and loss statement',
            'income statement',
            'revenue',
            'net profit',
            'total income',
            'total expenses',
            'profit before tax',
            'profit after tax'
        ]
        
        return any(keyword in text_lower for keyword in pnl_keywords)
    
    def _is_actual_cash_flow_page(self, text: str) -> bool:
        """Check if page contains actual cash flow data (not auditor reports)"""
        text_lower = text.lower()
        
        # Skip auditor reports and other non-financial content
        skip_keywords = [
            'auditor', 'audit', 'opinion', 'report', 'independent',
            'basis for opinion', 'key audit matter', 'material misstatement',
            'fraud or error', 'audit procedures', 'audit evidence'
        ]
        
        if any(word in text_lower for word in skip_keywords):
            return False
        
        # Look for actual cash flow headers
        cash_flow_keywords = [
            'consolidated statement of cash flow',
            'cash flow statement',
            'cash flows',
            'operating activities',
            'investing activities',
            'financing activities',
            'net cash flow'
        ]
        
        return any(keyword in text_lower for keyword in cash_flow_keywords)
    
    def _process_balance_sheet_table(self, table: List[List]) -> List[Dict]:
        """Process balance sheet table data"""
        data = []
        
        # Find header row with years
        header_row = None
        year_columns = {}
        
        for row_idx, row in enumerate(table):
            if len(row) < 2:
                continue
            
            # Look for year headers in the row
            for col_idx, cell in enumerate(row):
                if cell and self._is_year_header(cell):
                    if header_row is None:
                        header_row = row_idx
                    year_columns[col_idx] = self._extract_year_from_header(cell)
        
        # If no year headers found, use default years
        if not year_columns:
            year_columns = {1: "2024", 2: "2023"}
        
        # Process data rows
        for row_idx, row in enumerate(table):
            if row_idx == header_row:  # Skip header row
                continue
                
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
            
            # Extract values from year columns
            for col_idx, year in year_columns.items():
                if col_idx < len(row):
                    value = self.clean_value(row[col_idx])
                    if value is not None:
                        data.append({
                            'metric_type': metric_type,
                            'description': metric_name,
                            'value': value,
                            'fiscal_year': year
                        })
        
        return data
    
    def _process_profit_loss_table(self, table: List[List]) -> List[Dict]:
        """Process profit & loss table data"""
        data = []
        
        # Find header row with years
        header_row = None
        year_columns = {}
        
        for row_idx, row in enumerate(table):
            if len(row) < 2:
                continue
            
            # Look for year headers in the row
            for col_idx, cell in enumerate(row):
                if cell and self._is_year_header(cell):
                    if header_row is None:
                        header_row = row_idx
                    year_columns[col_idx] = self._extract_year_from_header(cell)
        
        # If no year headers found, use default years
        if not year_columns:
            year_columns = {1: "2024", 2: "2023"}
        
        # Process data rows
        for row_idx, row in enumerate(table):
            if row_idx == header_row:  # Skip header row
                continue
                
            if len(row) < 2:
                continue
            
            metric_name = row[0].strip() if row[0] else ""
            if not metric_name:
                continue
            
            metric_type = self._find_metric_type(metric_name)
            if not metric_type:
                continue
            
            # Extract values from year columns
            for col_idx, year in year_columns.items():
                if col_idx < len(row):
                    value = self.clean_value(row[col_idx])
                    if value is not None:
                        data.append({
                            'metric_type': metric_type,
                            'description': metric_name,
                            'value': value,
                            'fiscal_year': year
                        })
        
        return data
    
    def _process_cash_flow_table(self, table: List[List]) -> List[Dict]:
        """Process cash flow table data"""
        data = []
        
        # Find header row with years
        header_row = None
        year_columns = {}
        
        for row_idx, row in enumerate(table):
            if len(row) < 2:
                continue
            
            # Look for year headers in the row
            for col_idx, cell in enumerate(row):
                if cell and self._is_year_header(cell):
                    if header_row is None:
                        header_row = row_idx
                    year_columns[col_idx] = self._extract_year_from_header(cell)
        
        # If no year headers found, use default years
        if not year_columns:
            year_columns = {1: "2024", 2: "2023"}
        
        # Process data rows
        for row_idx, row in enumerate(table):
            if row_idx == header_row:  # Skip header row
                continue
                
            if len(row) < 2:
                continue
            
            metric_name = row[0].strip() if row[0] else ""
            if not metric_name:
                continue
            
            metric_type = self._find_metric_type(metric_name)
            if not metric_type:
                continue
            
            # Extract values from year columns
            for col_idx, year in year_columns.items():
                if col_idx < len(row):
                    value = self.clean_value(row[col_idx])
                    if value is not None:
                        data.append({
                            'metric_type': metric_type,
                            'description': metric_name,
                            'value': value,
                            'fiscal_year': year
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
    
    def _is_year_header(self, text: str) -> bool:
        """Check if text is a year header"""
        if not text:
            return False
        
        text_clean = text.strip().lower()
        
        # Look for year patterns
        year_patterns = [
            r'\b20\d{2}\b',  # 2024, 2023, etc.
            r'\b\d{4}\b',    # Any 4-digit number
            r'year ended',
            r'as at',
            r'31st march',
            r'31 march'
        ]
        
        import re
        for pattern in year_patterns:
            if re.search(pattern, text_clean):
                return True
        
        return False
    
    def _extract_year_from_header(self, text: str) -> str:
        """Extract year from header text"""
        if not text:
            return "2024"
        
        import re
        
        # Look for 4-digit year
        year_match = re.search(r'\b(20\d{2})\b', text)
        if year_match:
            return year_match.group(1)
        
        # Default to 2024 if no year found
        return "2024" 