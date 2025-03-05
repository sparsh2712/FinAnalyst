import yfinance as yf
import pandas as pd
import json

def fetch_yearly_earnings(ticker):
    """
    Fetches the yearly earnings (income statement) of a company from Yahoo Finance.
    Stores it in a JSON file where each year is a key and NaN values are replaced with null.
    """
    stock = yf.Ticker(ticker)
    
    # Fetch Income Statement (Yearly Earnings)
    earnings = stock.financials

    if earnings is None or earnings.empty:
        print("No earnings data available for", ticker)
        return

    # Transpose for better readability
    earnings = earnings.T

    # Convert index (dates) to string format for JSON compatibility
    earnings.index = earnings.index.strftime("%Y")

    # Convert NaN values to None (null in JSON)
    earnings = earnings.where(pd.notna(earnings), None)

    # Convert to dictionary where each year is a key
    earnings_dict = earnings.to_dict(orient="index")

    # Save to JSON file
    filename = f"{ticker}_earnings.json"
    with open(filename, "w") as f:
        json.dump(earnings_dict, f, indent=4)

    print(f"Yearly earnings saved to {filename}")

# Fetch and store Zomato's yearly earnings
fetch_yearly_earnings("ZOMATO.NS")
