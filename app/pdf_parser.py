import fitz  # PyMuPDF
import pdfplumber
import re
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import logging
from decimal import Decimal
import os

logger = logging.getLogger(__name__)

class BalanceSheetParser:
    def __init__(self):
        self.metric_mappings = {
            'total_assets': ['total assets', 'total asset', 'assets'],
            'total_liabilities': ['total liabilities', 'total liability', 'liabilities'],
            'total_equity': ['total equity', 'shareholders equity', 'shareholder equity', 'equity'],
            'revenue': ['revenue', 'total revenue', 'sales', 'income'],
            'net_profit': ['net profit', 'net income', 'profit after tax', 'profit for the year'],
            'cash_flow': ['cash flow', 'net cash flow', 'cash and cash equivalents'],
            'current_assets': ['current assets'],
            'non_current_assets': ['non-current assets', 'non current assets'],
            'current_liabilities': ['current liabilities'],
            'non_current_liabilities': ['non-current liabilities', 'non current liabilities'],
            'inventory': ['inventory', 'inventories', 'stock'],
            'accounts_receivable': ['trade receivables', 'accounts receivable', 'receivables'],
            'accounts_payable': ['trade payables', 'accounts payable', 'payables'],
            'short_term_debt': ['short term borrowings', 'short-term borrowings', 'short term debt'],
            'long_term_debt': ['long term borrowings', 'long-term borrowings', 'long term debt']
        }
        
        # Financial patterns for extraction
        self.financial_patterns = {
            'total_assets': r'Total Assets.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'total_liabilities': r'Total Liabilities.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'total_equity': r'Total Equity.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'revenue': r'Revenue.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'net_profit': r'Net Profit.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'cash_equivalents': r'Cash and Cash Equivalents.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'inventory': r'Inventories.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'accounts_receivable': r'Trade Receivables.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'accounts_payable': r'Trade Payables.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'short_term_debt': r'Short-term Borrowings.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'long_term_debt': r'Long-term Borrowings.*?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
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
        """Extract balance sheet data from PDF using multiple methods"""
        extracted_data = {
            'balance_sheet': [],
            'profit_loss': [],
            'cash_flow': []
        }
        
        try:
            # Method 1: Extract text and use regex patterns
            full_text = self.extract_full_text(pdf_path)
            pattern_data = self.extract_from_patterns(full_text)
            
            # Method 2: Extract from tables
            table_data = self.extract_from_tables(pdf_path)
            
            # Method 3: Parse balance sheet sections
            section_data = self.extract_from_sections(pdf_path)
            
            # Combine all extracted data
            all_data = pattern_data + table_data + section_data
            
            # Organize by type
            for entry in all_data:
                if entry.get('metric_type'):
                    if 'asset' in entry['metric_type'] or 'liability' in entry['metric_type'] or 'equity' in entry['metric_type']:
                        extracted_data['balance_sheet'].append(entry)
                    elif 'revenue' in entry['metric_type'] or 'profit' in entry['metric_type'] or 'income' in entry['metric_type']:
                        extracted_data['profit_loss'].append(entry)
                    elif 'cash' in entry['metric_type'] or 'flow' in entry['metric_type']:
                        extracted_data['cash_flow'].append(entry)
            
            logger.info(f"Extracted {len(all_data)} financial entries")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
    
    def extract_full_text(self, pdf_path: str) -> str:
        """Extract all text from PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def extract_from_patterns(self, text: str) -> List[Dict]:
        """Extract financial data using regex patterns"""
        data = []
        text_lower = text.lower()
        
        # Look for year patterns
        year_pattern = r'\b(20\d{2})\b'
        years = re.findall(year_pattern, text)
        years = list(set(years))  # Remove duplicates
        years.sort(reverse=True)  # Most recent first
        
        if not years:
            years = ["2024", "2023"]  # Default years
        
        # Extract data using patterns
        for metric_type, pattern in self.financial_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                value_str = match.group(1)
                value = self.clean_value(value_str)
                if value is not None:
                    # Find the metric name from mappings
                    metric_name = None
                    for key, keywords in self.metric_mappings.items():
                        if key == metric_type:
                            metric_name = keywords[0].title()
                            break
                    
                    if metric_name:
                        data.append({
                            'metric_type': metric_type,
                            'description': metric_name,
                            'value': value,
                            'fiscal_year': years[0] if years else "2024"
                        })
        
        return data
    
    def extract_from_tables(self, pdf_path: str) -> List[Dict]:
        """Extract data from PDF tables"""
        data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # Skip auditor reports
                    if any(word in text.lower() for word in ['auditor', 'audit', 'opinion', 'report']):
                        continue
                    
                    # Look for financial statement headers
                    if any(keyword in text.lower() for keyword in ['balance sheet', 'profit and loss', 'cash flow']):
                        tables = page.extract_tables()
                        for table in tables:
                            table_data = self.process_table(table)
                            data.extend(table_data)
        
        except Exception as e:
            logger.error(f"Error extracting from tables: {e}")
        
        return data
    
    def extract_from_sections(self, pdf_path: str) -> List[Dict]:
        """Extract data from specific balance sheet sections"""
        data = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Look for balance sheet sections
                if "Consolidated Balance Sheet" in text or "Balance Sheet as at" in text:
                    # Extract the next few pages for complete data
                    section_text = text
                    for next_page in range(page_num + 1, min(page_num + 5, len(doc))):
                        section_text += "\n" + doc[next_page].get_text()
                    
                    # Parse the section
                    section_data = self.parse_balance_sheet_section(section_text)
                    data.extend(section_data)
                    break  # Found balance sheet, stop searching
            
            doc.close()
        
        except Exception as e:
            logger.error(f"Error extracting from sections: {e}")
        
        return data
    
    def parse_balance_sheet_section(self, text: str) -> List[Dict]:
        """Parse balance sheet section text"""
        data = []
        lines = text.split('\n')
        
        # Look for year headers
        years = []
        year_pattern = r'\b(20\d{2})\b'
        for line in lines:
            years.extend(re.findall(year_pattern, line))
        years = list(set(years))
        years.sort(reverse=True)
        
        if not years:
            years = ["2024", "2023"]
        
        # Parse lines with financial data
        for line in lines:
            # Look for pattern: Label Value1 Value2
            match = re.match(r'^(.*?)\s+([\d,]+)\s+([\d,]+)$', line.strip())
            if match:
                label = match.group(1).strip()
                value_2024 = self.clean_value(match.group(2))
                value_2023 = self.clean_value(match.group(3))
                
                # Find metric type
                metric_type = self._find_metric_type(label)
                if metric_type and value_2024 is not None:
                    data.append({
                        'metric_type': metric_type,
                        'description': label,
                        'value': value_2024,
                        'fiscal_year': years[0] if years else "2024"
                    })
                
                if metric_type and value_2023 is not None:
                    data.append({
                        'metric_type': metric_type,
                        'description': label,
                        'value': value_2023,
                        'fiscal_year': years[1] if len(years) > 1 else "2023"
                    })
        
        return data
    
    def process_table(self, table: List[List]) -> List[Dict]:
        """Process a single table"""
        data = []
        
        if not table or len(table) < 2:
            return data
        
        # Find header row with years
        header_row = None
        year_columns = {}
        
        for row_idx, row in enumerate(table):
            if len(row) < 2:
                continue
            
            # Look for year headers
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
    
    def _find_metric_type(self, metric_name: str) -> Optional[str]:
        """Find metric type from metric name"""
        metric_lower = metric_name.lower()
        
        for metric_type, keywords in self.metric_mappings.items():
            if any(keyword in metric_lower for keyword in keywords):
                return metric_type
        
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
        
        for pattern in year_patterns:
            if re.search(pattern, text_clean):
                return True
        
        return False
    
    def _extract_year_from_header(self, text: str) -> str:
        """Extract year from header text"""
        if not text:
            return "2024"
        
        # Look for 4-digit year
        year_match = re.search(r'\b(20\d{2})\b', text)
        if year_match:
            return year_match.group(1)
        
        # Default to 2024 if no year found
        return "2024" 
        return "2024" 