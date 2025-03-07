import yfinance as yf
import json
import pandas as pd
import matplotlib.pyplot as plt

def plot_ratio(ratio_dict, title, ylabel):
    """Plots a line graph for a given financial ratio dictionary."""
    if not ratio_dict:
        print(f"No data available for {title}")
        return
    
    years = list(ratio_dict.keys())
    values = list(ratio_dict.values())
    
    plt.figure(figsize=(8, 5))
    plt.plot(years, values, marker='o', linestyle='-')
    plt.xlabel("Year")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid()
    plt.show()

def get_balance_sheet(ticker, duration):
    """Fetches the balance sheet of a given company for the specified duration in years and returns it as a dictionary with years as keys."""
    stock = yf.Ticker(ticker)
    statement = stock.balance_sheet
    
    if statement is None or statement.empty:
        return {}
    
    statement = statement.iloc[:, :duration]
    statement.columns = pd.to_datetime(statement.columns).year.astype(str)
    statement_dict = {col: statement[col].where(statement[col].notna(), None).to_dict() for col in statement.columns}
    return statement_dict

def get_cashflow_statement(ticker, duration):
    """Fetches the cash flow statement of a given company for the specified duration in years and returns it as a dictionary with years as keys."""
    stock = yf.Ticker(ticker)
    statement = stock.cashflow
    
    if statement is None or statement.empty:
        return {}
    
    statement = statement.iloc[:, :duration]
    statement.columns = pd.to_datetime(statement.columns).year.astype(str)
    statement_dict = {col: statement[col].where(statement[col].notna(), None).to_dict() for col in statement.columns}
    return statement_dict

def get_yearly_earnings(ticker, duration):
    """Fetches the yearly earnings statement of a given company for the specified duration in years and returns it as a dictionary with years as keys."""
    stock = yf.Ticker(ticker)
    statement = stock.financials
    
    if statement is None or statement.empty:
        return {}
    
    statement = statement.iloc[:, :duration]
    statement.columns = pd.to_datetime(statement.columns).year.astype(str)
    statement_dict = {col: statement[col].where(statement[col].notna(), None).to_dict() for col in statement.columns}
    return statement_dict

def get_income_statement(ticker, duration):
    """Fetches the income statement of a given company for the specified duration in years and returns it as a dictionary with years as keys."""
    stock = yf.Ticker(ticker)
    statement = stock.income_stmt
    
    if statement is None or statement.empty:
        return {}
    
    statement = statement.iloc[:, :duration]
    statement.columns = pd.to_datetime(statement.columns).year.astype(str)
    statement_dict = {col: statement[col].where(statement[col].notna(), None).to_dict() for col in statement.columns}
    return statement_dict

def get_yearly_stock_price(ticker, duration):
    """Fetches historical year-end closing prices for the given ticker over the specified duration."""
    stock = yf.Ticker(ticker)
    history = stock.history(period=f"{duration}y", interval="1mo")  # Fetch monthly data over the duration
    
    prices = {}
    for date, row in history.iterrows():
        year = date.year
        if year not in prices:  # Take the last available price for each year
            prices[year] = row["Close"]
    
    return prices

def get_stock_info(ticker):
    """Fetches general stock information including market cap, sector, industry, beta, and dividend yield."""
    stock = yf.Ticker(ticker)
    return stock.info if stock.info else {}

def get_historical_data(ticker, duration=None, start_date=None, end_date=None, freq="1mo"):
    """Fetches historical market data based on either duration or start and end dates."""
    stock = yf.Ticker(ticker)
    if duration:
        data = stock.history(period=duration, interval=freq)
    elif start_date and end_date:
        data = stock.history(start=start_date, end=end_date, interval=freq)
    else:
        raise ValueError("Either duration or start and end dates must be provided.")
    return data.reset_index()

def get_dividends(ticker):
    """Fetches historical dividend payments."""
    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    return dividends.reset_index() if not dividends.empty else pd.DataFrame()

def get_major_holders(ticker):
    """Fetches major shareholders and institutional holders."""
    stock = yf.Ticker(ticker)
    holders = {
        "major_holders": stock.major_holders.to_dict() if stock.major_holders is not None else {},
        "institutional_holders": stock.institutional_holders.to_dict() if stock.institutional_holders is not None else {}
    }
    return holders

def get_sustainability(ticker):
    """Fetches ESG (Environmental, Social, Governance) scores for the company."""
    stock = yf.Ticker(ticker)
    return stock.sustainability.to_dict() if stock.sustainability is not None else {}

if __name__ == "__main__":
    ticker = "RELIANCE.NS"
    duration = 5
    
    balance_sheet_data = get_balance_sheet(ticker, duration)
    with open("balance_sheet.json", "w", encoding="utf-8") as file:
        json.dump(balance_sheet_data, file, indent=4)
    print("Balance sheet saved as JSON: balance_sheet.json")
    
    cashflow_data = get_cashflow_statement(ticker, duration)
    with open("cashflow.json", "w", encoding="utf-8") as file:
        json.dump(cashflow_data, file, indent=4)
    print("Cash flow statement saved as JSON: cashflow.json")
    
    earnings_data = get_yearly_earnings(ticker, duration)
    with open("earnings.json", "w", encoding="utf-8") as file:
        json.dump(earnings_data, file, indent=4)
    print("Yearly earnings statement saved as JSON: earnings.json")
    
    income_statement_data = get_income_statement(ticker, duration)
    with open("income_statement.json", "w", encoding="utf-8") as file:
        json.dump(income_statement_data, file, indent=4)
    print("Income statement saved as JSON: income_statement.json")
    
    stock_info = get_stock_info(ticker)
    with open("stock_info.json", "w", encoding="utf-8") as file:
        json.dump(stock_info, file, indent=4)
    print("Stock info saved as JSON: stock_info.json")
    
    historical_data = get_historical_data(ticker, duration="1y")
    historical_data.to_csv("historical_data.csv", index=False)
    print("Historical data saved as CSV: historical_data.csv")
    
    dividends = get_dividends(ticker)
    dividends.to_csv("dividends.csv", index=False)
    print("Dividends saved as CSV: dividends.csv")
    
    holders = get_major_holders(ticker)
    with open("holders.json", "w", encoding="utf-8") as file:
        json.dump(holders, file, indent=4)
    print("Major holders saved as JSON: holders.json")
    
    sustainability = get_sustainability(ticker)
    with open("sustainability.json", "w", encoding="utf-8") as file:
        json.dump(sustainability, file, indent=4)
    print("Sustainability data saved as JSON: sustainability.json")