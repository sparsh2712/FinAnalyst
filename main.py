"""
Financial Ratio Analysis Dashboard

This script launches a Streamlit dashboard for analyzing financial ratios
of companies listed in the company_ticker_map.csv file.

Usage:
    streamlit run main.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import yfinance as yf

# Import ratio calculation modules
from profitability_ratios import calculate_profitability_ratios, fetch_financial_data as fetch_profit_data
from liquidity_ratios import calculate_liquidity_ratios
from solvency_ratios import calculate_solvency_ratios
from efficiency_ratios import calculate_efficiency_ratios
from valuation_ratios import calculate_valuation_ratios
from market_performance_ratios import fetch_financial_data as fetch_market_data, calculate_market_performance_ratios

# Set page configuration
st.set_page_config(
    page_title="Financial Ratio Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load company to ticker mapping
@st.cache_data
def load_company_ticker_map():
    try:
        return pd.read_csv("comapny_ticker_map.csv")
    except Exception as e:
        st.error(f"Error loading company ticker map: {e}")
        return pd.DataFrame(columns=["Company Name", "Symbol", "Industry"])

# Find ticker for company name with enhanced matching
def find_ticker(company_name, company_df):
    # First, try exact match (case-insensitive)
    exact_matches = company_df[company_df["Company Name"].str.lower() == company_name.lower()]
    if not exact_matches.empty:
        return exact_matches.iloc[0]["Symbol"], exact_matches.iloc[0]["Company Name"]
    
    # If no exact match, try contains match
    contains_matches = company_df[company_df["Company Name"].str.contains(company_name, case=False)]
    if not contains_matches.empty:
        # Return the first match, but also show alternatives
        best_match = contains_matches.iloc[0]
        st.info(f"Using best match: {best_match['Company Name']} ({best_match['Symbol']})")
        
        if len(contains_matches) > 1:
            st.info("Other possible matches:")
            for idx, row in contains_matches.iloc[1:5].iterrows():
                st.write(f"- {row['Company Name']} ({row['Symbol']})")
        
        return best_match["Symbol"], best_match["Company Name"]
    
    # If still no match, try each word in the company name
    words = company_name.lower().split()
    for word in words:
        if len(word) > 3:  # Only use words with more than 3 characters to avoid common words
            word_matches = company_df[company_df["Company Name"].str.lower().str.contains(word)]
            if not word_matches.empty:
                best_match = word_matches.iloc[0]
                st.warning(f"No exact match found. Using partial match based on '{word}': {best_match['Company Name']} ({best_match['Symbol']})")
                
                if len(word_matches) > 1:
                    st.info("Other possible matches:")
                    for idx, row in word_matches.iloc[1:5].iterrows():
                        st.write(f"- {row['Company Name']} ({row['Symbol']})")
                
                return best_match["Symbol"], best_match["Company Name"]
    
    # No match found
    return None, None

# Fetch financial data and calculate ratios
@st.cache_data
def calculate_all_ratios(ticker, period="5y"):
    try:
        # Fetch data
        company_financial_data = fetch_profit_data(ticker, period)
        company_market_data = fetch_market_data(ticker, period, "^GSPC")
        
        # Calculate ratios
        profitability = calculate_profitability_ratios(company_financial_data)
        liquidity = calculate_liquidity_ratios(company_financial_data)
        solvency = calculate_solvency_ratios(company_financial_data)
        efficiency = calculate_efficiency_ratios(company_financial_data)
        valuation = calculate_valuation_ratios(company_financial_data)
        market = calculate_market_performance_ratios(company_market_data, period)
        
        return {
            "profitability": profitability,
            "liquidity": liquidity,
            "solvency": solvency,
            "efficiency": efficiency,
            "valuation": valuation,
            "market": market
        }
    except Exception as e:
        st.error(f"Error calculating ratios: {e}")
        return None

# Create trend graphs for specified ratios
def create_trend_graph(ratio_df, ratio_name):
    if ratio_df is None or ratio_name not in ratio_df.columns or ratio_df[ratio_name].isnull().all():
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ratio_df[ratio_name].dropna().plot(ax=ax, marker='o', linewidth=2)
    plt.title(f"{ratio_name} Trend")
    plt.ylabel(ratio_name)
    plt.xlabel("Year")
    plt.grid(True)
    plt.tight_layout()
    
    return fig

# Main function to run the dashboard
def main():
    # Sidebar
    st.sidebar.title("Financial Ratio Analysis")
    st.sidebar.markdown("This dashboard analyzes financial ratios for companies listed in the database.")
    
    # Load company mapping
    company_df = load_company_ticker_map()
    
    # Company selection
    st.sidebar.header("Company Selection")
    
    # Option to directly select from list or enter a name
    selection_method = st.sidebar.radio("Select company by:", ["Company Name", "Search by Name"])
    
    ticker = None
    company_name = None
    
    if selection_method == "Company Name":
        # Sort company names for dropdown
        sorted_companies = sorted(company_df["Company Name"].tolist())
        selected_company = st.sidebar.selectbox("Select Company:", sorted_companies)
        company_name = selected_company
        ticker = company_df[company_df["Company Name"] == selected_company]["Symbol"].iloc[0]
    else:
        # Allow entering a company name
        search_term = st.sidebar.text_input("Search for Company:")
        if search_term:
            ticker, company_name = find_ticker(search_term, company_df)
    
    # Analysis period selection
    period = st.sidebar.selectbox("Select Analysis Period:", ["1y", "3y", "5y", "10y"], index=2)
    
    # Benchmark selection
    st.sidebar.header("Benchmark")
    use_benchmark = st.sidebar.checkbox("Compare with benchmark companies")
    
    benchmark_companies = []
    if use_benchmark and ticker:
        # Group companies by industry
        if "Industry" in company_df.columns:
            company_industry = company_df[company_df["Symbol"] == ticker]["Industry"].iloc[0]
            industry_companies = company_df[company_df["Industry"] == company_industry]["Company Name"].tolist()
            industry_companies = [c for c in industry_companies if c != company_name]
            
            if industry_companies:
                st.sidebar.markdown(f"**Industry**: {company_industry}")
                selected_benchmarks = st.sidebar.multiselect("Select benchmark companies:", 
                                                           industry_companies,
                                                           max_selections=3)
                for company in selected_benchmarks:
                    benchmark_ticker = company_df[company_df["Company Name"] == company]["Symbol"].iloc[0]
                    benchmark_companies.append((company, benchmark_ticker))
            else:
                st.sidebar.warning("No industry peers found.")
        else:
            st.sidebar.warning("Industry information not available in the dataset.")
    
    # Market index selection
    market_index = st.sidebar.selectbox("Select Market Index:", ["^GSPC (S&P 500)", "^NSEI (Nifty 50)", "^BSESN (Sensex)"])
    market_ticker = market_index.split()[0]
    
    # Main content
    st.title("Financial Ratio Analysis Dashboard")
    
    if ticker and st.sidebar.button("Analyze"):
        st.write(f"## Analysis for {company_name} ({ticker})")
        
        # Show progress
        progress_bar = st.progress(0)
        
        # Fetch data and calculate ratios
        with st.spinner("Calculating financial ratios..."):
            ratios = calculate_all_ratios(ticker, period)
            progress_bar.progress(50)
            
            # Calculate benchmark ratios if selected
            benchmark_ratios = {}
            if benchmark_companies:
                for name, bench_ticker in benchmark_companies:
                    try:
                        benchmark_ratios[name] = calculate_all_ratios(bench_ticker, period)
                    except Exception as e:
                        st.warning(f"Could not calculate ratios for {name}: {e}")
            
            progress_bar.progress(100)
        
        if ratios:
            # Display results by category
            st.header("Financial Ratio Analysis")
            
            # Create tabs for each category
            tab_profitability, tab_liquidity, tab_solvency, tab_efficiency, tab_valuation, tab_market = st.tabs([
                "Profitability", "Liquidity", "Solvency", "Efficiency", "Valuation", "Market"
            ])
            
            # Profitability Ratios
            with tab_profitability:
                st.subheader("Profitability Ratios")
                
                # Trend Graphs
                trend_ratios = [
                    "Net Profit Margin (%)", 
                    "Operating Profit Margin (%)", 
                    "Return on Equity (%)", 
                    "Return on Assets (%)",
                    "Return on Capital Employed (%)"
                ]
                
                # Create 2 columns for graphs
                col1, col2 = st.columns(2)
                
                for i, ratio in enumerate(trend_ratios):
                    if ratio in ratios["profitability"].columns:
                        with col1 if i % 2 == 0 else col2:
                            fig = create_trend_graph(ratios["profitability"], ratio)
                            if fig:
                                st.pyplot(fig)
                
                # Single Numbers
                st.subheader("Key Metrics")
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                if "EPS (₹ per share)" in ratios["profitability"].columns:
                    with metrics_col1:
                        eps_value = ratios["profitability"]["EPS (₹ per share)"].iloc[-1]
                        if not pd.isna(eps_value):
                            st.metric("Earnings Per Share (₹)", f"₹{eps_value:.2f}")
            
            # Liquidity Ratios
            with tab_liquidity:
                st.subheader("Liquidity Ratios")
                
                # Trend Graphs
                trend_ratios = ["Current Ratio", "Quick Ratio"]
                
                # Create 2 columns for graphs
                col1, col2 = st.columns(2)
                
                for i, ratio in enumerate(trend_ratios):
                    if ratio in ratios["liquidity"].columns:
                        with col1 if i % 2 == 0 else col2:
                            fig = create_trend_graph(ratios["liquidity"], ratio)
                            if fig:
                                st.pyplot(fig)
                
                # Single Numbers
                st.subheader("Key Metrics")
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                if "Cash Ratio" in ratios["liquidity"].columns:
                    with metrics_col1:
                        cash_ratio = ratios["liquidity"]["Cash Ratio"].iloc[-1]
                        if not pd.isna(cash_ratio):
                            st.metric("Cash Ratio", f"{cash_ratio:.2f}")
            
            # Solvency Ratios
            with tab_solvency:
                st.subheader("Solvency Ratios")
                
                # Trend Graphs
                trend_ratios = ["Debt-to-Equity Ratio", "Interest Coverage Ratio"]
                
                # Create 2 columns for graphs
                col1, col2 = st.columns(2)
                
                for i, ratio in enumerate(trend_ratios):
                    if ratio in ratios["solvency"].columns:
                        with col1 if i % 2 == 0 else col2:
                            fig = create_trend_graph(ratios["solvency"], ratio)
                            if fig:
                                st.pyplot(fig)
                
                # Single Numbers
                st.subheader("Key Metrics")
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                if "Debt-to-Asset Ratio" in ratios["solvency"].columns:
                    with metrics_col1:
                        debt_asset = ratios["solvency"]["Debt-to-Asset Ratio"].iloc[-1]
                        if not pd.isna(debt_asset):
                            st.metric("Debt-to-Asset Ratio", f"{debt_asset:.2f}")
            
            # Efficiency Ratios
            with tab_efficiency:
                st.subheader("Efficiency Ratios")
                
                # Trend Graphs
                trend_ratios = ["Asset Turnover Ratio", "Inventory Turnover Ratio", "Receivables Turnover Ratio"]
                
                # Create 2 columns for graphs
                col1, col2 = st.columns(2)
                
                for i, ratio in enumerate(trend_ratios):
                    if ratio in ratios["efficiency"].columns:
                        with col1 if i % 2 == 0 else col2:
                            fig = create_trend_graph(ratios["efficiency"], ratio)
                            if fig:
                                st.pyplot(fig)
                
                # Single Numbers
                st.subheader("Key Metrics")
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                if "Days Sales Outstanding" in ratios["efficiency"].columns:
                    with metrics_col1:
                        dso = ratios["efficiency"]["Days Sales Outstanding"].iloc[-1]
                        if not pd.isna(dso):
                            st.metric("Days Sales Outstanding", f"{dso:.2f}")
            
            # Valuation Ratios
            with tab_valuation:
                st.subheader("Valuation Ratios")
                
                # Trend Graphs
                trend_ratios = ["P/E Ratio", "P/B Ratio"]
                
                # Create 2 columns for graphs
                col1, col2 = st.columns(2)
                
                for i, ratio in enumerate(trend_ratios):
                    if ratio in ratios["valuation"].columns:
                        with col1 if i % 2 == 0 else col2:
                            fig = create_trend_graph(ratios["valuation"], ratio)
                            if fig:
                                st.pyplot(fig)
                
                # Single Numbers
                st.subheader("Key Metrics")
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                if "EV/EBITDA" in ratios["valuation"].columns:
                    with metrics_col1:
                        ev_ebitda = ratios["valuation"]["EV/EBITDA"].iloc[-1]
                        if not pd.isna(ev_ebitda):
                            st.metric("EV/EBITDA", f"{ev_ebitda:.2f}")
            
            # Market Performance Ratios
            with tab_market:
                st.subheader("Market Performance Ratios")
                
                # Trend Graphs
                trend_ratios = ["Dividend Yield (%)", "Beta"]
                
                # Create 2 columns for graphs
                col1, col2 = st.columns(2)
                
                for i, ratio in enumerate(trend_ratios):
                    if ratio in ratios["market"].columns:
                        with col1 if i % 2 == 0 else col2:
                            fig = create_trend_graph(ratios["market"], ratio)
                            if fig:
                                st.pyplot(fig)
                
                # Single Numbers
                st.subheader("Key Metrics")
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                if "Market Capitalization" in ratios["market"].columns:
                    market_cap = ratios["market"]["Market Capitalization"].iloc[-1]
                    if not pd.isna(market_cap):
                        if market_cap >= 1_000_000_000:
                            formatted_cap = f"${market_cap/1_000_000_000:.2f}B"
                        elif market_cap >= 1_000_000:
                            formatted_cap = f"${market_cap/1_000_000:.2f}M"
                        else:
                            formatted_cap = f"${market_cap:.2f}"
                        with metrics_col1:
                            st.metric("Market Capitalization", formatted_cap)
            
            # Download button for all ratios
            st.header("Download Data")
            
            # Combine all ratios into a single DataFrame
            all_ratios = pd.DataFrame()
            
            for category, ratio_df in ratios.items():
                if not ratio_df.empty:
                    # Add a prefix to the column names to identify the category
                    prefixed_df = ratio_df.copy()
                    prefixed_df.columns = [f"{category}_{col}" for col in prefixed_df.columns]
                    
                    # Merge with all_ratios
                    if all_ratios.empty:
                        all_ratios = prefixed_df
                    else:
                        # Use the index of all_ratios and join
                        all_ratios = all_ratios.join(prefixed_df, how='outer')
            
            # Convert to CSV for download
            csv = all_ratios.to_csv().encode('utf-8')
            
            st.download_button(
                label="Download Ratio Data as CSV",
                data=csv,
                file_name=f"{company_name}_financial_ratios.csv",
                mime="text/csv",
            )
            
    else:
        # Show instructions when no company is selected
        st.info("To get started, select a company from the sidebar and click 'Analyze'.")
        
        # Show description
        st.markdown("""
        ## Financial Ratio Analysis
        
        This dashboard analyzes various financial ratios for companies listed in the database. 
        
        The analysis includes the following categories of ratios:
        
        ### 1. Profitability Ratios
        - Net Profit Margin (%)
        - Operating Profit Margin (%)
        - Return on Equity (ROE) (%)
        - Return on Assets (ROA) (%)
        - Return on Capital Employed (ROCE) (%)
        - Earnings Per Share (EPS)
        
        ### 2. Liquidity Ratios
        - Current Ratio
        - Quick Ratio
        - Cash Ratio
        
        ### 3. Solvency Ratios
        - Debt-to-Equity Ratio
        - Interest Coverage Ratio
        - Debt-to-Asset Ratio
        
        ### 4. Efficiency Ratios
        - Asset Turnover Ratio
        - Inventory Turnover Ratio
        - Receivables Turnover Ratio
        - Days Sales Outstanding (DSO)
        
        ### 5. Valuation Ratios
        - Price-to-Earnings (P/E) Ratio
        - Price-to-Book (P/B) Ratio
        - Enterprise Value to EBITDA (EV/EBITDA)
        
        ### 6. Market Performance Ratios
        - Dividend Yield (%)
        - Beta (Stock Volatility)
        - Market Capitalization
        """)

if __name__ == "__main__":
    main()