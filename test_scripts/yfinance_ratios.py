import yfinance as yf

# Example: Fetch financial data for Reliance Industries (RELIANCE.NS)
ticker = yf.Ticker("ASIANPAINT.NS")

# Fetch different financial ratios
debt_to_equity = ticker.info.get('debtToEquity')
gross_margin = ticker.info.get('grossMargins')
operating_margin = ticker.info.get('operatingMargins')
net_margin = ticker.info.get('profitMargins')
market_cap = ticker.info.get('marketCap')

print(f"Debt to Equity: {debt_to_equity}")
print(f"Gross Margin: {gross_margin}")
print(f"Operating Margin: {operating_margin}")
print(f"Net Margin: {net_margin}")
print(f"Market Cap: {market_cap}")
