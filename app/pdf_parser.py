import fitz  # PyMuPDF
import pdfplumber
import re
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import logging
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
        """Extract balance sheet data from PDF using memory-efficient approach"""
        extracted_data = {
            'balance_sheet': [],
            'profit_loss': [],
            'cash_flow': []
        }
        
        try:
            # Use memory-efficient approach: process page by page
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Processing PDF with {total_pages} pages")
                
                # Process pages in chunks to avoid memory issues
                chunk_size = 10
                for start_page in range(0, total_pages, chunk_size):
                    end_page = min(start_page + chunk_size, total_pages)
                    
                    for page_num in range(start_page, end_page):
                        try:
                            page = pdf.pages[page_num]
                            text = page.extract_text()
                            
                            if not text:
                                continue
                            
                            # Skip auditor reports
                            if any(word in text.lower() for word in ['auditor', 'audit', 'opinion', 'report', 'independent']):
                                continue
                            
                            # Look for financial statement headers
                            if any(keyword in text.lower() for keyword in ['balance sheet', 'profit and loss', 'cash flow', 'consolidated']):
                                # Extract tables from this page
                                tables = page.extract_tables()
                                for table in tables:
                                    if table and len(table) > 1:
                                        table_data = self.process_table(table)
                                        for entry in table_data:
                                            if entry.get('metric_type'):
                                                if 'asset' in entry['metric_type'] or 'liability' in entry['metric_type'] or 'equity' in entry['metric_type']:
                                                    extracted_data['balance_sheet'].append(entry)
                                                elif 'revenue' in entry['metric_type'] or 'profit' in entry['metric_type'] or 'income' in entry['metric_type']:
                                                    extracted_data['profit_loss'].append(entry)
                                                elif 'cash' in entry['metric_type'] or 'flow' in entry['metric_type']:
                                                    extracted_data['cash_flow'].append(entry)
                        
                        except Exception as e:
                            logger.warning(f"Error processing page {page_num}: {e}")
                            continue
                    
                    # Clear memory after each chunk
                    if start_page % (chunk_size * 2) == 0:
                        import gc
                        gc.collect()
            
            logger.info(f"Extracted {sum(len(entries) for entries in extracted_data.values())} financial entries")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise
    
    def process_table(self, table: List[List]) -> List[Dict]:
        """Process a single table with memory-efficient approach"""
        data = []
        
        if not table or len(table) < 2:
            return data
        
        try:
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
                
                # Look for metric name in first column or second column
                metric_name = None
                if row[0] and row[0].strip():
                    metric_name = row[0].strip()
                elif len(row) > 1 and row[1] and row[1].strip():
                    metric_name = row[1].strip()
                
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
            
            # If no data found with normal processing, try alternative approach
            if not data:
                data = self._process_table_alternative(table)
        
        except Exception as e:
            logger.warning(f"Error processing table: {e}")
        
        return data
    
    def _process_table_alternative(self, table: List[List]) -> List[Dict]:
        """Alternative table processing for complex table structures"""
        data = []
        
        try:
            # Look for rows with numeric values
            for row in table:
                if not row or len(row) < 2:
                    continue
                
                # Find the first non-empty cell that might be a metric name
                metric_name = None
                for cell in row:
                    if cell and cell.strip() and not self._is_numeric(cell):
                        metric_name = cell.strip()
                        break
                
                if not metric_name:
                    continue
                
                # Find matching metric type
                metric_type = self._find_metric_type(metric_name)
                if not metric_type:
                    continue
                
                # Look for numeric values in the row
                for cell in row:
                    if cell and self._is_numeric(cell):
                        value = self.clean_value(cell)
                        if value is not None:
                            data.append({
                                'metric_type': metric_type,
                                'description': metric_name,
                                'value': value,
                                'fiscal_year': "2024"  # Default year
                            })
                            break  # Use first numeric value found
        
        except Exception as e:
            logger.warning(f"Error in alternative table processing: {e}")
        
        return data
    
    def _is_numeric(self, text: str) -> bool:
        """Check if text contains numeric values"""
        if not text:
            return False
        
        # Remove common formatting
        text = text.strip().replace(',', '').replace('₹', '').replace('$', '')
        
        # Check if it's a number
        try:
            float(text)
            return True
        except ValueError:
            return False
    
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