"""
Financial Data Utilities Module

This module contains utilities for fetching, transforming, and storing financial data
in a consistent and debug-friendly format.
"""

import os
import json
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_financial_data(ticker, period="5y"):
    """
    Fetch financial data for a given ticker and convert to simple, flat data structures.
    
    Args:
        ticker (str): Stock ticker symbol
        period (str): Analysis period (e.g., "5y" for 5 years)
        
    Returns:
        dict: Dictionary containing financial data with standardized, flat structures
    """
    logger.info(f"Fetching financial data for {ticker} over {period} period")
    
    try:
        # Get the ticker object
        tick = yf.Ticker(ticker)
        
        # Fetch financial statements
        income_stmt = tick.financials
        balance_sheet = tick.balance_sheet
        cash_flow = tick.cashflow
        
        # Get stock price data for the period
        end_date = datetime.now()
        if period.endswith('y'):
            years = int(period[:-1])
            start_date = end_date - timedelta(days=365 * years)
        else:
            # Default to 5 years
            start_date = end_date - timedelta(days=365 * 5)
        
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        
        # Process financial statements to make them flat and JSON-compatible
        # Transpose to have dates as index
        income_stmt_processed = process_financial_statement(income_stmt, "income_statement")
        balance_sheet_processed = process_financial_statement(balance_sheet, "balance_sheet")
        cash_flow_processed = process_financial_statement(cash_flow, "cash_flow")
        
        # Process stock data
        stock_data_processed = process_stock_data(stock_data)
        
        # Get info
        info = tick.info
        
        return {
            'income_stmt': income_stmt_processed,
            'balance_sheet': balance_sheet_processed,
            'cash_flow': cash_flow_processed,
            'stock_data': stock_data_processed,
            'info': info
        }
    
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        raise

def process_financial_statement(statement, statement_type):
    """
    Process financial statement dataframe to make it flat and JSON-compatible.
    
    Args:
        statement (pd.DataFrame): Financial statement dataframe
        statement_type (str): Type of financial statement for logging
        
    Returns:
        dict: Dictionary with years as keys and financial data as values
    """
    if statement is None or statement.empty:
        logger.warning(f"No {statement_type} data available")
        return {}
    
    # Transpose for better readability (dates as index)
    statement = statement.T
    
    # Convert to dictionary where each year is a key
    result = {}
    for date, row in statement.iterrows():
        # Convert date to string format
        date_str = date.strftime("%Y-%m-%d")
        
        # Convert row to dictionary, replacing NaN with None
        row_dict = row.where(pd.notna(row), None).to_dict()
        
        result[date_str] = row_dict
    
    return result

def process_stock_data(stock_data):
    """
    Process stock price data to make it flat and JSON-compatible.
    
    Args:
        stock_data (pd.DataFrame): Stock price dataframe
        
    Returns:
        dict: Dictionary with dates as keys and stock price data as values
    """
    if stock_data is None or stock_data.empty:
        logger.warning("No stock price data available")
        return {}
    
    # Reset index to make date a column
    stock_data = stock_data.reset_index()
    
    # Convert to dictionary where each date is a key
    result = {}
    for _, row in stock_data.iterrows():
        date_str = row['Date'].strftime("%Y-%m-%d")
        
        # Create a dictionary for this row, excluding the Date column
        row_dict = {
            'Open': row['Open'],
            'High': row['High'],
            'Low': row['Low'],
            'Close': row['Close'],
            'Adj Close': row['Adj Close'] if 'Adj Close' in row else row['Close'],
            'Volume': row['Volume']
        }
        
        # Replace NaN with None
        row_dict = {k: None if pd.isna(v) else v for k, v in row_dict.items()}
        
        result[date_str] = row_dict
    
    return result

def save_to_json(data, filename):
    """
    Save financial data to a JSON file.
    
    Args:
        data (dict): Financial data dictionary
        filename (str): Output filename
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Data successfully saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {str(e)}")
        raise

def load_from_json(filename):
    """
    Load financial data from a JSON file.
    
    Args:
        filename (str): Input filename
        
    Returns:
        dict: Financial data dictionary
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Data successfully loaded from {filename}")
        return data
    except Exception as e:
        logger.error(f"Error loading data from {filename}: {str(e)}")
        raise

def get_annual_stock_prices(stock_data, financial_dates):
    """
    Get annual stock prices matching financial statement dates.
    
    Args:
        stock_data (dict): Stock price data dictionary
        financial_dates (list): List of financial statement dates as strings
        
    Returns:
        dict: Dictionary with financial dates as keys and closest stock prices as values
    """
    result = {}
    
    for fin_date_str in financial_dates:
        fin_date = datetime.strptime(fin_date_str, "%Y-%m-%d")
        
        # Convert stock data dates to datetime objects for comparison
        stock_dates = [datetime.strptime(d, "%Y-%m-%d") for d in stock_data.keys()]
        
        # Find the closest date
        closest_date = min(stock_dates, key=lambda d: abs(d - fin_date))
        closest_date_str = closest_date.strftime("%Y-%m-%d")
        
        result[fin_date_str] = stock_data[closest_date_str]['Close']
    
    return result

def create_output_directories(base_dir="./output"):
    """
    Create output directories for storing analysis results.
    
    Args:
        base_dir (str): Base output directory
        
    Returns:
        dict: Dictionary with paths to different output directories
    """
    directories = {
        'base': base_dir,
        'profitability': os.path.join(base_dir, 'profitability'),
        'liquidity': os.path.join(base_dir, 'liquidity'),
        'solvency': os.path.join(base_dir, 'solvency'),
        'efficiency': os.path.join(base_dir, 'efficiency'),
        'valuation': os.path.join(base_dir, 'valuation'),
        'market': os.path.join(base_dir, 'market'),
        'json': os.path.join(base_dir, 'json')
    }
    
    for directory in directories.values():
        os.makedirs(directory, exist_ok=True)
    
    return directories