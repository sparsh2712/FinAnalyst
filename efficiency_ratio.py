import yfinance as yf
import json
import pandas as pd
import matplotlib.pyplot as plt
from financial_data_utils import plot_ratio, get_balance_sheet, get_income_statement

class EfficiencyRatios:
    """Calculates efficiency ratios for a given stock ticker based on financial data."""
    
    def __init__(self, ticker, duration, data):
        self.ticker = ticker
        self.duration = duration
        self.data = data
        self.income_statement = data.get("income_statement", {})
        self.balance_sheet = data.get("balance_sheet", {})
    
    def asset_turnover_ratio(self):
        """Calculates and plots Asset Turnover Ratio = Revenue / Average Total Assets."""
        ratios = {}
        for year in self.income_statement:
            revenue = self.income_statement.get(year, {}).get("Total Revenue", None)
            total_assets = self.balance_sheet.get(year, {}).get("Total Assets", None)
            prev_assets = self.balance_sheet.get(str(int(year)-1), {}).get("Total Assets", None)
            
            if revenue is not None and total_assets is not None and prev_assets is not None:
                avg_assets = (total_assets + prev_assets) / 2
                ratios[year] = revenue / avg_assets
        
        return ratios
        # plot_ratio(ratios, "Asset Turnover Ratio", "Times")
    
    def inventory_turnover_ratio(self):
        """Calculates and plots Inventory Turnover Ratio = Cost of Goods Sold / Average Inventory."""
        ratios = {}
        for year in self.income_statement:
            cogs = self.income_statement.get(year, {}).get("Cost Of Revenue", None)
            inventory = (self.balance_sheet.get(year, {}).get("Inventory") or 0) + (self.balance_sheet.get(year, {}).get("Other Inventories") or 0)
            prev_inventory = (self.balance_sheet.get(str(int(year)-1), {}).get("Inventory") or 0) + (self.balance_sheet.get(str(int(year)-1), {}).get("Other Inventories") or 0)
            
            if cogs is not None and inventory > 0 and prev_inventory > 0:
                avg_inventory = (inventory + prev_inventory) / 2
                ratios[year] = cogs / avg_inventory
        
        return ratios
        # plot_ratio(ratios, "Inventory Turnover Ratio", "Times")
    
    def receivables_turnover_ratio(self):
        """Calculates and plots Receivables Turnover Ratio = Revenue / Average Accounts Receivable."""
        ratios = {}
        for year in self.income_statement:
            revenue = self.income_statement.get(year, {}).get("Total Revenue", None)
            accounts_receivable = self.balance_sheet.get(year, {}).get("Accounts Receivable", None)
            prev_accounts_receivable = self.balance_sheet.get(str(int(year)-1), {}).get("Accounts Receivable", None)
            
            if revenue is not None and accounts_receivable is not None and prev_accounts_receivable is not None:
                avg_receivables = (accounts_receivable + prev_accounts_receivable) / 2
                ratios[year] = revenue / avg_receivables
        
        return ratios
        #plot_ratio(ratios, "Receivables Turnover Ratio", "Times")

if __name__ == "__main__":
    ticker = "RELIANCE.NS"
    duration = 5
    data = {
        "income_statement": get_income_statement(ticker, duration),
        "balance_sheet": get_balance_sheet(ticker, duration)
    }
    
    ratios = EfficiencyRatios(ticker, duration, data)
    ratios.asset_turnover_ratio()
    ratios.inventory_turnover_ratio()
    ratios.receivables_turnover_ratio()