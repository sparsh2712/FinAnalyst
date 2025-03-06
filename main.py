"""
Financial Analysis Dashboard

This script creates a comprehensive dashboard for analyzing financial ratios.
It integrates all ratio calculation modules and provides a streamlined interface
for fetching data, calculating ratios, and visualizing results.

Usage:
    streamlit run financial_dashboard.py
    
This improved implementation:
1. Uses JSON-compatible data structures for easy debugging and storage
2. Eliminates multi-indexed DataFrames for better readability
3. Provides enhanced error handling and logging
4. Follows patterns from test scripts for consistency
"""

import os
import json
import logging
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import traceback

# Import utility modules
from financial_data_utils import fetch_financial_data, save_to_json, load_from_json, create_output_directories
from profitability_ratios import calculate_profitability_ratios, convert_ratios_to_dataframe as convert_profit_ratios
from liquidity_ratios import calculate_liquidity_ratios, convert_ratios_to_dataframe as convert_liquidity_ratios

# Attempt to import solvency and other ratio modules if available
try:
    from solvency_ratios import calculate_solvency_ratios, convert_ratios_to_dataframe as convert_solvency_ratios
    SOLVENCY_MODULE_AVAILABLE = True
except ImportError:
    logger.warning("Solvency ratios module not available")
    SOLVENCY_MODULE_AVAILABLE = False

try:
    from efficiency_ratios import calculate_efficiency_ratios, convert_ratios_to_dataframe as convert_efficiency_ratios
    EFFICIENCY_MODULE_AVAILABLE = True
except ImportError:
    logger.warning("Efficiency ratios module not available")
    EFFICIENCY_MODULE_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def map_company_to_ticker(company_name, mapping_file="comapny_ticker_map.csv"):
    """
    Map company name to ticker symbol using the mapping file.
    
    Args:
        company_name (str): Company name
        mapping_file (str): Path to mapping CSV file
        
    Returns:
        tuple: (ticker, company_name) or (None, None) if not found
    """
    try:
        df = pd.read_csv(mapping_file)
        
        # Try exact match (case-insensitive)
        exact_matches = df[df["Company Name"].str.lower() == company_name.lower()]
        if not exact_matches.empty:
            match = exact_matches.iloc[0]
            return match["Symbol"], match["Company Name"]
        
        # Try contains match
        contains_matches = df[df["Company Name"].str.contains(company_name, case=False)]
        if not contains_matches.empty:
            match = contains_matches.iloc[0]
            logger.info(f"Found approximate match: {match['Company Name']} ({match['Symbol']})")
            return match["Symbol"], match["Company Name"]
        
        # Try word matching
        words = company_name.lower().split()
        for word in words:
            if len(word) > 3:  # Only use words with more than 3 characters
                word_matches = df[df["Company Name"].str.lower().str.contains(r'\b{}\b'.format(word), regex=True)]
                if not word_matches.empty:
                    match = word_matches.iloc[0]
                    logger.info(f"Found word match on '{word}': {match['Company Name']} ({match['Symbol']})")
                    return match["Symbol"], match["Company Name"]
        
        logger.warning(f"No match found for company name: {company_name}")
        return None, None
    
    except Exception as e:
        logger.error(f"Error mapping company to ticker: {str(e)}")
        return None, None

def get_industry_peers(ticker, mapping_file="comapny_ticker_map.csv", max_peers=5):
    """
    Get industry peers for a given ticker.
    
    Args:
        ticker (str): Company ticker symbol
        mapping_file (str): Path to mapping CSV file
        max_peers (int): Maximum number of peers to return
        
    Returns:
        list: List of ticker symbols for industry peers
    """
    try:
        df = pd.read_csv(mapping_file)
        
        # Find the company's industry
        company_row = df[df["Symbol"] == ticker]
        if company_row.empty:
            logger.warning(f"Ticker {ticker} not found in mapping file")
            return []
        
        industry = company_row.iloc[0]["Industry"]
        
        # Find other companies in the same industry
        industry_peers = df[(df["Industry"] == industry) & (df["Symbol"] != ticker)]
        
        # Return ticker symbols of peers (up to max_peers)
        return industry_peers.head(max_peers)["Symbol"].tolist()
    
    except Exception as e:
        logger.error(f"Error finding industry peers: {str(e)}")
        return []

def analyze_company(ticker, company_name, period="5y", benchmark_tickers=None, output_dir="./output", progress_callback=None):
    """
    Analyze financial ratios for a company.
    
    Args:
        ticker (str): Company ticker symbol
        company_name (str): Company name
        period (str): Analysis period (e.g., "5y" for 5 years)
        benchmark_tickers (list): List of benchmark ticker symbols
        output_dir (str): Base output directory
        progress_callback (function): Optional callback for progress updates
        
    Returns:
        dict: Dictionary with analysis results
    """
    # Create output directories
    directories = create_output_directories(output_dir)
    
    # Fetch and save data
    data_file = os.path.join(directories['json'], f"{ticker}_data.json")
    
    try:
        # Update progress if callback provided
        if progress_callback:
            progress_callback(0.1, f"Finding financial data for {company_name}")
            
        # Check if data already exists
        if os.path.exists(data_file):
            logger.info(f"Loading existing data for {ticker} from {data_file}")
            data = load_from_json(data_file)
        else:
            logger.info(f"Fetching new data for {ticker}")
            data = fetch_financial_data(ticker, period)
            save_to_json(data, data_file)
            
        if progress_callback:
            progress_callback(0.2, f"Analyzing {company_name} financial data")
        
        # Calculate ratios
        logger.info(f"Calculating ratios for {ticker}")
        
        # Profitability ratios
        profit_ratios = calculate_profitability_ratios(data)
        profit_df = convert_profit_ratios(profit_ratios)
        
        # Liquidity ratios
        liquidity_ratios = calculate_liquidity_ratios(data)
        liquidity_df = convert_liquidity_ratios(liquidity_ratios)
        
        # Fetch and calculate benchmark data if provided
        benchmark_data = {}
        if benchmark_tickers:
            if progress_callback:
                progress_callback(0.3, f"Collecting benchmark data for comparison")
                
            for i, b_ticker in enumerate(benchmark_tickers):
                if progress_callback:
                    progress_percent = 0.3 + (0.2 * (i / len(benchmark_tickers)))
                    progress_callback(progress_percent, f"Processing benchmark: {b_ticker}")
                
                b_data_file = os.path.join(directories['json'], f"{b_ticker}_data.json")
                
                if os.path.exists(b_data_file):
                    logger.info(f"Loading existing data for benchmark {b_ticker}")
                    b_data = load_from_json(b_data_file)
                else:
                    logger.info(f"Fetching new data for benchmark {b_ticker}")
                    b_data = fetch_financial_data(b_ticker, period)
                    save_to_json(b_data, b_data_file)
                
                # Calculate benchmark ratios
                b_profit_ratios = calculate_profitability_ratios(b_data)
                b_profit_df = convert_profit_ratios(b_profit_ratios)
                
                b_liquidity_ratios = calculate_liquidity_ratios(b_data)
                b_liquidity_df = convert_liquidity_ratios(b_liquidity_ratios)
                
                benchmark_data[b_ticker] = {
                    'data': b_data,
                    'profit_df': b_profit_df,
                    'liquidity_df': b_liquidity_df
                }
        
        # Generate visualizations
        logger.info(f"Generating visualizations for {ticker}")
        
        if progress_callback:
            progress_callback(0.6, f"Generating visualizations")
            
        # Create benchmark dataframes dictionary for plotting
        benchmark_profit_dfs = {ticker: data['profit_df'] for ticker, data in benchmark_data.items()}
        benchmark_liquidity_dfs = {ticker: data['liquidity_df'] for ticker, data in benchmark_data.items()}
        
        # Plot profitability ratios
        for ratio in ['Net Profit Margin (%)', 'Operating Profit Margin (%)', 
                     'Return on Equity (%)', 'Return on Assets (%)', 
                     'Return on Capital Employed (%)']:
            if ratio in profit_df.columns:
                from profitability_ratios import plot_trend_graph
                plot_trend_graph(profit_df, ratio, company_name, benchmark_profit_dfs, 
                                directories['profitability'])
        
        # Plot liquidity ratios
        for ratio in ['Current Ratio', 'Quick Ratio']:
            if ratio in liquidity_df.columns:
                from liquidity_ratios import plot_trend_graph
                plot_trend_graph(liquidity_df, ratio, company_name, benchmark_liquidity_dfs,
                                directories['liquidity'])
        
        # Display single number ratios
        if 'EPS (₹ per share)' in profit_df.columns:
            from profitability_ratios import display_latest_values
            eps_table = display_latest_values(profit_df, 'EPS (₹ per share)', company_name, 
                                             benchmark_profit_dfs)
            logger.info(f"EPS Table:\n{eps_table}")
        
        if 'Cash Ratio' in liquidity_df.columns:
            from liquidity_ratios import display_latest_values
            cash_ratio_table = display_latest_values(liquidity_df, 'Cash Ratio', company_name,
                                                   benchmark_liquidity_dfs)
            logger.info(f"Cash Ratio Table:\n{cash_ratio_table}")
        
        # Update progress to complete
        if progress_callback:
            progress_callback(1.0, f"Analysis complete for {company_name}")
            
        # Return analysis results
        return {
            'company': {
                'ticker': ticker,
                'name': company_name,
                'data': data,
                'profit_df': profit_df,
                'liquidity_df': liquidity_df
            },
            'benchmarks': benchmark_data,
            'directories': directories
        }
    
    except Exception as e:
        logger.error(f"Error analyzing company {ticker}: {str(e)}")
        logger.error(traceback.format_exc())
        if progress_callback:
            progress_callback(1.0, f"Error: {str(e)}")
        raise

def run_streamlit_app():
    """
    Run the Streamlit app for financial ratio analysis.
    """
    st.set_page_config(
        page_title="Financial Ratio Analysis Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Financial Ratio Analysis Dashboard")
    st.markdown("This dashboard analyzes financial ratios for companies listed in the database.")
    
    # Sidebar
    st.sidebar.title("Financial Ratio Analysis")
    st.sidebar.markdown("Select a company and parameters for analysis.")
    
    # Company selection
    selection_method = st.sidebar.radio("Select company by:", ["Company Name", "Search by Name"])
    
    company_name = None
    ticker = None
    
    if selection_method == "Company Name":
        try:
            # Load company mapping
            company_df = pd.read_csv("comapny_ticker_map.csv")
            sorted_companies = sorted(company_df["Company Name"].tolist())
            
            selected_company = st.sidebar.selectbox("Select Company:", sorted_companies)
            if selected_company:
                company_name = selected_company
                ticker = company_df[company_df["Company Name"] == selected_company]["Symbol"].iloc[0]
        except Exception as e:
            st.sidebar.error(f"Error loading company list: {str(e)}")
    else:
        # Allow entering a company name
        search_term = st.sidebar.text_input("Search for Company:")
        if search_term:
            ticker, company_name = map_company_to_ticker(search_term)
            if ticker and company_name:
                st.sidebar.success(f"Found: {company_name} ({ticker})")
            else:
                st.sidebar.error(f"No matching company found for '{search_term}'")
    
    # Analysis period selection
    period = st.sidebar.selectbox("Select Analysis Period:", ["1y", "3y", "5y", "10y"], index=2)
    
    # Benchmark selection
    st.sidebar.header("Benchmark")
    use_benchmark = st.sidebar.checkbox("Compare with benchmark companies")
    
    benchmark_tickers = []
    if use_benchmark and ticker:
        # Find industry peers for benchmarking
        try:
            industry_peers = get_industry_peers(ticker)
            if industry_peers:
                selected_benchmarks = st.sidebar.multiselect(
                    "Select benchmark companies:",
                    industry_peers,
                    max_selections=3
                )
                benchmark_tickers = selected_benchmarks
            else:
                st.sidebar.warning("No industry peers found for benchmarking.")
        except Exception as e:
            st.sidebar.error(f"Error finding benchmark companies: {str(e)}")
    
    # Analysis button
    analyze_button = st.sidebar.button("Analyze", type="primary")
    
    # Main content area
    if not ticker:
        st.info("Please select a company to analyze.")
        
        # Show instruction card
        st.markdown("""
        ## Financial Ratio Analysis
        
        This dashboard helps you analyze various financial ratios for companies, including:
        
        1. **Profitability Ratios** - Measure a company's ability to generate profit
        2. **Liquidity Ratios** - Assess a company's ability to pay short-term obligations
        3. **Solvency Ratios** - Evaluate a company's long-term financial stability
        4. **Efficiency Ratios** - Analyze how effectively a company uses its resources
        5. **Valuation Ratios** - Assess a company's stock value relative to financial metrics
        
        To get started:
        1. Select a company using the sidebar
        2. Choose an analysis period
        3. Optionally select benchmark companies for comparison
        4. Click "Analyze"
        """)
    
    elif analyze_button:
        try:
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(progress, status):
                progress_bar.progress(progress)
                status_text.text(status)
            
            # Run analysis
            results = analyze_company(
                ticker, 
                company_name, 
                period=period, 
                benchmark_tickers=benchmark_tickers, 
                progress_callback=update_progress
            )
            
            # Display results
            if results:
                st.success(f"Analysis complete for {company_name}")
                
                # Create tabs for each category
                tab_profit, tab_liquid = st.tabs(["Profitability", "Liquidity"])
                
                # Profitability Ratios
                with tab_profit:
                    st.header("Profitability Ratios")
                    profit_df = results['company']['profit_df']
                    
                    if not profit_df.empty:
                        # Display trend ratios in 2 columns
                        trend_ratios = [
                            'Net Profit Margin (%)', 
                            'Operating Profit Margin (%)', 
                            'Return on Equity (%)', 
                            'Return on Assets (%)', 
                            'Return on Capital Employed (%)'
                        ]
                        
                        col1, col2 = st.columns(2)
                        
                        for i, ratio in enumerate(trend_ratios):
                            if ratio in profit_df.columns:
                                with col1 if i % 2 == 0 else col2:
                                    st.subheader(ratio)
                                    img_path = os.path.join(
                                        results['directories']['profitability'],
                                        f"{ratio.replace(' ', '_').replace('(', '').replace(')', '').replace('%', 'Pct')}.png"
                                    )
                                    if os.path.exists(img_path):
                                        st.image(img_path)
                                    else:
                                        st.warning(f"Chart not available for {ratio}")
                        
                        # Show EPS
                        st.subheader("Earnings Per Share (₹)")
                        if 'EPS (₹ per share)' in profit_df.columns:
                            st.metric("Latest EPS", f"₹{profit_df['EPS (₹ per share)'].iloc[-1]:.2f}")
                            
                            # Show comparison with benchmarks
                            if benchmark_tickers:
                                st.subheader("EPS Comparison")
                                eps_data = {'Company': [company_name]}
                                eps_values = [profit_df['EPS (₹ per share)'].iloc[-1]]
                                
                                for b_ticker, b_data in results['benchmarks'].items():
                                    if 'EPS (₹ per share)' in b_data['profit_df'].columns:
                                        eps_data[b_ticker] = [b_data['profit_df']['EPS (₹ per share)'].iloc[-1]]
                                        eps_values.append(b_data['profit_df']['EPS (₹ per share)'].iloc[-1])
                                
                                eps_df = pd.DataFrame(eps_data)
                                st.dataframe(eps_df)
                    else:
                        st.warning("No profitability ratio data available.")
                
                # Liquidity Ratios
                with tab_liquid:
                    st.header("Liquidity Ratios")
                    liquidity_df = results['company']['liquidity_df']
                    
                    if not liquidity_df.empty:
                        # Display trend ratios in 2 columns
                        trend_ratios = ['Current Ratio', 'Quick Ratio']
                        
                        col1, col2 = st.columns(2)
                        
                        for i, ratio in enumerate(trend_ratios):
                            if ratio in liquidity_df.columns:
                                with col1 if i % 2 == 0 else col2:
                                    st.subheader(ratio)
                                    img_path = os.path.join(
                                        results['directories']['liquidity'],
                                        f"{ratio.replace(' ', '_')}.png"
                                    )
                                    if os.path.exists(img_path):
                                        st.image(img_path)
                                    else:
                                        st.warning(f"Chart not available for {ratio}")
                        
                        # Show Cash Ratio
                        st.subheader("Cash Ratio")
                        if 'Cash Ratio' in liquidity_df.columns:
                            st.metric("Latest Cash Ratio", f"{liquidity_df['Cash Ratio'].iloc[-1]:.2f}")
                            
                            # Show comparison with benchmarks
                            if benchmark_tickers:
                                st.subheader("Cash Ratio Comparison")
                                cash_data = {'Company': [company_name]}
                                cash_values = [liquidity_df['Cash Ratio'].iloc[-1]]
                                
                                for b_ticker, b_data in results['benchmarks'].items():
                                    if 'Cash Ratio' in b_data['liquidity_df'].columns:
                                        cash_data[b_ticker] = [b_data['liquidity_df']['Cash Ratio'].iloc[-1]]
                                        cash_values.append(b_data['liquidity_df']['Cash Ratio'].iloc[-1])
                                
                                cash_df = pd.DataFrame(cash_data)
                                st.dataframe(cash_df)
                    else:
                        st.warning("No liquidity ratio data available.")
                
                # Download data button
                st.header("Download Data")
                
                # Combine all ratios into a single DataFrame for download
                combined_df = pd.DataFrame()
                
                # Add profitability ratios
                if not profit_df.empty:
                    for col in profit_df.columns:
                        combined_df[f"Profitability_{col}"] = profit_df[col]
                
                # Add liquidity ratios
                if not liquidity_df.empty:
                    for col in liquidity_df.columns:
                        combined_df[f"Liquidity_{col}"] = liquidity_df[col]
                
                # Convert to CSV
                csv = combined_df.to_csv().encode('utf-8')
                
                st.download_button(
                    label="Download Financial Ratios as CSV",
                    data=csv,
                    file_name=f"{company_name}_financial_ratios.csv",
                    mime="text/csv",
                )
        
        except Exception as e:
            st.error(f"Error analyzing company: {str(e)}")
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    # Check if script is being run directly or via streamlit
    import sys
    if len(sys.argv) > 1 and sys.argv[0].endswith('streamlit'):
        # Script is being run via streamlit
        run_streamlit_app()
    else:
        # Script is being run directly, parse arguments
        parser = argparse.ArgumentParser(description="Financial Ratio Analysis")
        parser.add_argument("--company", required=True, help="Company name")
        parser.add_argument("--period", default="5y", help="Analysis period (e.g., 5y for 5 years)")
        parser.add_argument("--benchmark", nargs="+", default=[], help="List of benchmark companies")
        parser.add_argument("--output", default="./output", help="Output directory")
        
        args = parser.parse_args()
        
        # Map company name to ticker
        ticker, company_name = map_company_to_ticker(args.company)
        
        if ticker and company_name:
            print(f"Analyzing {company_name} ({ticker})")
            
            # Map benchmark companies to tickers
            benchmark_tickers = []
            for benchmark in args.benchmark:
                b_ticker, b_name = map_company_to_ticker(benchmark)
                if b_ticker:
                    benchmark_tickers.append(b_ticker)
                    print(f"Added benchmark: {b_name} ({b_ticker})")
            
            # Run analysis
            analyze_company(ticker, company_name, args.period, benchmark_tickers, args.output)