import yfinance as yf
import json
import pandas as pd
import matplotlib.pyplot as plt
from financial_data_utils import plot_ratio, get_balance_sheet, get_income_statement, get_yearly_stock_price

class MarketPerformanceRatios:
    """Calculates market performance ratios for a given stock ticker based on financial data."""
    
    def __init__(self, ticker, duration, data):
        self.ticker = ticker
        self.duration = duration
        self.data = data
        self.stock_price = data.get("stock_price", get_yearly_stock_price(ticker, duration))
        self.balance_sheet = data.get("balance_sheet", {})
        self.income_statement = data.get("income_statement", {})
        print("hi")
    
    def dividend_yield(self):
        """Calculates and plots Dividend Yield = (Dividend Per Share / Stock Price) * 100."""
        ratios = {}
        for year in self.income_statement:
            dividend_per_share = self.income_statement.get(year, {}).get("Dividends Per Share", None)
            stock_price = self.stock_price.get(year, None)
            
            if dividend_per_share is not None and stock_price is not None and stock_price > 0:
                ratios[year] = (dividend_per_share / stock_price) * 100
        
        return ratios
        # plot_ratio(ratios, "Dividend Yield (%)", "%")
    
    def beta(self):
        """Retrieves and plots Beta (Stock Volatility)."""
        ratios = {}
        for year in self.stock_price:
            beta_value = self.stock_price.get(year, {}).get("Beta", None)
            if beta_value is not None:
                ratios[year] = beta_value
        
        return ratios
        # plot_ratio(ratios, "Beta (Stock Volatility)", "")
    
    def market_capitalization(self):
        """Calculates and plots Market Capitalization = Stock Price * Total Shares Outstanding."""
        ratios = {}
        for year in self.balance_sheet:
            stock_price = self.stock_price.get(year, None)
            total_shares = self.balance_sheet.get(year, {}).get("Ordinary Shares Number", None)
            
            if stock_price is not None and total_shares is not None:
                ratios[year] = stock_price * total_shares
        
        return ratios
        # plot_ratio(ratios, "Market Capitalization", "USD")

if __name__ == "__main__":
    ticker = "RELIANCE.NS"
    duration = 5
    data = {
        "income_statement": get_income_statement(ticker, duration),
        "balance_sheet": get_balance_sheet(ticker, duration),
        "stock_price": get_yearly_stock_price(ticker, duration)
    }
        
    market_ratios = MarketPerformanceRatios(ticker, duration, data)
    market_ratios.dividend_yield()
    market_ratios.beta()
    market_ratios.market_capitalization()
