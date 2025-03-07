import yfinance as yf
import pandas as pd
from financial_data_utils import get_balance_sheet, get_yearly_stock_price, get_stock_info, get_dividends

class MarketPerformanceRatios:
    """Calculates market performance ratios for a given stock ticker based on financial data."""
    
    def __init__(self, ticker, duration, data):
        self.ticker = ticker
        self.duration = duration
        self.stock_price = data.get("stock_price", get_yearly_stock_price(ticker, duration))
        self.balance_sheet = data.get("balance_sheet", {})
        self.stock_info = data.get("stock_info", get_stock_info(ticker))
        self.dividends = get_dividends(ticker)
        if not self.dividends.empty:
            self.dividends['Date'] = pd.to_datetime(self.dividends['Date'])
    
    def dividend_yield(self):
        """Calculates Dividend Yield = (Dividend Per Share / Stock Price) * 100."""
        ratios = {}
        for year in self.stock_price:
            yearly_dividends = self.dividends[self.dividends['Date'].dt.year == int(year)]['Dividends'].sum()
            stock_price = self.stock_price.get(year, None)
            
            if stock_price and stock_price > 0:
                ratios[year] = (yearly_dividends / stock_price) * 100
        
        return ratios
    
    def beta(self):
        """Returns Beta (Stock Volatility)."""
        return self.stock_info.get("beta")
    
    def market_capitalization(self):
        """Calculates Market Capitalization = Stock Price * Total Shares Outstanding."""
        ratios = {}
        for year in self.balance_sheet:
            stock_price = self.stock_price.get(year)
            total_shares = self.balance_sheet.get(year, {}).get("Ordinary Shares Number")
            print(f"Year: {year} stock_price: {stock_price} total_shares: {total_shares}")

            if stock_price and total_shares:
                ratios[year] = stock_price * total_shares
        
        return ratios

if __name__ == "__main__":
    ticker = "RELIANCE.NS"
    duration = 5
    data = {
        "balance_sheet": get_balance_sheet(ticker, duration),
        "stock_price": get_yearly_stock_price(ticker, duration),
        "stock_info": get_stock_info(ticker)
    }
    
    print(data["stock_price"])
    market_ratios = MarketPerformanceRatios(ticker, duration, data)
    # print(market_ratios.dividend_yield())
    # print("Beta (Stock Volatility):", market_ratios.beta())
    print(market_ratios.market_capitalization())