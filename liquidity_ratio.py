import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from financial_data_utils import get_balance_sheet, plot_ratio

class LiquidityRatios:
    """Calculates liquidity ratios for a given stock ticker based on financial data."""
    
    def __init__(self, ticker, duration, data):
        self.ticker = ticker
        self.duration = duration
        self.data = data
        self.balance_sheet = data.get("balance_sheet", {})
    
    def current_ratio(self):
        """Calculates and plots Current Ratio = Current Assets / Current Liabilities."""
        if not self.balance_sheet:
            return {}
        
        current_ratio = {}
        for year, data in self.balance_sheet.items():
            current_assets = data.get("Current Assets", None)
            current_liabilities = data.get("Current Liabilities", None)
            
            if current_assets is not None and current_liabilities:
                current_ratio[year] = current_assets / current_liabilities
        
        return current_ratio
        # plot_ratio(current_ratio, "Current Ratio", "Ratio")
    
    def quick_ratio(self):
        """Calculates and plots Quick Ratio = (Current Assets - Inventory) / Current Liabilities."""
        if not self.balance_sheet:
            return {}
        
        quick_ratio = {}
        for year, data in self.balance_sheet.items():
            current_assets = data.get("Current Assets", None)
            inventory = data.get("Inventory", 0)
            current_liabilities = data.get("Current Liabilities", None)
            
            if current_assets is not None and current_liabilities:
                quick_ratio[year] = (current_assets - inventory) / current_liabilities
        
        return quick_ratio
        # plot_ratio(quick_ratio, "Quick Ratio", "Ratio")
    
    def cash_ratio(self):
        """Calculates and plots Cash Ratio = Cash & Cash Equivalents / Current Liabilities."""
        if not self.balance_sheet:
            return
        
        cash_ratio = {}
        for year, data in self.balance_sheet.items():
            cash_equivalents = data.get("Cash And Cash Equivalents", None)
            current_liabilities = data.get("Current Liabilities", None)
            
            if cash_equivalents is not None and current_liabilities:
                cash_ratio[year] = cash_equivalents / current_liabilities
        
        return cash_ratio
        # plot_ratio(cash_ratio, "Cash Ratio", "Ratio")

if __name__ == "__main__":
    ticker = "ZOMATO.NS"
    duration = 5
    data = {
        "balance_sheet": get_balance_sheet(ticker, duration)
    }
    
    ratios = LiquidityRatios(ticker, duration, data)
    ratios.current_ratio()
    ratios.quick_ratio()
    ratios.cash_ratio()
