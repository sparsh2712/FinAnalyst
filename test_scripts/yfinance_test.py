import yfinance as yf
import json

# Fetch data for Zomato
stock = yf.Ticker("ZOMATO.NS")

# Get the income statement
income_statement = stock.income_stmt

# Convert index and columns to strings
income_statement.index = income_statement.index.astype(str)
income_statement.columns = income_statement.columns.astype(str)

# Replace NaN values with None for proper JSON formatting
income_statement = income_statement.where(income_statement.notna(), None)

# Convert to dictionary
income_statement_dict = income_statement.to_dict()

# Save as JSON
with open("zomato_income_statement.json", "w", encoding="utf-8") as file:
    json.dump(income_statement_dict, file, indent=4)

print("Income statement saved as JSON: zomato_income_statement.json")
