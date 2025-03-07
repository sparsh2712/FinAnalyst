import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import os
import io

# Import all ratio calculation modules
from profitability_ratio import ProfitabilityRatios
from liquidity_ratio import LiquidityRatios
from solvency_ratio import SolvencyRatios
from efficiency_ratio import EfficiencyRatios
from market_performance_ratio import MarketPerformanceRatios
from valuation_ratio import ValuationRatios
from financial_data_utils import get_balance_sheet, get_income_statement, get_yearly_stock_price, get_stock_info

# Set page configuration
st.set_page_config(
    page_title="Financial Ratio Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("Financial Ratio Analysis Dashboard")
st.markdown("""
This dashboard calculates and visualizes key financial ratios for selected companies.
Select a company from the dropdown menu and click 'Analyze' to view its financial performance metrics.
""")

# Load company ticker mapping
@st.cache_data
def load_company_data():
    try:
        return pd.read_csv("/Users/sparsh/Desktop/FinAnalyst/comapny_ticker_map.csv")
    except FileNotFoundError:
        # Create sample data if file doesn't exist
        st.warning("company_ticker_map.csv not found. Using sample data.")
        sample_data = {
            'Company Name': ['Reliance Industries', 'Tata Consultancy Services', 'HDFC Bank', 'Infosys', 'Zomato'],
            'Symbol': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ZOMATO']
        }
        return pd.DataFrame(sample_data)

company_data = load_company_data()

# Create a function to fetch all required financial data
@st.cache_data
def fetch_financial_data(ticker, duration=5):
    with st.spinner(f"Fetching financial data for {ticker}..."):
        try:
            # Get all required data in one go
            data = {
                "income_statement": get_income_statement(ticker, duration),
                "balance_sheet": get_balance_sheet(ticker, duration),
                "stock_price": get_yearly_stock_price(ticker, duration),
                "stock_info": get_stock_info(ticker)
            }
            return data
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return None

# Function to plot ratio as a line chart
def plot_ratio_chart(ratio_dict, title, ylabel, use_percent=False):
    if not ratio_dict:
        st.info(f"No data available for {title}")
        return
    
    fig, ax = plt.subplots(figsize=(10, 5))
    years = list(ratio_dict.keys())
    values = list(ratio_dict.values())
    
    ax.plot(years, values, marker='o', linestyle='-', linewidth=2)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Format y-axis as percentage if needed
    if use_percent:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2f}%'))
    
    plt.tight_layout()
    st.pyplot(fig)

# Function to visualize a category of ratios
def visualize_ratio_category(title, ratios_dict, use_percent=False):
    st.subheader(title)
    
    for ratio_name, (ratio_values, ylabel) in ratios_dict.items():
        if ratio_values:
            with st.expander(f"{ratio_name}", expanded=True):
                plot_ratio_chart(ratio_values, ratio_name, ylabel, use_percent)
        else:
            st.info(f"No data available for {ratio_name}")

# Create a navbar with company dropdown and analyze button
st.sidebar.header("Analysis Controls")

# Company dropdown
company_names = company_data['Company Name'].tolist()
selected_company = st.sidebar.selectbox("Select a company:", company_names)

# Get ticker for selected company
selected_ticker = company_data.loc[company_data['Company Name'] == selected_company, 'Symbol'].iloc[0]
ticker_with_suffix = f"{selected_ticker}.NS"  # Add .NS suffix as required

# Add duration selection
duration = st.sidebar.slider("Select duration (years):", min_value=1, max_value=10, value=5)

# Add analyze button
analyze_button = st.sidebar.button("Analyze", type="primary", use_container_width=True)

# Only perform analysis when button is clicked
if analyze_button:
    # Show company info
    st.sidebar.subheader(f"Selected Company: {selected_company}")
    st.sidebar.write(f"Ticker: {ticker_with_suffix}")
    
    # Fetch data
    financial_data = fetch_financial_data(ticker_with_suffix, duration)
    
    if financial_data:
        # Initialize ratio calculators
        profitability = ProfitabilityRatios(ticker_with_suffix, duration, financial_data)
        liquidity = LiquidityRatios(ticker_with_suffix, duration, financial_data)
        solvency = SolvencyRatios(ticker_with_suffix, duration, financial_data)
        efficiency = EfficiencyRatios(ticker_with_suffix, duration, financial_data)
        market_performance = MarketPerformanceRatios(ticker_with_suffix, duration, financial_data)
        valuation = ValuationRatios(ticker_with_suffix, duration, {
            "income_statement": financial_data["income_statement"],
            "balance_sheet": financial_data["balance_sheet"],
            "stock_prices": financial_data["stock_price"]  # Match the expected key in the ValuationRatios class
        })
        
        # Create tabs for different ratio categories
        tabs = st.tabs(["Profitability", "Liquidity", "Solvency", "Efficiency", "Valuation", "Market Performance"])
        
        # Profitability Ratios Tab
        with tabs[0]:
            profitability_ratios = {
                "Net Profit Margin (%)": (profitability.net_profit_margin(), "Percentage"),
                "Operating Profit Margin (%)": (profitability.operating_profit_margin(), "Percentage"),
                "Return on Equity (ROE) (%)": (profitability.return_on_equity(), "Percentage"),
                "Return on Assets (ROA) (%)": (profitability.return_on_assets(), "Percentage"),
                "Return on Capital Employed (ROCE) (%)": (profitability.return_on_capital_employed(), "Percentage"),
                "Earnings Per Share (EPS)": (profitability.earnings_per_share(), "₹ per share")
            }
            visualize_ratio_category("Profitability Ratios", profitability_ratios, use_percent=True)
        
        # Liquidity Ratios Tab
        with tabs[1]:
            liquidity_ratios = {
                "Current Ratio": (liquidity.current_ratio(), "Ratio"),
                "Quick Ratio": (liquidity.quick_ratio(), "Ratio"),
                "Cash Ratio": (liquidity.cash_ratio(), "Ratio")
            }
            visualize_ratio_category("Liquidity Ratios", liquidity_ratios)
        
        # Solvency Ratios Tab
        with tabs[2]:
            solvency_ratios = {
                "Debt-to-Equity (D/E) Ratio": (solvency.debt_to_equity_ratio(), "Ratio"),
                "Interest Coverage Ratio": (solvency.interest_coverage_ratio(), "Ratio"),
                "Debt-to-Asset Ratio": (solvency.debt_to_asset_ratio(), "Ratio")
            }
            visualize_ratio_category("Solvency Ratios", solvency_ratios)
        
        # Efficiency Ratios Tab
        with tabs[3]:
            efficiency_ratios = {
                "Asset Turnover Ratio": (efficiency.asset_turnover_ratio(), "Times"),
                "Inventory Turnover Ratio": (efficiency.inventory_turnover_ratio(), "Times"),
                "Receivables Turnover Ratio": (efficiency.receivables_turnover_ratio(), "Times")
            }
            visualize_ratio_category("Efficiency Ratios", efficiency_ratios)
        
        # Valuation Ratios Tab
        with tabs[4]:
            valuation_ratios = {
                "Price-to-Earnings (P/E) Ratio": (valuation.pe_ratio(), "Times"),
                "Price-to-Book (P/B) Ratio": (valuation.pb_ratio(), "Times"),
                "Enterprise Value to EBITDA (EV/EBITDA)": (valuation.ev_ebitda_ratio(), "Times")
            }
            visualize_ratio_category("Valuation Ratios", valuation_ratios)
        
        # Market Performance Ratios Tab
        with tabs[5]:
            market_ratios = {
                "Dividend Yield (%)": (market_performance.dividend_yield(), "Percentage"),
                "Market Capitalization": (market_performance.market_capitalization(), "₹")
            }
            visualize_ratio_category("Market Performance Ratios", market_ratios)
            
            # Beta as single value
            beta = market_performance.beta()
            if beta:
                st.metric("Beta (Stock Volatility)", f"{beta:.2f}")
        
        # Prepare data for download
        st.sidebar.subheader("Download Data")
        
        @st.cache_data
        def prepare_download_data():
            # Combine all ratios into a single DataFrame
            all_ratios = {}
            
            # Add each ratio category
            for ratio_name, (ratio_values, _) in profitability_ratios.items():
                if ratio_values:
                    all_ratios[ratio_name] = ratio_values
            
            for ratio_name, (ratio_values, _) in liquidity_ratios.items():
                if ratio_values:
                    all_ratios[ratio_name] = ratio_values
            
            for ratio_name, (ratio_values, _) in solvency_ratios.items():
                if ratio_values:
                    all_ratios[ratio_name] = ratio_values
            
            for ratio_name, (ratio_values, _) in efficiency_ratios.items():
                if ratio_values:
                    all_ratios[ratio_name] = ratio_values
            
            for ratio_name, (ratio_values, _) in valuation_ratios.items():
                if ratio_values:
                    all_ratios[ratio_name] = ratio_values
            
            for ratio_name, (ratio_values, _) in market_ratios.items():
                if ratio_values:
                    all_ratios[ratio_name] = ratio_values
            
            # Convert to DataFrame
            df = pd.DataFrame(all_ratios)
            return df
        
        ratios_df = prepare_download_data()
        
        # Create a download button
        csv = ratios_df.to_csv(index=True)
        st.sidebar.download_button(
            label="Download Ratios as CSV",
            data=csv,
            file_name=f"{selected_company}_financial_ratios.csv",
            mime="text/csv"
        )
    else:
        st.error("Failed to fetch financial data. Please try another company.")
else:
    # Display a message when the app is first loaded or when no analysis is being performed
    st.info("👈 Select a company from the sidebar and click 'Analyze' to view financial ratio analysis.")