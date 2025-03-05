"""
Efficiency Ratios Analysis Script

This script calculates and visualizes efficiency ratios for a given company
and benchmarks against industry averages.

Ratios calculated:
1. Asset Turnover Ratio (Trend Graph)
2. Inventory Turnover Ratio (Trend Graph)
3. Receivables Turnover Ratio (Trend Graph)
4. Days Sales Outstanding (DSO) (Single Number)

Usage:
    python efficiency_ratios.py --ticker AAPL --period 5y --benchmark MSFT GOOGL
    
    Required arguments:
        --ticker: Company ticker symbol
        --period: Analysis period (e.g., 5y for 5 years)
    
    Optional arguments:
        --benchmark: List of peer companies for benchmarking
        --output: Output directory for saving visualizations (default: ./output)
"""

import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from datetime import datetime, timedelta

# Set plotting style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Calculate efficiency ratios")
    parser.add_argument("--ticker", required=True, help="Company ticker symbol")
    parser.add_argument("--period", default="5y", help="Analysis period (e.g., 5y for 5 years)")
    parser.add_argument("--benchmark", nargs="+", default=[], help="List of peer companies for benchmarking")
    parser.add_argument("--output", default="./output", help="Output directory for saving visualizations")
    return parser.parse_args()

def fetch_financial_data(ticker, period="5y"):
    """Fetch financial data for a given ticker."""
    # Get the ticker object
    tick = yf.Ticker(ticker)
    
    # Fetch financial statements
    income_stmt = tick.financials
    balance_sheet = tick.balance_sheet
    
    # Transpose to have dates as index
    income_stmt = income_stmt.T
    balance_sheet = balance_sheet.T
    
    # Get stock price data for the period
    end_date = datetime.now()
    if period.endswith('y'):
        years = int(period[:-1])
        start_date = end_date - timedelta(days=365 * years)
    else:
        # Default to 5 years
        start_date = end_date - timedelta(days=365 * 5)
    
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    
    return {
        'income_stmt': income_stmt,
        'balance_sheet': balance_sheet,
        'stock_data': stock_data,
        'info': tick.info
    }

def calculate_efficiency_ratios(data):
    """Calculate efficiency ratios from financial data."""
    print("calculating efficiency ratio")
    income_stmt = data['income_stmt']
    balance_sheet = data['balance_sheet']
    
    # Calculate ratios
    results = pd.DataFrame(index=income_stmt.index)
    
    # Asset Turnover Ratio = Revenue / Average Total Assets
    if 'Total Revenue' in income_stmt.columns and 'Total Assets' in balance_sheet.columns:
        # Calculate average total assets for each year
        avg_assets = balance_sheet['Total Assets'].rolling(window=2).mean()
        # For the first year, just use the available value
        avg_assets.iloc[0] = balance_sheet['Total Assets'].iloc[0]
        
        # Match income statement dates with balance sheet dates and calculate ratio
        common_dates = income_stmt.index.intersection(avg_assets.index)
        if not common_dates.empty:
            results.loc[common_dates, 'Asset Turnover Ratio'] = (
                income_stmt.loc[common_dates, 'Total Revenue'] / 
                avg_assets.loc[common_dates]
            )
    
    # Inventory Turnover Ratio = Cost of Goods Sold / Average Inventory
    if 'Cost Of Revenue' in income_stmt.columns and 'Inventory' in balance_sheet.columns:
        # Calculate average inventory for each year
        avg_inventory = balance_sheet['Inventory'].rolling(window=2).mean()
        # For the first year, just use the available value
        avg_inventory.iloc[0] = balance_sheet['Inventory'].iloc[0]
        
        # Match income statement dates with balance sheet dates and calculate ratio
        common_dates = income_stmt.index.intersection(avg_inventory.index)
        if not common_dates.empty:
            results.loc[common_dates, 'Inventory Turnover Ratio'] = (
                income_stmt.loc[common_dates, 'Cost Of Revenue'] / 
                avg_inventory.loc[common_dates]
            )
    
    # Receivables Turnover Ratio = Revenue / Average Accounts Receivable
    if 'Total Revenue' in income_stmt.columns and 'Net Receivables' in balance_sheet.columns:
        # Calculate average accounts receivable for each year
        avg_receivables = balance_sheet['Net Receivables'].rolling(window=2).mean()
        # For the first year, just use the available value
        avg_receivables.iloc[0] = balance_sheet['Net Receivables'].iloc[0]
        
        # Match income statement dates with balance sheet dates and calculate ratio
        common_dates = income_stmt.index.intersection(avg_receivables.index)
        if not common_dates.empty:
            results.loc[common_dates, 'Receivables Turnover Ratio'] = (
                income_stmt.loc[common_dates, 'Total Revenue'] / 
                avg_receivables.loc[common_dates]
            )
    
    # Days Sales Outstanding (DSO) = (Accounts Receivable / Revenue) * 365
    if 'Total Revenue' in income_stmt.columns and 'Net Receivables' in balance_sheet.columns:
        common_dates = income_stmt.index.intersection(balance_sheet.index)
        if not common_dates.empty:
            results.loc[common_dates, 'Days Sales Outstanding'] = (
                balance_sheet.loc[common_dates, 'Net Receivables'] / 
                income_stmt.loc[common_dates, 'Total Revenue']
            ) * 365
    
    print("succesfully calculated efficiency ratio")
    return results

def plot_trend_graphs(company_ratios, benchmark_ratios=None, output_dir="./output"):
    """
    Plot trend graphs for specified ratios.
    
    Args:
        company_ratios: DataFrame with company ratios
        benchmark_ratios: Dictionary of DataFrames with benchmark companies' ratios
        output_dir: Directory to save the plots
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # List of ratios to plot as trend graphs
    trend_ratios = [
        'Asset Turnover Ratio', 
        'Inventory Turnover Ratio', 
        'Receivables Turnover Ratio'
    ]
    
    for ratio in trend_ratios:
        if ratio in company_ratios.columns:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Plot company data
            company_ratios[ratio].plot(ax=ax, marker='o', label=f"Company")
            
            # Plot benchmark companies data
            if benchmark_ratios:
                for company, ratios in benchmark_ratios.items():
                    if ratio in ratios.columns:
                        ratios[ratio].plot(ax=ax, linestyle='--', marker='x', label=f"{company}")
            
            plt.title(f"{ratio} Trend (Past 5 Years)")
            plt.ylabel(ratio)
            plt.xlabel("Year")
            plt.legend()
            plt.tight_layout()
            
            # Save the plot
            plt.savefig(os.path.join(output_dir, f"{ratio.replace(' ', '_')}.png"))
            plt.close()

def display_single_numbers(company_ratios, benchmark_ratios=None):
    """
    Display single number ratios with benchmarking.
    
    Args:
        company_ratios: DataFrame with company ratios
        benchmark_ratios: Dictionary of DataFrames with benchmark companies' ratios
    """
    # List of ratios to display as single numbers
    single_ratios = ['Days Sales Outstanding']
    
    # Create a table for the latest values
    latest_values = {}
    
    # Get the latest value for the company
    for ratio in single_ratios:
        if ratio in company_ratios.columns:
            latest_values['Company'] = company_ratios[ratio].iloc[-1]
    
    # Get the latest values for benchmark companies
    if benchmark_ratios:
        for company, ratios in benchmark_ratios.items():
            for ratio in single_ratios:
                if ratio in ratios.columns:
                    latest_values[company] = ratios[ratio].iloc[-1]
    
    # Display as a DataFrame
    latest_df = pd.DataFrame(latest_values, index=single_ratios)
    print("\nSingle Number Ratios (Latest Values):")
    print(latest_df)
    
    return latest_df

def main():
    """Main function to run the efficiency ratio analysis."""
    args = parse_arguments()
    
    print(f"\nAnalyzing efficiency ratios for {args.ticker}...")
    
    # Fetch data for the main company
    company_data = fetch_financial_data(args.ticker, args.period)
    company_ratios = calculate_efficiency_ratios(company_data)
    
    # Fetch data for benchmark companies
    benchmark_ratios = {}
    for benchmark in args.benchmark:
        print(f"Fetching data for benchmark company: {benchmark}")
        benchmark_data = fetch_financial_data(benchmark, args.period)
        benchmark_ratios[benchmark] = calculate_efficiency_ratios(benchmark_data)
    
    # Plot trend graphs
    print("Generating trend graphs...")
    plot_trend_graphs(company_ratios, benchmark_ratios, args.output)
    
    # Display single number ratios
    print("Calculating single number ratios...")
    display_single_numbers(company_ratios, benchmark_ratios)
    
    print(f"\nAnalysis complete. Visualizations saved to {args.output} directory.")

if __name__ == "__main__":
    main()