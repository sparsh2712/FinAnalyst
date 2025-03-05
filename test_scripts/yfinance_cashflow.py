import yfinance as yf
import pandas as pd
import json
import numpy as np

def fetch_cashflow_statement(ticker):
    """
    Fetches the cash flow statement of a company from Yahoo Finance.
    Stores it in a JSON file where each year is a key and NaN values are replaced with null.
    """
    stock = yf.Ticker(ticker)
    
    # Fetch Cash Flow Statement
    cashflow = stock.cashflow

    if cashflow is None or cashflow.empty:
        print("No cash flow data available for", ticker)
        return

    # Transpose for better readability
    cashflow = cashflow.T

    # Convert index (dates) to string format for JSON compatibility
    cashflow.index = cashflow.index.strftime("%Y")

    # Convert NaN values to None (null in JSON)
    cashflow = cashflow.where(pd.notna(cashflow), None)

    # Convert to dictionary where each year is a key
    cashflow_dict = cashflow.to_dict(orient="index")

    # Save to JSON file
    filename = f"{ticker}_cashflow.json"
    with open(filename, "w") as f:
        json.dump(cashflow_dict, f, indent=4)

    print(f"Cash flow statement saved to {filename}")

# Fetch and store Zomato's cash flow statement
fetch_cashflow_statement("ZOMATO.NS")
