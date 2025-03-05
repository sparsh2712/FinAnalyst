"""
Market Performance Ratios Analysis Script

This script calculates and visualizes market performance ratios for a given company
and benchmarks against market averages.

Ratios calculated:
1. Dividend Yield (%) (Trend Graph)
2. Beta (Stock Volatility) (Trend Graph)
3. Market Capitalization (Single Number)

Usage:
    python market_performance_ratios.py --ticker AAPL --period 5y --market_index ^GSPC
    
    Required arguments:
        --ticker: Company ticker symbol
        --period: Analysis period (e.g., 5y for 5 years)
    
    Optional arguments:
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
    parser = argparse.ArgumentParser(description="Calculate market performance ratios")
    parser.add_argument("--ticker", required=True, help="Company ticker symbol")
    parser.add_argument("--period", default="5y", help="Analysis period (e.g., 5y for 5 years)")
    parser.add_argument("--market_index", default="^GSPC", help="Market index for comparison")
    parser.add_argument("--output", default="./output", help="Output directory for saving visualizations")
    return parser.parse_args()

def fetch_financial_data(ticker, period="5y", market_index="^GSPC"):
    """Fetch financial data for a given ticker."""
    print("fetching market data")
    # Get the ticker object
    ticker = f"{ticker}.NS"
    tick = yf.Ticker(ticker)
    
    # Get stock price data for the period
    end_date = datetime.now()
    if period.endswith('y'):
        years = int(period[:-1])
        start_date = end_date - timedelta(days=365 * years)
    else:
        # Default to 5 years
        start_date = end_date - timedelta(days=365 * 5)
    
    # Get both the company stock data and market index data
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    market_data = yf.download(market_index, start=start_date, end=end_date)
    
    # Get dividend history
    try:
        dividends = tick.dividends
    except:
        dividends = pd.Series(dtype=float)
    
    print("succesfully fetched market data")
    return {
        'stock_data': stock_data,
        'market_data': market_data,
        'dividends': dividends,
        'info': tick.info
    }

def calculate_market_performance_ratios(data, ticker, period="5y"):
    """Calculate market performance ratios from financial data."""
    print("calculating market performance ratios")
    stock_data = data['stock_data']
    market_data = data['market_data']
    dividends = data['dividends']
    info = data['info']
    
    dividends.index = dividends.index.to_pydatetime()
    dividends.index = dividends.index.tz_localize(None)

    # Calculate ratios
    results = pd.DataFrame()
    
    # For yearly analysis, resample to yearly frequency
    stock_yearly = stock_data.resample('YE').last()
    
    # Dividend Yield (%) = (Annual Dividend Per Share / Stock Price) * 100
    # Calculate historical dividend yield
    dividend_yield = pd.DataFrame(index=stock_yearly.index, columns=['Dividend Yield (%)'])
    for year in stock_yearly.index:
        # Get dividends for the year
        print(f"year: {year}")
        year_start = datetime(year.year, 1, 1)
        year_end = datetime(year.year, 12, 31)
        
        # Filter dividends for the year
        year_dividends = dividends[(dividends.index >= year_start) & (dividends.index <= year_end)]
        # Calculate annual dividend
        annual_dividend = year_dividends.sum()
        # Calculate dividend yield
        if annual_dividend > 0:
            year = year.strftime('%Y-%m-%d')
            if (ticker, year) in stock_yearly.index:
                stock_price = stock_yearly.loc[(ticker, year), 'Close']
                dividend_yield.loc[year, 'Dividend Yield (%)'] = (annual_dividend / stock_price) * 100
        else:
            dividend_yield.loc[year, 'Dividend Yield (%)'] = 0
    # Beta (Stock Volatility)
    # Calculate rolling beta using 1-year windows with 3-month steps

    returns = stock_data['Close'].pct_change().dropna()
    market_returns = market_data['Close'].pct_change().dropna()
    
    
    # Combine returns into a single DataFrame and align dates
    stock_returns = returns.iloc[:, 0]
    market_returns = market_returns.iloc[:, 0]
    combined_returns = pd.DataFrame({'stock': stock_returns, 'market': market_returns})
    combined_returns = combined_returns.dropna()
    
    # Calculate rolling beta
    window_size = 252  # Approximately 1 year of trading days
    rolling_cov = combined_returns['stock'].rolling(window=window_size).cov(combined_returns['market'])
    rolling_var = combined_returns['market'].rolling(window=window_size).var()
    rolling_beta = rolling_cov / rolling_var
    
    # Resample to yearly for the chart
    beta_yearly = rolling_beta.resample('YE').last()
    beta_df = pd.DataFrame(beta_yearly, columns=['Beta'])
    
    # Current Market Capitalization
    market_cap = info.get('marketCap', np.nan)
    
    # Combine all results into a single DataFrame
    results = pd.concat([dividend_yield, beta_df], axis=1)
    results['Market Capitalization'] = market_cap
    
    print("Succesfully calculated performance ratios")

    return results

def plot_trend_graphs(company_ratios, market_ratios=None, output_dir="./output"):
    """
    Plot trend graphs for specified ratios.
    
    Args:
        company_ratios: DataFrame with company ratios
        market_ratios: DataFrame with market average ratios
        output_dir: Directory to save the plots
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # List of ratios to plot as trend graphs
    trend_ratios = ['Dividend Yield (%)', 'Beta']
    
    for ratio in trend_ratios:
        if ratio in company_ratios.columns:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Plot company data
            company_ratios[ratio].plot(ax=ax, marker='o', label=f"Company")
            
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

def display_single_numbers(company_ratios, market_ratios=None):
    """
    Display single number ratios with benchmarking.
    
    Args:
        company_ratios: DataFrame with company ratios
        market_ratios: DataFrame with market average ratios
    """
    # List of ratios to display as single numbers
    single_ratios = ['Market Capitalization']
    
    # Create a table for the latest values
    latest_values = {}
    
    # Get the latest value for the company
    for ratio in single_ratios:
        if ratio in company_ratios.columns:
            latest_values['Company'] = company_ratios[ratio].iloc[-1]
    
    # Get the market average if available
    if market_ratios is not None:
        for ratio in single_ratios:
            if ratio in market_ratios.columns:
                latest_values['Market Average'] = market_ratios[ratio].iloc[-1]
    
    # Display as a DataFrame
    latest_df = pd.DataFrame(latest_values, index=single_ratios)
    
    # Format market cap in billions
    latest_df = latest_df / 1_000_000_000
    latest_df = latest_df.applymap(lambda x: f"${x:.2f}B" if pd.notna(x) else "N/A")
    
    print("\nSingle Number Ratios (Latest Values):")
    print(latest_df)
    
    return latest_df

def main():
    """Main function to run the market performance ratio analysis."""
    args = parse_arguments()
    
    print(f"\nAnalyzing market performance ratios for {args.ticker}...")
    
    # Fetch data for the main company
    company_data = fetch_financial_data(args.ticker, args.period, args.market_index)
    company_ratios = calculate_market_performance_ratios(company_data, args.period)
    
    # Fetch market index data (for benchmarking)
    market_data = None
    market_ratios = None
    if args.market_index:
        print(f"Fetching data for market index: {args.market_index}")
        try:
            market_tick = yf.Ticker(args.market_index)
            market_info = {
                'stock_data': company_data['market_data'],  # Use the already fetched market data
                'market_data': company_data['market_data'],  # Same data for correlation with itself
                'dividends': market_tick.dividends,
                'info': market_tick.info
            }
            market_ratios = calculate_market_performance_ratios(market_info, args.period)
        except Exception as e:
            print(f"Warning: Failed to calculate market ratios: {e}")
    
    # Plot trend graphs
    print("Generating trend graphs...")
    plot_trend_graphs(company_ratios, market_ratios, args.output)
    
    # Display single number ratios
    print("Calculating single number ratios...")
    display_single_numbers(company_ratios, market_ratios)
    
    print(f"\nAnalysis complete. Visualizations saved to {args.output} directory.")

if __name__ == "__main__":
    main()