"""
Profitability Ratios Analysis Module

This module calculates profitability ratios using simplified data structures.

Ratios calculated:
1. Net Profit Margin (%)
2. Operating Profit Margin (%)
3. Return on Equity (ROE) (%)
4. Return on Assets (ROA) (%)
5. Return on Capital Employed (ROCE) (%)
6. Earnings Per Share (EPS)
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set plotting style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def calculate_profitability_ratios(data):
    """
    Calculate profitability ratios from financial data.
    
    Args:
        data (dict): Dictionary containing financial data
        
    Returns:
        dict: Dictionary with dates as keys and calculated ratios as values
    """
    logger.info("Calculating profitability ratios")
    
    # Extract data
    income_stmt = data['income_stmt']
    balance_sheet = data['balance_sheet']
    info = data['info']
    
    # Initialize results dictionary
    results = {}
    
    # Process each financial period
    for date_str, income_data in income_stmt.items():
        # Skip if we don't have matching balance sheet data
        if date_str not in balance_sheet:
            continue
        
        balance_data = balance_sheet[date_str]
        
        # Initialize ratios dictionary for this period
        ratios = {}
        
        # Net Profit Margin (%) = (Net Income / Total Revenue) * 100
        if 'Net Income' in income_data and 'Total Revenue' in income_data:
            net_income = income_data['Net Income']
            total_revenue = income_data['Total Revenue']
            
            if net_income is not None and total_revenue is not None and total_revenue != 0:
                ratios['Net Profit Margin (%)'] = (net_income / total_revenue) * 100
            else:
                ratios['Net Profit Margin (%)'] = None
        
        # Operating Profit Margin (%) = (Operating Income / Total Revenue) * 100
        if 'Operating Income' in income_data and 'Total Revenue' in income_data:
            operating_income = income_data['Operating Income']
            total_revenue = income_data['Total Revenue']
            
            if operating_income is not None and total_revenue is not None and total_revenue != 0:
                ratios['Operating Profit Margin (%)'] = (operating_income / total_revenue) * 100
            else:
                ratios['Operating Profit Margin (%)'] = None
        
        # Return on Equity (ROE) (%) = (Net Income / Total Stockholder Equity) * 100
        if 'Net Income' in income_data and 'Total Stockholder Equity' in balance_data:
            net_income = income_data['Net Income']
            total_equity = balance_data['Total Stockholder Equity']
            
            if net_income is not None and total_equity is not None and total_equity != 0:
                ratios['Return on Equity (%)'] = (net_income / total_equity) * 100
            else:
                ratios['Return on Equity (%)'] = None
        
        # Return on Assets (ROA) (%) = (Net Income / Total Assets) * 100
        if 'Net Income' in income_data and 'Total Assets' in balance_data:
            net_income = income_data['Net Income']
            total_assets = balance_data['Total Assets']
            
            if net_income is not None and total_assets is not None and total_assets != 0:
                ratios['Return on Assets (%)'] = (net_income / total_assets) * 100
            else:
                ratios['Return on Assets (%)'] = None
        
        # Return on Capital Employed (ROCE) (%)
        # ROCE = EBIT / Capital Employed
        # Capital Employed = Total Assets - Current Liabilities
        if ('Operating Income' in income_data and 
            'Total Assets' in balance_data and 
            'Total Current Liabilities' in balance_data):
            
            ebit = income_data['Operating Income']  # EBIT is often reported as Operating Income
            total_assets = balance_data['Total Assets']
            current_liabilities = balance_data['Total Current Liabilities']
            
            capital_employed = total_assets - current_liabilities
            
            if (ebit is not None and capital_employed is not None and 
                capital_employed != 0 and capital_employed > 0):
                ratios['Return on Capital Employed (%)'] = (ebit / capital_employed) * 100
            else:
                ratios['Return on Capital Employed (%)'] = None
        
        # Earnings Per Share (EPS)
        if 'Net Income' in income_data:
            net_income = income_data['Net Income']
            shares_outstanding = info.get('sharesOutstanding', None)
            
            if net_income is not None and shares_outstanding is not None and shares_outstanding > 0:
                ratios['EPS (₹ per share)'] = net_income / shares_outstanding
            else:
                ratios['EPS (₹ per share)'] = None
        
        # Add ratios for this period to results
        results[date_str] = ratios
    
    logger.info("Successfully calculated profitability ratios")
    return results

def convert_ratios_to_dataframe(ratios_dict):
    """
    Convert ratios dictionary to a pandas DataFrame.
    
    Args:
        ratios_dict (dict): Dictionary with dates as keys and calculated ratios as values
        
    Returns:
        pd.DataFrame: DataFrame with dates as index and ratios as columns
    """
    # Create list of dictionaries
    data = []
    for date_str, ratios in ratios_dict.items():
        row = {'Date': date_str, **ratios}
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Convert Date column to datetime and set as index
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        df = df.set_index('Date')
    
    return df

def plot_trend_graph(ratio_df, ratio_name, company_name, benchmark_dfs=None, output_dir=None):
    """
    Plot trend graph for a specific ratio.
    
    Args:
        ratio_df (pd.DataFrame): DataFrame with ratios for the main company
        ratio_name (str): Name of ratio to plot
        company_name (str): Name of the main company
        benchmark_dfs (dict, optional): Dictionary with company names as keys and DataFrames as values
        output_dir (str, optional): Directory to save the plot
    """
    if ratio_name not in ratio_df.columns:
        logger.warning(f"Ratio '{ratio_name}' not found in DataFrame")
        return
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot main company data
    ratio_df[ratio_name].plot(ax=ax, marker='o', linewidth=2, label=company_name)
    
    # Plot benchmark data if available
    if benchmark_dfs:
        for name, df in benchmark_dfs.items():
            if ratio_name in df.columns:
                df[ratio_name].plot(ax=ax, linestyle='--', marker='x', label=name)
    
    plt.title(f"{ratio_name} - {company_name} vs Benchmarks")
    plt.ylabel(ratio_name)
    plt.xlabel("Year")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save plot if output directory is provided
    if output_dir:
        filename = f"{ratio_name.replace(' ', '_').replace('(', '').replace(')', '').replace('%', 'Pct')}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath)
        logger.info(f"Plot saved to {filepath}")
    
    plt.close()

def display_latest_values(ratio_df, ratio_name, company_name, benchmark_dfs=None):
    """
    Display latest values for a specific ratio across companies.
    
    Args:
        ratio_df (pd.DataFrame): DataFrame with ratios for the main company
        ratio_name (str): Name of ratio to display
        company_name (str): Name of the main company
        benchmark_dfs (dict, optional): Dictionary with company names as keys and DataFrames as values
        
    Returns:
        pd.DataFrame: DataFrame with latest values
    """
    if ratio_name not in ratio_df.columns:
        logger.warning(f"Ratio '{ratio_name}' not found in DataFrame")
        return None
    
    # Get latest value for main company
    latest_value = ratio_df[ratio_name].iloc[-1] if not ratio_df.empty else None
    
    # Create dictionary of latest values
    latest_values = {company_name: latest_value}
    
    # Add benchmark values if available
    if benchmark_dfs:
        for name, df in benchmark_dfs.items():
            if ratio_name in df.columns and not df.empty:
                latest_values[name] = df[ratio_name].iloc[-1]
            else:
                latest_values[name] = None
    
    # Create DataFrame
    latest_df = pd.DataFrame({ratio_name: latest_values}).T
    
    return latest_df