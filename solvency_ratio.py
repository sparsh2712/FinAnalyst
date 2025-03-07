import yfinance as yf
import json
import pandas as pd
from financial_data_utils import plot_ratio, get_balance_sheet, get_income_statement
import matplotlib.pyplot as plt

class SolvencyRatios:
    """Calculates solvency ratios for a given stock ticker based on financial data."""
    
    def __init__(self, ticker, duration, data):
        self.ticker = ticker
        self.duration = duration
        self.data = data
        self.income_statement = data.get("income_statement", {})
        self.balance_sheet = data.get("balance_sheet", {})
    
    def debt_to_equity_ratio(self):
        """Calculates and plots Debt-to-Equity (D/E) Ratio = Total Debt / Shareholders' Equity."""
        if not self.balance_sheet:
            return {}
        
        de_ratio = {}
        for year in self.balance_sheet:
            total_debt = self.balance_sheet.get(year, {}).get("Total Debt", None)
            equity = self.balance_sheet.get(year, {}).get("Stockholders Equity", None)
            
            if total_debt is not None and equity:
                de_ratio[year] = total_debt / equity
        
        return de_ratio
        # plot_ratio(de_ratio, "Debt-to-Equity (D/E) Ratio", "Ratio")
    
    def interest_coverage_ratio(self):
        """Calculates and plots Interest Coverage Ratio = EBIT / Interest Expense."""
        if not self.income_statement:
            return {}
        
        icr = {}
        for year in self.income_statement:
            ebit = self.income_statement.get(year, {}).get("EBIT", None)
            interest_expense = self.income_statement.get(year, {}).get("Interest Expense", None)
            
            if ebit is not None and interest_expense and interest_expense != 0:
                icr[year] = ebit / interest_expense
        
        return icr
        # plot_ratio(icr, "Interest Coverage Ratio", "Ratio")
    
    def debt_to_asset_ratio(self):
        """Calculates and plots Debt-to-Asset Ratio = Total Debt / Total Assets."""
        if not self.balance_sheet:
            return {}
        
        da_ratio = {}
        for year in self.balance_sheet:
            total_debt = self.balance_sheet.get(year, {}).get("Total Debt", None)
            total_assets = self.balance_sheet.get(year, {}).get("Total Assets", None)
            
            if total_debt is not None and total_assets:
                da_ratio[year] = total_debt / total_assets
        
        return da_ratio
        # plot_ratio(da_ratio, "Debt-to-Asset Ratio", "Ratio")

if __name__ == "__main__":
    ticker = "ZOMATO.NS"
    duration = 5
    data = {
        "income_statement": get_income_statement(ticker, duration),
        "balance_sheet": get_balance_sheet(ticker, duration)
    }
    
    ratios = SolvencyRatios(ticker, duration, data)
    ratios.debt_to_equity_ratio()
    ratios.interest_coverage_ratio()
    ratios.debt_to_asset_ratio()
