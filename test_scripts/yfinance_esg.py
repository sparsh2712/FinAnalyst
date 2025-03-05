import yfinance as yf

# Define ticker
ticker = "ZOMATO.NS"  # Example: Zomato

# Fetch sustainability data
stock = yf.Ticker(ticker)
sustainability = stock.sustainability

# Print sustainability scores
print(sustainability)
