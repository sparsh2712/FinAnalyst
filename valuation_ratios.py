"""
Valuation Ratios Analysis Script

This script calculates and visualizes valuation ratios for a given company
and benchmarks against industry averages and market averages.

Ratios calculated:
1. Price-to-Earnings (P/E) Ratio (Trend Graph)
2. Price-to-Book (P/B) Ratio (Trend Graph)
3. Enterprise Value to EBITDA (EV/EBITDA) (Single Number)

Usage:
    python valuation_ratios.py --ticker AAPL --period 5y --benchmark MSFT GOOGL --market_index ^GSPC
    
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
    parser = argparse.ArgumentParser(description="Calculate valuation ratios")
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

def calculate_valuation_ratios(data):
    """Calculate valuation ratios from financial data."""
    print("calculating valuation ratios")
    income_stmt = data['income_stmt']
    balance_sheet = data['balance_sheet']
    stock_data = data['stock_data']
    info = data['info']
    
    # Calculate ratios
    results = pd.DataFrame()
    
    # For historical P/E and P/B ratios, we need to align stock prices with financial statement dates
    fin_dates = income_stmt.index
    yearly_stock_prices = {}
    
    for date in fin_dates:
        # Find closest stock price to financial date
        closest_date = stock_data.index[stock_data.index <= date][-1]
        yearly_stock_prices[date] = stock_data.loc[closest_date, 'Close']
    
    # Create a DataFrame with historical stock prices
    price_df = pd.Series(yearly_stock_prices, name='Stock Price').to_frame()
    
    # Add dates as index
    results = pd.DataFrame(index=fin_dates)
    
    # Price-to-Earnings (P/E) Ratio = Stock Price / Earnings Per Share
    if 'Net Income' in income_stmt.columns and 'Stock Price' in price_df.columns:
        # Get outstanding shares for each period
        # Note: In a real-world scenario, you would need historical shares outstanding
        # Here we'll use the current shares outstanding as an approximation
        shares_outstanding = info.get('sharesOutstanding', None)
        
        if shares_outstanding:
            # Calculate historical EPS
            income_stmt['EPS'] = income_stmt['Net Income'] / shares_outstanding
            
            # Calculate P/E ratio
            results['P/E Ratio'] = price_df['Stock Price'] / income_stmt['EPS']
    
    # Price-to-Book (P/B) Ratio = Stock Price / Book Value Per Share
    if 'Total Stockholder Equity' in balance_sheet.columns and 'Stock Price' in price_df.columns:
        # Get outstanding shares for each period
        shares_outstanding = info.get('sharesOutstanding', None)
        
        if shares_outstanding:
            # Calculate historical Book Value Per Share
            balance_sheet['Book Value Per Share'] = balance_sheet['Total Stockholder Equity'] / shares_outstanding
            
            # Calculate P/B ratio
            results['P/B Ratio'] = price_df['Stock Price'] / balance_sheet['Book Value Per Share']
    
    # Enterprise Value to EBITDA (EV/EBITDA)
    # This is typically calculated using current market data rather than historical
    # We'll use the trailing EV/EBITDA from the info object
    results['EV/EBITDA'] = info.get('enterpriseToEbitda', np.nan)
    results = results.reset_index()
    results.columns = results.columns.map('_'.join)
    print("succesfully calculated valuation ratios")
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
    trend_ratios = ['P/E Ratio', 'P/B Ratio']
    
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
            plt.savefig(os.path.join(output_dir, f"{ratio.replace(' ', '_').replace('/', '_')}.png"))
            plt.close()

def display_single_numbers(company_ratios, benchmark_ratios=None):
    """
    Display single number ratios with benchmarking.
    
    Args:
        company_ratios: DataFrame with company ratios
        benchmark_ratios: Dictionary of DataFrames with benchmark companies' ratios
    """
    # List of ratios to display as single numbers
    single_ratios = ['EV/EBITDA']
    
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
    """Main function to run the valuation ratio analysis."""
    args = parse_arguments()
    
    print(f"\nAnalyzing valuation ratios for {args.ticker}...")
    
    # Fetch data for the main company
    company_data = fetch_financial_data(args.ticker, args.period)
    company_ratios = calculate_valuation_ratios(company_data)
    
    # Fetch data for benchmark companies
    benchmark_ratios = {}
    for benchmark in args.benchmark:
        print(f"Fetching data for benchmark company: {benchmark}")
        benchmark_data = fetch_financial_data(benchmark, args.period)
        benchmark_ratios[benchmark] = calculate_valuation_ratios(benchmark_data)
    
    # Fetch market index data
    market_data = None
    market_ratios = None
    if args.market_index:
        print(f"Fetching data for market index: {args.market_index}")
        try:
            market_data = fetch_financial_data(args.market_index, args.period)
            market_ratios = calculate_valuation_ratios(market_data)
        except Exception as e:
            print(f"Warning: Failed to fetch market index data: {e}")
    
    # Plot trend graphs
    print("Generating trend graphs...")
    plot_trend_graphs(company_ratios, benchmark_ratios, market_ratios, args.output)
    
    # Display single number ratios
    print("Calculating single number ratios...")
    display_single_numbers(company_ratios, benchmark_ratios)
    
    print(f"\nAnalysis complete. Visualizations saved to {args.output} directory.")

if __name__ == "__main__":
    main()