import openai
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, List, Optional
import json
import logging
from app.config import settings
from app.models import BalanceSheetEntry, Company

logger = logging.getLogger(__name__)

class BalanceSheetChat:
    def __init__(self):
        # Only initialize OpenAI if API key is available
        self.llm = None
        self.openai_available = False
        
        if settings.openai_api_key and settings.openai_api_key.strip():
            try:
                openai.api_key = settings.openai_api_key
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.1,
                    openai_api_key=settings.openai_api_key,
                    max_retries=2,  # Add retry limit
                    request_timeout=30  # Add timeout
                )
                self.openai_available = True
                logger.info("OpenAI initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
                self.openai_available = False
        else:
            logger.info("OpenAI API key not provided, using fallback responses only")
        
        self.system_prompt = """You are a financial analyst assistant specializing in balance sheet analysis. 
        You help users understand financial data by providing clear, accurate explanations and insights.
        
        When analyzing data:
        1. Always provide context and explain what the numbers mean
        2. Calculate year-over-year changes when relevant
        3. Highlight trends and patterns
        4. Use proper financial terminology
        5. If asked for visualizations, suggest appropriate chart types
        6. Always mention the currency (₹ Crore) when discussing values
        
        Available metrics include:
        - total_assets: Total assets of the company
        - total_liabilities: Total liabilities
        - total_equity: Shareholders' equity
        - revenue: Total revenue/sales
        - net_profit: Net profit after tax
        - cash_flow: Net cash flow
        - current_assets: Current assets
        - non_current_assets: Non-current assets
        - current_liabilities: Current liabilities
        - non_current_liabilities: Non-current liabilities
        """
    
    def generate_fallback_response(self, data: Dict, question: str) -> str:
        """Generate a fallback response when OpenAI is unavailable"""
        question_lower = question.lower()
        
        # Simple keyword-based responses
        if any(word in question_lower for word in ['profit', 'income', 'earnings']):
            if 'net_profit' in data:
                years = list(data['net_profit'].keys())
                if len(years) >= 2:
                    latest = data['net_profit'][years[0]]['value']
                    previous = data['net_profit'][years[1]]['value']
                    change = ((latest - previous) / previous * 100) if previous != 0 else 0
                    return f"Based on the data, the net profit was ₹{latest:,.0f} Cr in {years[0]} and ₹{previous:,.0f} Cr in {years[1]}. This represents a {change:+.1f}% change year-over-year."
        
        if any(word in question_lower for word in ['revenue', 'sales']):
            if 'revenue' in data:
                years = list(data['revenue'].keys())
                if len(years) >= 2:
                    latest = data['revenue'][years[0]]['value']
                    previous = data['revenue'][years[1]]['value']
                    change = ((latest - previous) / previous * 100) if previous != 0 else 0
                    return f"The revenue was ₹{latest:,.0f} Cr in {years[0]} and ₹{previous:,.0f} Cr in {years[1]}. This shows a {change:+.1f}% change year-over-year."
        
        if any(word in question_lower for word in ['assets']):
            if 'total_assets' in data:
                years = list(data['total_assets'].keys())
                if len(years) >= 2:
                    latest = data['total_assets'][years[0]]['value']
                    previous = data['total_assets'][years[1]]['value']
                    change = ((latest - previous) / previous * 100) if previous != 0 else 0
                    return f"Total assets were ₹{latest:,.0f} Cr in {years[0]} and ₹{previous:,.0f} Cr in {years[1]}. This represents a {change:+.1f}% change."
        
        if any(word in question_lower for word in ['liabilities', 'debt']):
            if 'total_liabilities' in data:
                years = list(data['total_liabilities'].keys())
                if len(years) >= 2:
                    latest = data['total_liabilities'][years[0]]['value']
                    previous = data['total_liabilities'][years[1]]['value']
                    change = ((latest - previous) / previous * 100) if previous != 0 else 0
                    return f"Total liabilities were ₹{latest:,.0f} Cr in {years[0]} and ₹{previous:,.0f} Cr in {years[1]}. This shows a {change:+.1f}% change."
        
        if any(word in question_lower for word in ['equity', 'shareholder']):
            if 'total_equity' in data:
                years = list(data['total_equity'].keys())
                if len(years) >= 2:
                    latest = data['total_equity'][years[0]]['value']
                    previous = data['total_equity'][years[1]]['value']
                    change = ((latest - previous) / previous * 100) if previous != 0 else 0
                    return f"Total equity was ₹{latest:,.0f} Cr in {years[0]} and ₹{previous:,.0f} Cr in {years[1]}. This represents a {change:+.1f}% change."
        
        if any(word in question_lower for word in ['cash', 'flow']):
            if 'cash_flow' in data:
                years = list(data['cash_flow'].keys())
                if len(years) >= 2:
                    latest = data['cash_flow'][years[0]]['value']
                    previous = data['cash_flow'][years[1]]['value']
                    change = ((latest - previous) / previous * 100) if previous != 0 else 0
                    return f"Cash flow was ₹{latest:,.0f} Cr in {years[0]} and ₹{previous:,.0f} Cr in {years[1]}. This shows a {change:+.1f}% change."
        
        # Generic response
        metrics = list(data.keys())
        if metrics:
            return f"I found data for the following metrics: {', '.join(metrics)}. The data shows financial information across multiple years. You can view the detailed numbers in the data table below."
        
        return "I couldn't find specific financial data for your question. Please try asking about revenue, profit, assets, or liabilities."
    
    def get_relevant_data(self, db: Session, question: str, company_id: Optional[int] = None) -> Dict:
        """Extract relevant financial data based on the question"""
        # Simple keyword-based data extraction
        question_lower = question.lower()
        
        # Determine which metrics to fetch
        metrics_to_fetch = []
        if any(word in question_lower for word in ['profit', 'income', 'earnings']):
            metrics_to_fetch.append('net_profit')
        if any(word in question_lower for word in ['revenue', 'sales', 'income']):
            metrics_to_fetch.append('revenue')
        if any(word in question_lower for word in ['assets', 'asset']):
            metrics_to_fetch.append('total_assets')
        if any(word in question_lower for word in ['liabilities', 'liability', 'debt']):
            metrics_to_fetch.append('total_liabilities')
        if any(word in question_lower for word in ['equity', 'shareholder']):
            metrics_to_fetch.append('total_equity')
        if any(word in question_lower for word in ['cash', 'flow']):
            metrics_to_fetch.append('cash_flow')
        
        # If no specific metrics mentioned, fetch all
        if not metrics_to_fetch:
            metrics_to_fetch = ['total_assets', 'total_liabilities', 'total_equity', 'revenue', 'net_profit']
        
        # Build query
        query = db.query(BalanceSheetEntry).filter(
            BalanceSheetEntry.metric_type.in_(metrics_to_fetch)
        )
        
        if company_id:
            query = query.filter(BalanceSheetEntry.company_id == company_id)
        
        # Get data for last 3 years
        entries = query.order_by(BalanceSheetEntry.fiscal_year.desc()).limit(15).all()
        
        # Organize data by metric and year
        data = {}
        for entry in entries:
            if entry.metric_type not in data:
                data[entry.metric_type] = {}
            data[entry.metric_type][entry.fiscal_year] = {
                'value': entry.value,
                'description': entry.description
            }
        
        return data
    
    def generate_chart_data(self, data: Dict, question: str) -> Optional[Dict]:
        """Generate chart data based on the question and available data"""
        question_lower = question.lower()
        
        # Determine chart type based on question
        if any(word in question_lower for word in ['trend', 'over time', 'growth', 'change']):
            chart_type = 'line'
        elif any(word in question_lower for word in ['compare', 'vs', 'versus']):
            chart_type = 'bar'
        else:
            chart_type = 'line'  # Default to line chart
        
        # Prepare chart data
        chart_data = {
            'type': chart_type,
            'labels': [],
            'datasets': []
        }
        
        # Get all years
        all_years = set()
        for metric_data in data.values():
            all_years.update(metric_data.keys())
        all_years = sorted(list(all_years))
        
        chart_data['labels'] = all_years
        
        # Create datasets for each metric
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
        for i, (metric, metric_data) in enumerate(data.items()):
            values = []
            for year in all_years:
                if year in metric_data:
                    values.append(metric_data[year]['value'])
                else:
                    values.append(None)
            
            dataset = {
                'label': metric.replace('_', ' ').title(),
                'data': values,
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)],
                'fill': False
            }
            chart_data['datasets'].append(dataset)
        
        return chart_data
    
    async def chat(self, db: Session, question: str, company_id: Optional[int] = None) -> Dict:
        """Process a natural language question and return an answer with data"""
        try:
            # Get relevant data
            data = self.get_relevant_data(db, question, company_id)
            
            if not data:
                return {
                    'answer': "I couldn't find relevant financial data for your question. Please try asking about specific metrics like revenue, profit, assets, or liabilities.",
                    'data': None,
                    'chart_data': None
                }
            
            # Generate chart data
            chart_data = self.generate_chart_data(data, question)
            
            # Try to get AI response if OpenAI is available, otherwise use fallback
            if self.openai_available and self.llm:
                try:
                    # Create context for the LLM
                    context = f"""
                    Financial Data Context:
                    {json.dumps(data, indent=2)}
                    
                    User Question: {question}
                    
                    Please provide a comprehensive answer based on the financial data above. 
                    Include specific numbers, trends, and insights. If the data shows multiple years, 
                    calculate year-over-year changes where relevant.
                    """
                    
                    # Generate response using LLM
                    messages = [
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=context)
                    ]
                    
                    response = await self.llm.ainvoke(messages)
                    answer = response.content
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    if "rate limit" in error_msg or "quota" in error_msg or "429" in error_msg:
                        logger.warning("OpenAI rate limit exceeded. Using fallback response.")
                        answer = self.generate_fallback_response(data, question)
                    elif "timeout" in error_msg or "time out" in error_msg:
                        logger.warning("OpenAI request timed out. Using fallback response.")
                        answer = self.generate_fallback_response(data, question)
                    else:
                        logger.warning(f"OpenAI API failed: {e}. Using fallback response.")
                        answer = self.generate_fallback_response(data, question)
            else:
                # Use fallback response when OpenAI is not available
                answer = self.generate_fallback_response(data, question)
            
            return {
                'answer': answer,
                'data': data,
                'chart_data': chart_data
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                'answer': "I encountered an error while processing your question. Please try again or rephrase your question.",
                'data': None,
                'chart_data': None
            }
    
    def get_metric_summary(self, db: Session, company_id: int, metric_type: str) -> Dict:
        """Get summary statistics for a specific metric"""
        entries = db.query(BalanceSheetEntry).filter(
            BalanceSheetEntry.company_id == company_id,
            BalanceSheetEntry.metric_type == metric_type
        ).order_by(BalanceSheetEntry.fiscal_year.desc()).all()
        
        if not entries:
            return {}
        
        values = [entry.value for entry in entries]
        years = [entry.fiscal_year for entry in entries]
        
        return {
            'metric': metric_type,
            'years': years,
            'values': values,
            'latest_value': values[0] if values else None,
            'previous_value': values[1] if len(values) > 1 else None,
            'change_percentage': ((values[0] - values[1]) / values[1] * 100) if len(values) > 1 and values[1] != 0 else None
        } 