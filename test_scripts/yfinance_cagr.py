import yfinance as yf

def get_market_cap(ticker):
    """
    Fetch historical market capitalization data for the given ticker.
    If it's a stock, calculate Market Cap = Close Price * Outstanding Shares.
    If it's an index, return Close Price as a proxy for growth.
    """
    stock = yf.Ticker(ticker)
    history = stock.history(period="10y")  # Get last 10 years of data
    
    if "NSEI" in ticker or "NSEBANK" in ticker:  # If it's an index, return Close Price
        history['Value'] = history['Close']
        return history[['Close', 'Value']]
    
    outstanding_shares = stock.info.get('sharesOutstanding', None)
    if not outstanding_shares:
        raise ValueError(f"Outstanding shares data not available for {ticker}")

    # Calculate Market Cap
    history['Market Cap'] = history['Close'] * outstanding_shares
    return history[['Close', 'Market Cap']]

def calculate_cagr(initial_value, final_value, years=10):
    """
    Calculate CAGR (Compound Annual Growth Rate).
    Formula: CAGR = ((Vf / Vi) ** (1/years)) - 1
    """
    return ((final_value / initial_value) ** (1 / years)) - 1

# Define tickers
hdfc_ticker = "HDFCBANK.NS"   # HDFC Bank (NSE)
nifty_ticker = "^NSEI"        # NIFTY 50 (Market Index)
bank_nifty_ticker = "^NSEBANK" # NIFTY Bank (Banking Sector)

# Fetch Data
hdfc_market_cap = get_market_cap(hdfc_ticker)
nifty_index = get_market_cap(nifty_ticker)
bank_nifty_index = get_market_cap(bank_nifty_ticker)

# Get initial and final values for CAGR calculation
initial_hdfc_mc = hdfc_market_cap.iloc[0]['Market Cap']
final_hdfc_mc = hdfc_market_cap.iloc[-1]['Market Cap']
hdfc_cagr = calculate_cagr(initial_hdfc_mc, final_hdfc_mc)

initial_nifty_value = nifty_index.iloc[0]['Value']
final_nifty_value = nifty_index.iloc[-1]['Value']
nifty_cagr = calculate_cagr(initial_nifty_value, final_nifty_value)

initial_bank_nifty_value = bank_nifty_index.iloc[0]['Value']
final_bank_nifty_value = bank_nifty_index.iloc[-1]['Value']
bank_nifty_cagr = calculate_cagr(initial_bank_nifty_value, final_bank_nifty_value)

# Print Results
print(f"HDFC Bank Market Cap (10 years ago): ₹{initial_hdfc_mc:,.2f} Cr")
print(f"HDFC Bank Market Cap (Now): ₹{final_hdfc_mc:,.2f} Cr")
print(f"HDFC Bank 10-year CAGR: {hdfc_cagr * 100:.2f}%\n")

print(f"NIFTY 50 10-year CAGR: {nifty_cagr * 100:.2f}%")
print(f"NIFTY Bank 10-year CAGR: {bank_nifty_cagr * 100:.2f}%")
