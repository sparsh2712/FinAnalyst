import matplotlib.pyplot as plt
from financial_data_utils import plot_ratio, get_balance_sheet, get_income_statement, get_yearly_stock_price

class ValuationRatios:
    """Calculates valuation ratios for a given stock ticker based on financial data."""

    def __init__(self, ticker, duration, data):
        self.ticker = ticker
        self.duration = duration
        self.data = data
        self.income_statement = data.get("income_statement", {})
        self.balance_sheet = data.get("balance_sheet", {})
        self.stock_prices = data.get("stock_prices", {})  # Stock prices now part of data

    def pe_ratio(self):
        """Calculates and plots Price-to-Earnings (P/E) Ratio = Stock Price / Earnings Per Share."""
        ratios = {}
        for year in self.income_statement:
            stock_price = self.stock_prices.get(int(year))
            eps = self.income_statement.get(year, {}).get("Diluted EPS")  # Correct key
            
            if stock_price is not None and eps is not None:
                ratios[year] = stock_price / eps
        
        return ratios
        # plot_ratio(ratios, "Price-to-Earnings (P/E) Ratio", "Times")

    def pb_ratio(self):
        """Calculates and plots Price-to-Book (P/B) Ratio = Stock Price / Book Value Per Share."""
        ratios = {}
        for year in self.balance_sheet:
            stock_price = self.stock_prices.get(int(year))
            total_equity = self.balance_sheet.get(year, {}).get("Stockholders Equity")  # Correct key
            shares_outstanding = self.balance_sheet.get(year, {}).get("Ordinary Shares Number")  # Correct key

            if stock_price is not None and total_equity is not None and shares_outstanding is not None and shares_outstanding > 0:
                book_value_per_share = total_equity / shares_outstanding
                ratios[year] = stock_price / book_value_per_share
        
        return ratios
        # plot_ratio(ratios, "Price-to-Book (P/B) Ratio", "Times")

    def ev_ebitda_ratio(self):
        """Calculates and plots EV/EBITDA Ratio = (Market Cap + Debt - Cash) / EBITDA."""
        ratios = {}
        for year in self.income_statement:
            stock_price = self.stock_prices.get(int(year))
            shares_outstanding = self.balance_sheet.get(year, {}).get("Ordinary Shares Number")  # Correct key
            total_debt = self.balance_sheet.get(year, {}).get("Total Debt")  # Correct key
            cash = self.balance_sheet.get(year, {}).get("Cash And Cash Equivalents")  # Correct key
            ebitda = self.income_statement.get(year, {}).get("EBITDA")  # Correct key

            if all(v is not None for v in [stock_price, shares_outstanding, total_debt, cash, ebitda]):
                market_cap = stock_price * shares_outstanding
                enterprise_value = market_cap + total_debt - cash
                ratios[year] = enterprise_value / ebitda
        
        return ratios
        # plot_ratio(ratios, "Enterprise Value to EBITDA (EV/EBITDA) Ratio", "Times")

if __name__ == "__main__":
    ticker = "ZOMATO.NS"
    duration = 5
    data = {
        "income_statement": get_income_statement(ticker, duration),
        "balance_sheet": get_balance_sheet(ticker, duration),
        "stock_prices": get_yearly_stock_price(ticker, duration)  # Stock prices included in data
    }

    ratios = ValuationRatios(ticker, duration, data)
    ratios.pe_ratio()
    ratios.pb_ratio()
    ratios.ev_ebitda_ratio()
