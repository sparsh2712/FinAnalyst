"""
Combined Financial Ratio Dashboard

This script creates a comprehensive dashboard of all financial ratios for a given company
and benchmarks against industry peers and market averages.

Usage:
    python combined_dashboard.py --ticker AAPL --period 5y --benchmark MSFT GOOGL --market_index ^GSPC
    
    Required arguments:
        --ticker: Company ticker symbol
        --period: Analysis period (e.g., 5y for 5 years)
    
    Optional arguments:
        --benchmark: List of peer companies for benchmarking
        --market_index: Market index for comparison (default: ^GSPC for S&P 500)
        --output: Output directory for saving visualizations (default: ./output)
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from datetime import datetime, timedelta

# Import the ratio calculation modules
# Make sure these are in the same directory or in your Python path
try:
    from profitability_ratios import fetch_financial_data as fetch_profit_data, calculate_profitability_ratios
    from liquidity_ratios import calculate_liquidity_ratios
    from solvency_ratios import calculate_solvency_ratios
    from efficiency_ratios import calculate_efficiency_ratios
    from valuation_ratios import calculate_valuation_ratios
    from market_performance_ratios import fetch_financial_data as fetch_market_data, calculate_market_performance_ratios
except ImportError:
    print("Error: Could not import ratio calculation modules.")
    print("Make sure all the individual ratio scripts are in the same directory.")
    sys.exit(1)

# Set plotting style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Create a comprehensive financial ratio dashboard")
    parser.add_argument("--ticker", required=True, help="Company ticker symbol")
    parser.add_argument("--period", default="5y", help="Analysis period (e.g., 5y for 5 years)")
    parser.add_argument("--benchmark", nargs="+", default=[], help="List of peer companies for benchmarking")
    parser.add_argument("--market_index", default="^GSPC", help="Market index for comparison")
    parser.add_argument("--output", default="./output", help="Output directory for saving visualizations")
    return parser.parse_args()

def create_dashboard(ticker, period="5y", benchmark=None, market_index="^GSPC", output_dir="./output"):
    """
    Create a comprehensive financial ratio dashboard.
    
    Args:
        ticker: Company ticker symbol
        period: Analysis period (e.g., 5y for 5 years)
        benchmark: List of peer companies for benchmarking
        market_index: Market index for comparison
        output_dir: Directory to save the visualizations
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n===== Financial Ratio Analysis for {ticker} =====\n")
    
    # 1. Fetch all required data
    print("Fetching financial data...")
    company_financial_data = fetch_profit_data(ticker, period)
    company_market_data = fetch_market_data(ticker, period, market_index)
    
    # 2. Calculate all ratios
    print("\nCalculating financial ratios...\n")
    
    # Profitability ratios
    print("1. Profitability Ratios:")
    profitability_ratios = calculate_profitability_ratios(company_financial_data)
    print_dataframe_info(profitability_ratios, "Profitability Ratios")
    
    # Liquidity ratios
    print("\n2. Liquidity Ratios:")
    liquidity_ratios = calculate_liquidity_ratios(company_financial_data)
    print_dataframe_info(liquidity_ratios, "Liquidity Ratios")
    
    # Solvency ratios
    print("\n3. Solvency Ratios:")
    solvency_ratios = calculate_solvency_ratios(company_financial_data)
    print_dataframe_info(solvency_ratios, "Solvency Ratios")
    
    # Efficiency ratios
    print("\n4. Efficiency Ratios:")
    efficiency_ratios = calculate_efficiency_ratios(company_financial_data)
    print_dataframe_info(efficiency_ratios, "Efficiency Ratios")
    
    # Valuation ratios
    print("\n5. Valuation Ratios:")
    valuation_ratios = calculate_valuation_ratios(company_financial_data)
    print_dataframe_info(valuation_ratios, "Valuation Ratios")
    
    # Market performance ratios
    print("\n6. Market Performance Ratios:")
    market_ratios = calculate_market_performance_ratios(company_market_data, period)
    print_dataframe_info(market_ratios, "Market Performance Ratios")
    
    # 3. Calculate benchmark ratios if specified
    benchmark_data = {}
    if benchmark:
        print("\nCalculating benchmark ratios...")
        for company in benchmark:
            print(f"  Processing {company}...")
            try:
                # Fetch data for benchmark company
                company_fin_data = fetch_profit_data(company, period)
                company_mkt_data = fetch_market_data(company, period, market_index)
                
                # Calculate ratios
                benchmark_data[company] = {
                    'profitability': calculate_profitability_ratios(company_fin_data),
                    'liquidity': calculate_liquidity_ratios(company_fin_data),
                    'solvency': calculate_solvency_ratios(company_fin_data),
                    'efficiency': calculate_efficiency_ratios(company_fin_data),
                    'valuation': calculate_valuation_ratios(company_fin_data),
                    'market': calculate_market_performance_ratios(company_mkt_data, period)
                }
            except Exception as e:
                print(f"  Warning: Failed to process benchmark {company}: {e}")
    
    # 4. Calculate market index ratios if specified
    market_index_data = None
    if market_index:
        print(f"\nCalculating market index ratios for {market_index}...")
        try:
            # We'll only use market index data for market performance ratios
            index_data = fetch_market_data(market_index, period, market_index)
            market_index_ratios = calculate_market_performance_ratios(index_data, period)
            market_index_data = {'market': market_index_ratios}
        except Exception as e:
            print(f"  Warning: Failed to process market index {market_index}: {e}")
    
    # 5. Generate visualizations
    print("\nGenerating visualizations...")
    
    # Create a subdirectory for each ratio category
    categories = [
        ('profitability', profitability_ratios),
        ('liquidity', liquidity_ratios),
        ('solvency', solvency_ratios),
        ('efficiency', efficiency_ratios),
        ('valuation', valuation_ratios),
        ('market', market_ratios)
    ]
    
    for category_name, ratios in categories:
        category_dir = os.path.join(output_dir, category_name)
        os.makedirs(category_dir, exist_ok=True)
        
        print(f"  Creating {category_name} charts...")
        for ratio in ratios.columns:
            # Skip non-numeric columns or empty data
            if not pd.api.types.is_numeric_dtype(ratios[ratio]) or ratios[ratio].isnull().all():
                continue
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Plot main company data
            ratios[ratio].plot(ax=ax, marker='o', linewidth=2, label=ticker)
            
            # Plot benchmark data if available
            if benchmark_data:
                for company, data in benchmark_data.items():
                    if category_name in data and ratio in data[category_name].columns:
                        data[category_name][ratio].plot(ax=ax, linestyle='--', marker='x', label=company)
            
            # Plot market index data if available and relevant
            if market_index_data and category_name == 'market' and ratio in market_index_data['market'].columns:
                market_index_data['market'][ratio].plot(ax=ax, linestyle='-.', color='black', label=f"{market_index} (Market)")
            
            # Set title and labels
            plt.title(f"{ratio} - {ticker} vs Benchmarks")
            plt.ylabel(ratio)
            plt.xlabel("Year")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            # Save figure
            fig_path = os.path.join(category_dir, f"{ratio.replace(' ', '_').replace('/', '_').replace('(%)', 'Pct')}.png")
            plt.savefig(fig_path)
            plt.close()
    
    # 6. Generate summary report
    print("\nGenerating summary report...")
    generate_summary_report(
        ticker, 
        profitability_ratios, 
        liquidity_ratios, 
        solvency_ratios, 
        efficiency_ratios, 
        valuation_ratios, 
        market_ratios, 
        benchmark_data, 
        market_index_data, 
        output_dir
    )
    
    print(f"\nAnalysis complete. Results saved to {output_dir}")

def print_dataframe_info(df, name):
    """Print information about a DataFrame."""
    if df.empty:
        print(f"  {name}: No data available")
    else:
        print(f"  {name}: {len(df.columns)} ratios over {len(df)} periods")
        for col in df.columns:
            non_null = df[col].count()
            print(f"    - {col}: {non_null} values")

def generate_summary_report(
    ticker, 
    profitability, 
    liquidity, 
    solvency, 
    efficiency, 
    valuation, 
    market, 
    benchmark_data, 
    market_index_data, 
    output_dir
):
    """Generate a summary report of all financial ratios."""
    report_path = os.path.join(output_dir, "financial_ratio_summary.html")
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Ratio Analysis: {ticker}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ text-align: left; padding: 8px; }}
            th {{ background-color: #2c3e50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .chart-container {{ display: flex; flex-wrap: wrap; justify-content: space-around; }}
            .chart {{ margin: 10px; border: 1px solid #ddd; padding: 5px; }}
        </style>
    </head>
    <body>
        <h1>Financial Ratio Analysis: {ticker}</h1>
        <p>Analysis Date: {datetime.now().strftime('%Y-%m-%d')}</p>
    """
    
    # Add summary tables for each category
    ratio_categories = [
        ('Profitability Ratios', profitability),
        ('Liquidity Ratios', liquidity),
        ('Solvency Ratios', solvency),
        ('Efficiency Ratios', efficiency),
        ('Valuation Ratios', valuation),
        ('Market Performance Ratios', market)
    ]
    
    for category_name, ratios in ratio_categories:
        if not ratios.empty:
            html_content += f"""
            <h2>{category_name}</h2>
            <table border="1">
                <tr>
                    <th>Ratio</th>
                    <th>Latest Value</th>
                    <th>5-Year Average</th>
                    <th>Trend</th>
                </tr>
            """
            
            for column in ratios.columns:
                if pd.api.types.is_numeric_dtype(ratios[column]) and not ratios[column].isnull().all():
                    latest_value = ratios[column].iloc[-1]
                    avg_value = ratios[column].mean()
                    
                    # Determine trend (↑, ↓, or →)
                    if len(ratios) > 1:
                        first_value = ratios[column].iloc[0]
                        if latest_value > first_value * 1.05:  # 5% increase threshold
                            trend = "↑ (Improving)"
                        elif latest_value < first_value * 0.95:  # 5% decrease threshold
                            trend = "↓ (Declining)"
                        else:
                            trend = "→ (Stable)"
                    else:
                        trend = "N/A"
                    
                    html_content += f"""
                    <tr>
                        <td>{column}</td>
                        <td>{latest_value:.2f}</td>
                        <td>{avg_value:.2f}</td>
                        <td>{trend}</td>
                    </tr>
                    """
            
            html_content += "</table>"
            
            # Add charts
            category_dir = os.path.join(output_dir, category_name.split()[0].lower())
            html_content += f"""
            <div class="chart-container">
            """
            
            for column in ratios.columns:
                chart_filename = f"{column.replace(' ', '_').replace('/', '_').replace('(%)', 'Pct')}.png"
                chart_path = os.path.join(category_dir, chart_filename)
                
                if os.path.exists(chart_path):
                    relative_path = os.path.join(category_name.split()[0].lower(), chart_filename)
                    html_content += f"""
                    <div class="chart">
                        <h3>{column}</h3>
                        <img src="{relative_path}" alt="{column} Chart" width="400">
                    </div>
                    """
            
            html_content += """
            </div>
            """
    
    # Add benchmark comparison if available
    if benchmark_data:
        html_content += """
        <h2>Benchmark Comparison (Latest Values)</h2>
        <table border="1">
            <tr>
                <th>Ratio</th>
                <th>Company</th>
        """
        
        # Add benchmark companies to the header
        for company in benchmark_data.keys():
            html_content += f"<th>{company}</th>"
        
        html_content += """
            </tr>
        """
        
        # Add ratios and values
        for category_name, ratios in ratio_categories:
            category_key = category_name.split()[0].lower()
            
            for column in ratios.columns:
                if pd.api.types.is_numeric_dtype(ratios[column]) and not ratios[column].isnull().all():
                    html_content += f"""
                    <tr>
                        <td>{column}</td>
                        <td>{ratios[column].iloc[-1]:.2f}</td>
                    """
                    
                    for company, data in benchmark_data.items():
                        if category_key in data and column in data[category_key].columns:
                            benchmark_value = data[category_key][column].iloc[-1]
                            html_content += f"<td>{benchmark_value:.2f}</td>"
                        else:
                            html_content += "<td>N/A</td>"
                    
                    html_content += "</tr>"
        
        html_content += "</table>"
    
    # Add conclusion
    html_content += """
        <h2>Analysis Conclusion</h2>
        <p>This report provides a comprehensive overview of the company's financial ratios across profitability, liquidity, solvency, efficiency, valuation, and market performance categories. The charts visualize trends over time and benchmark comparisons. For detailed analysis of specific ratios, refer to the individual charts.</p>
    """
    
    # Close the HTML document
    html_content += """
    </body>
    </html>
    """
    
    # Write the HTML file
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    print(f"Summary report saved to: {report_path}")

def main():
    """Main function to run the dashboard creation."""
    args = parse_arguments()
    create_dashboard(
        args.ticker,
        args.period,
        args.benchmark,
        args.market_index,
        args.output
    )

if __name__ == "__main__":
    main()