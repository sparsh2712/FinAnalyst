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
            return {}
        
        net_profit_margin = {}
        for year, data in self.income_statement.items():
            net_profit = data.get("Net Income", None)
            revenue = data.get("Total Revenue", None)
            
            if net_profit is not None and revenue:
                net_profit_margin[year] = (net_profit / revenue) * 100
        
        return net_profit_margin
    
    def operating_profit_margin(self):
        """Calculates and plots Operating Profit Margin (%) = (Operating Profit / Revenue) * 100."""
        if not self.income_statement:
            return {}
        
        operating_profit_margin = {}
        for year, data in self.income_statement.items():
            operating_profit = data.get("Operating Income", None)
            revenue = data.get("Total Revenue", None)
            
            if operating_profit is not None and revenue:
                operating_profit_margin[year] = (operating_profit / revenue) * 100
        
        return operating_profit_margin
    
    def return_on_equity(self):
        """Calculates and plots Return on Equity (ROE) (%) = (Net Profit / Shareholders' Equity) * 100."""
        if not self.income_statement or not self.balance_sheet:
            return {}
        
        roe = {}
        for year in self.income_statement:
            net_profit = self.income_statement.get(year, {}).get("Net Income", None)
            equity = self.balance_sheet.get(year, {}).get("Stockholders Equity", None)
            
            if net_profit is not None and equity and equity != 0:
                roe[year] = (net_profit / equity) * 100
        
        return roe
    
    def return_on_assets(self):
        """Calculates and plots Return on Assets (ROA) (%) = (Net Profit / Total Assets) * 100."""
        if not self.income_statement or not self.balance_sheet:
            return {}
        
        roa = {}
        for year in self.income_statement:
            net_profit = self.income_statement.get(year, {}).get("Net Income", None)
            total_assets = self.balance_sheet.get(year, {}).get("Total Assets", None)
            
            if net_profit is not None and total_assets and total_assets != 0:
                roa[year] = (net_profit / total_assets) * 100
        
        return roa
    
    def return_on_capital_employed(self):
        """Calculates and plots Return on Capital Employed (ROCE) (%) = (EBIT / Capital Employed) * 100."""
        if not self.income_statement or not self.balance_sheet:
            return {}
        
        roce = {}
        for year in self.income_statement:
            ebit = self.income_statement.get(year, {}).get("EBIT", None)
            capital_employed = self.balance_sheet.get(year, {}).get("Total Assets", None)
            
            if ebit is not None and capital_employed and capital_employed != 0:
                roce[year] = (ebit / capital_employed) * 100
        
        return roce
    
    def earnings_per_share(self):
        """Calculates and plots Earnings Per Share (EPS) if outstanding shares data is available, otherwise returns current EPS."""
        if not self.income_statement:
            return {}
        
        eps = {}
        for year in self.income_statement:
            net_profit = self.income_statement.get(year, {}).get("Net Income", None)
            shares_outstanding = self.balance_sheet.get(year, {}).get("Ordinary Shares Number", None)
            
            if net_profit is not None and shares_outstanding and shares_outstanding > 0:
                eps[year] = net_profit / shares_outstanding
        
        return eps