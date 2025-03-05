import yfinance as yf
import json

# Define the ticker symbol for Zomato
ticker = "ZOMATO.NS"

# Fetch company data
stock = yf.Ticker(ticker)

# Get the balance sheet
balance_sheet = stock.balance_sheet

# Convert index (dates) and column names to strings for JSON compatibility
balance_sheet.index = balance_sheet.index.astype(str)
balance_sheet.columns = balance_sheet.columns.astype(str)

# Replace NaN values with None to avoid JSON serialization issues
balance_sheet = balance_sheet.where(balance_sheet.notna(), None)

# Convert to dictionary
balance_sheet_dict = balance_sheet.to_dict()

# Save as JSON
with open("zomato_balance_sheet.json", "w", encoding="utf-8") as file:
    json.dump(balance_sheet_dict, file, indent=4)

print("Balance sheet saved as JSON: zomato_balance_sheet.json")
