"""
Profitability Ratios Analysis Script

This script calculates and visualizes profitability ratios for a given company
and benchmarks against industry averages.

Ratios calculated:
1. Net Profit Margin (%)
2. Operating Profit Margin (%)
3. Return on Equity (ROE) (%)
4. Return on Assets (ROA) (%)
5. Return on Capital Employed (ROCE) (%)
6. Earnings Per Share (EPS)

Usage:
    python profitability_ratios.py --ticker AAPL --period 5y --benchmark MSFT GOOGL
    
    Required arguments:
        --ticker: Company ticker symbol
        --period: Analysis period (e.g., 5y for 5 years)
    
    Optional arguments:
        --benchmark: List of peer companies for benchmarking
        --market_index: Market index for comparison (default: ^GSPC for S&P 500)
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
    parser = argparse.ArgumentParser(description="Calculate profitability ratios")
    parser.add_argument("--ticker", required=True, help="Company ticker symbol")
    parser.add_argument("--period", default="5y", help="Analysis period (e.g., 5y for 5 years)")
    parser.add_argument("--benchmark", nargs="+", default=[], help="List of peer companies for benchmarking")
    parser.add_argument("--market_index", default="^GSPC", help="Market index for comparison")
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

def calculate_profitability_ratios(data):
    """Calculate profitability ratios from financial data."""
    income_stmt = data['income_stmt']
    balance_sheet = data['balance_sheet']
    
    # Calculate ratios
    results = pd.DataFrame(index=income_stmt.index)
    
    # Net Profit Margin (%) = (Net Income / Total Revenue) * 100
    if 'Net Income' in income_stmt.columns and 'Total Revenue' in income_stmt.columns:
        results['Net Profit Margin (%)'] = (income_stmt['Net Income'] / income_stmt['Total Revenue']) * 100
    
    # Operating Profit Margin (%) = (Operating Income / Total Revenue) * 100
    if 'Operating Income' in income_stmt.columns and 'Total Revenue' in income_stmt.columns:
        results['Operating Profit Margin (%)'] = (income_stmt['Operating Income'] / income_stmt['Total Revenue']) * 100
    
    # Return on Equity (ROE) (%) = (Net Income / Total Stockholder Equity) * 100
    if 'Net Income' in income_stmt.columns and 'Total Stockholder Equity' in balance_sheet.columns:
        results['Return on Equity (%)'] = (income_stmt['Net Income'] / balance_sheet['Total Stockholder Equity']) * 100
    
    # Return on Assets (ROA) (%) = (Net Income / Total Assets) * 100
    if 'Net Income' in income_stmt.columns and 'Total Assets' in balance_sheet.columns:
        results['Return on Assets (%)'] = (income_stmt['Net Income'] / balance_sheet['Total Assets']) * 100
    
    # Return on Capital Employed (ROCE) (%)
    # ROCE = EBIT / Capital Employed
    # Capital Employed = Total Assets - Current Liabilities
    if ('Operating Income' in income_stmt.columns and 
        'Total Assets' in balance_sheet.columns and 
        'Total Current Liabilities' in balance_sheet.columns):
        ebit = income_stmt['Operating Income']  # EBIT is often reported as Operating Income
        capital_employed = balance_sheet['Total Assets'] - balance_sheet['Total Current Liabilities']
        results['Return on Capital Employed (%)'] = (ebit / capital_employed) * 100
    
    # Earnings Per Share (EPS)
    results['EPS (₹ per share)'] = data['info'].get('trailingEPS', np.nan)
    
    return results

def plot_trend_graphs(company_ratios, benchmark_ratios=None, market_ratios=None, output_dir="./output"):
    """
    Plot trend graphs for specified ratios.
    
    Args:
        company_ratios: DataFrame with company ratios
        benchmark_ratios: Dictionary of DataFrames with benchmark companies' ratios
        market_ratios: DataFrame with market average ratios
        output_dir: Directory to save the plots
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # List of ratios to plot as trend graphs
    trend_ratios = [
        'Net Profit Margin (%)', 
        'Operating Profit Margin (%)', 
        'Return on Equity (%)', 
        'Return on Assets (%)',
        'Return on Capital Employed (%)'
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
            
            # Plot market average if available
            if market_ratios is not None and ratio in market_ratios.columns:
                market_ratios[ratio].plot(ax=ax, linestyle='-.', color='black', label="Market Average")
            
            plt.title(f"{ratio} Trend (Past 5 Years)")
            plt.ylabel(ratio)
            plt.xlabel("Year")
            plt.legend()
            plt.tight_layout()
            
            # Save the plot
            plt.savefig(os.path.join(output_dir, f"{ratio.replace(' ', '_').replace('(%)', 'Pct')}.png"))
            plt.close()

def display_single_numbers(company_ratios, benchmark_ratios=None, market_ratios=None):
    """
    Display single number ratios with benchmarking.
    
    Args:
        company_ratios: DataFrame with company ratios
        benchmark_ratios: Dictionary of DataFrames with benchmark companies' ratios
        market_ratios: DataFrame with market average ratios
    """
    # List of ratios to display as single numbers
    single_ratios = ['EPS (₹ per share)']
    
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
    
    # Get the market average
    if market_ratios is not None:
        for ratio in single_ratios:
            if ratio in market_ratios.columns:
                latest_values['Market Average'] = market_ratios[ratio].iloc[-1]
    
    # Display as a DataFrame
    latest_df = pd.DataFrame(latest_values, index=single_ratios)
    print("\nSingle Number Ratios (Latest Values):")
    print(latest_df)
    
    return latest_df

def main():
    """Main function to run the profitability ratio analysis."""
    args = parse_arguments()
    
    print(f"\nAnalyzing profitability ratios for {args.ticker}...")
    
    # Fetch data for the main company
    company_data = fetch_financial_data(args.ticker, args.period)
    company_ratios = calculate_profitability_ratios(company_data)
    
    # Fetch data for benchmark companies
    benchmark_ratios = {}
    for benchmark in args.benchmark:
        print(f"Fetching data for benchmark company: {benchmark}")
        benchmark_data = fetch_financial_data(benchmark, args.period)
        benchmark_ratios[benchmark] = calculate_profitability_ratios(benchmark_data)
    
    # Fetch market index data
    market_data = None
    market_ratios = None
    if args.market_index:
        print(f"Fetching data for market index: {args.market_index}")
        try:
            market_data = fetch_financial_data(args.market_index, args.period)
            market_ratios = calculate_profitability_ratios(market_data)
        except Exception as e:
            print(f"Warning: Failed to fetch market index data: {e}")
    
    # Plot trend graphs
    print("Generating trend graphs...")
    plot_trend_graphs(company_ratios, benchmark_ratios, market_ratios, args.output)
    
    # Display single number ratios
    print("Calculating single number ratios...")
    display_single_numbers(company_ratios, benchmark_ratios, market_ratios)
    
    print(f"\nAnalysis complete. Visualizations saved to {args.output} directory.")

if __name__ == "__main__":
    main()