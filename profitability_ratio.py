import yfinance as yf
import json
import pandas as pd
import matplotlib.pyplot as plt
from financial_data_utils import get_income_statement, get_balance_sheet, plot_ratio
class ProfitabilityRatios:
    """Calculates profitability ratios for a given stock ticker based on financial data."""
    
    def __init__(self, ticker, duration, data):
        self.ticker = ticker
        self.duration = duration
        self.data = data
        self.income_statement = data.get("income_statement", {})
        self.balance_sheet = data.get("balance_sheet", {})
    
    def net_profit_margin(self):
        """Calculates and plots Net Profit Margin (%) = (Net Profit / Revenue) * 100."""
        if not self.income_statement:
            return
        
        net_profit_margin = {}
        for year, data in self.income_statement.items():
            net_profit = data.get("Net Income", None)
            revenue = data.get("Total Revenue", None)
            
            if net_profit is not None and revenue:
                net_profit_margin[year] = (net_profit / revenue) * 100
        
        return ratios
        # plot_ratio(net_profit_margin, "Net Profit Margin (%)", "Percentage")
    
    def operating_profit_margin(self):
        """Calculates and plots Operating Profit Margin (%) = (Operating Profit / Revenue) * 100."""
        if not self.income_statement:
            return
        
        operating_profit_margin = {}
        for year, data in self.income_statement.items():
            operating_profit = data.get("Operating Income", None)
            revenue = data.get("Total Revenue", None)
            
            if operating_profit is not None and revenue:
                operating_profit_margin[year] = (operating_profit / revenue) * 100
        
        return ratios
        # plot_ratio(operating_profit_margin, "Operating Profit Margin (%)", "Percentage")
    
    def return_on_equity(self):
        """Calculates and plots Return on Equity (ROE) (%) = (Net Profit / Shareholders' Equity) * 100."""
        if not self.income_statement or not self.balance_sheet:
            return
        
        roe = {}
        for year in self.income_statement:
            net_profit = self.income_statement.get(year, {}).get("Net Income", None)
            equity = self.balance_sheet.get(year, {}).get("Stockholders Equity", None)
            
            if net_profit is not None and equity:
                roe[year] = (net_profit / equity) * 100
        
        return ratios
        # plot_ratio(roe, "Return on Equity (ROE) (%)", "Percentage")
    
    def return_on_assets(self):
        """Calculates and plots Return on Assets (ROA) (%) = (Net Profit / Total Assets) * 100."""
        if not self.income_statement or not self.balance_sheet:
            return
        
        roa = {}
        for year in self.income_statement:
            net_profit = self.income_statement.get(year, {}).get("Net Income", None)
            total_assets = self.balance_sheet.get(year, {}).get("Total Assets", None)
            
            if net_profit is not None and total_assets:
                roa[year] = (net_profit / total_assets) * 100
        
        return ratios
        # plot_ratio(roa, "Return on Assets (ROA) (%)", "Percentage")
    
    def return_on_capital_employed(self):
        """Calculates and plots Return on Capital Employed (ROCE) (%) = (EBIT / Capital Employed) * 100."""
        if not self.income_statement or not self.balance_sheet:
            return
        
        roce = {}
        for year in self.income_statement:
            ebit = self.income_statement.get(year, {}).get("EBIT", None)
            capital_employed = self.balance_sheet.get(year, {}).get("Total Assets", None)
            
            if ebit is not None and capital_employed:
                roce[year] = (ebit / capital_employed) * 100
        
        return ratios
        # plot_ratio(roce, "Return on Capital Employed (ROCE) (%)", "Percentage")
    
    def earnings_per_share(self):
        """Calculates and plots Earnings Per Share (EPS) if outstanding shares data is available, otherwise returns current EPS."""
        if not self.income_statement:
            return
        
        eps = {}
        for year in self.income_statement:
            net_profit = self.income_statement.get(year, {}).get("Net Income", None)
            shares_outstanding = self.balance_sheet.get(year, {}).get("Ordinary Shares Number", None)
            
            if net_profit is not None and shares_outstanding:
                eps[year] = net_profit / shares_outstanding
        
        if eps:
            return ratios
            # plot_ratio(eps, "Earnings Per Share (EPS)", "₹ per share")
        else:
            stock = yf.Ticker(self.ticker)
            return stock.info.get("trailingEps", "EPS data unavailable")

if __name__ == "__main__":
    ticker = "ALOKINDS.NS"
    duration = 5
    data = {
        "income_statement": get_income_statement(ticker, duration),
        "balance_sheet": get_balance_sheet(ticker, duration)
    }

    # print(data["balance_sheet"].keys())
    
    ratios = ProfitabilityRatios(ticker, duration, data)
    ratios.net_profit_margin()
    ratios.operating_profit_margin()
    ratios.return_on_equity()
    ratios.return_on_assets()
    ratios.return_on_capital_employed()
    ratios.earnings_per_share()
