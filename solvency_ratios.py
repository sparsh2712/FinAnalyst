"""
Solvency Ratios Analysis Script

This script calculates and visualizes solvency ratios for a given company
and benchmarks against industry averages.

Ratios calculated:
1. Debt-to-Equity (D/E) Ratio (Trend Graph)
2. Interest Coverage Ratio (Trend Graph)
3. Debt-to-Asset Ratio (Single Number)

Usage:
    python solvency_ratios.py --ticker AAPL --period 5y --benchmark MSFT GOOGL
    
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
    parser = argparse.ArgumentParser(description="Calculate solvency ratios")
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

def calculate_solvency_ratios(data):
    """Calculate solvency ratios from financial data."""
    income_stmt = data['income_stmt']
    balance_sheet = data['balance_sheet']
    
    # Calculate ratios
    results = pd.DataFrame(index=balance_sheet.index)
    
    # Debt-to-Equity (D/E) Ratio = Total Debt / Shareholders' Equity
    # Note: Total Debt often includes both short-term and long-term debt
    if ('Long Term Debt' in balance_sheet.columns and 
        'Total Stockholder Equity' in balance_sheet.columns):
        # Use Long Term Debt if available
        results['Debt-to-Equity Ratio'] = balance_sheet['Long Term Debt'] / balance_sheet['Total Stockholder Equity']
    elif ('Total Debt' in balance_sheet.columns and 
          'Total Stockholder Equity' in balance_sheet.columns):
        # Use Total Debt if available
        results['Debt-to-Equity Ratio'] = balance_sheet['Total Debt'] / balance_sheet['Total Stockholder Equity']
    
    # Interest Coverage Ratio = EBIT / Interest Expense
    if ('Operating Income' in income_stmt.columns and 
        'Interest Expense' in income_stmt.columns):
        # EBIT is often reported as Operating Income
        results['Interest Coverage Ratio'] = income_stmt['Operating Income'] / abs(income_stmt['Interest Expense'])
    
    # Debt-to-Asset Ratio = Total Debt / Total Assets
    if ('Long Term Debt' in balance_sheet.columns and 
        'Total Assets' in balance_sheet.columns):
        # Use Long Term Debt if available
        results['Debt-to-Asset Ratio'] = balance_sheet['Long Term Debt'] / balance_sheet['Total Assets']
    elif ('Total Debt' in balance_sheet.columns and 
          'Total Assets' in balance_sheet.columns):
        # Use Total Debt if available
        results['Debt-to-Asset Ratio'] = balance_sheet['Total Debt'] / balance_sheet['Total Assets']
    
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
    trend_ratios = ['Debt-to-Equity Ratio', 'Interest Coverage Ratio']
    
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
            plt.savefig(os.path.join(output_dir, f"{ratio.replace(' ', '_').replace('-', '_')}.png"))
            plt.close()

def display_single_numbers(company_ratios, benchmark_ratios=None):
    """
    Display single number ratios with benchmarking.
    
    Args:
        company_ratios: DataFrame with company ratios
        benchmark_ratios: Dictionary of DataFrames with benchmark companies' ratios
    """
    # List of ratios to display as single numbers
    single_ratios = ['Debt-to-Asset Ratio']
    
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
    """Main function to run the solvency ratio analysis."""
    args = parse_arguments()
    
    print(f"\nAnalyzing solvency ratios for {args.ticker}...")
    
    # Fetch data for the main company
    company_data = fetch_financial_data(args.ticker, args.period)
    company_ratios = calculate_solvency_ratios(company_data)
    
    # Fetch data for benchmark companies
    benchmark_ratios = {}
    for benchmark in args.benchmark:
        print(f"Fetching data for benchmark company: {benchmark}")
        benchmark_data = fetch_financial_data(benchmark, args.period)
        benchmark_ratios[benchmark] = calculate_solvency_ratios(benchmark_data)
    
    # Plot trend graphs
    print("Generating trend graphs...")
    plot_trend_graphs(company_ratios, benchmark_ratios, args.output)
    
    # Display single number ratios
    print("Calculating single number ratios...")
    display_single_numbers(company_ratios, benchmark_ratios)
    
    print(f"\nAnalysis complete. Visualizations saved to {args.output} directory.")

if __name__ == "__main__":
    main()