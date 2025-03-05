# Financial Ratio Analysis System

## Financial Ratios to Compute

The system should compute the following financial ratios, categorized by type. Some ratios require **trend graphs** for historical analysis, while others are best represented as **single numbers**.

### 1. Profitability Ratios

#### Trend Graphs (Past 5 Years):

- **Net Profit Margin (%)** = (Net Profit / Revenue) \* 100
- **Operating Profit Margin (%)** = (Operating Profit / Revenue) \* 100
- **Return on Equity (ROE) (%)** = (Net Profit / Shareholders' Equity) \* 100
- **Return on Assets (ROA) (%)** = (Net Profit / Total Assets) \* 100
- **Return on Capital Employed (ROCE) (%)** = (EBIT / Capital Employed) \* 100

#### Single Numbers:

- **Earnings Per Share (EPS) (₹ per share)** = Net Profit / Total Outstanding Shares

### 2. Liquidity Ratios

#### Trend Graphs (Past 5 Years):

- **Current Ratio** = Current Assets / Current Liabilities
- **Quick Ratio** = (Current Assets - Inventory) / Current Liabilities

#### Single Numbers:

- **Cash Ratio** = Cash & Cash Equivalents / Current Liabilities

### 3. Solvency Ratios

#### Trend Graphs (Past 5 Years):

- **Debt-to-Equity (D/E) Ratio** = Total Debt / Shareholders' Equity
- **Interest Coverage Ratio** = EBIT / Interest Expense

#### Single Numbers:

- **Debt-to-Asset Ratio** = Total Debt / Total Assets

### 4. Efficiency Ratios

#### Trend Graphs (Past 5 Years):

- **Asset Turnover Ratio** = Revenue / Average Total Assets
- **Inventory Turnover Ratio** = Cost of Goods Sold / Average Inventory
- **Receivables Turnover Ratio** = Revenue / Average Accounts Receivable

#### Single Numbers:

- **Days Sales Outstanding (DSO)** = (Accounts Receivable / Revenue) \* 365

### 5. Valuation Ratios

#### Trend Graphs (Past 5 Years):

- **Price-to-Earnings (P/E) Ratio** = Stock Price / Earnings Per Share
- **Price-to-Book (P/B) Ratio** = Stock Price / Book Value Per Share

#### Single Numbers:

- **Enterprise Value to EBITDA (EV/EBITDA)** = (Market Cap + Debt - Cash) / EBITDA

### 6. Market Performance Ratios

#### Trend Graphs (Past 5 Years):

- **Dividend Yield (%)** = (Dividend Per Share / Stock Price) \* 100
- **Beta (Stock Volatility)** = Measures volatility relative to the market

#### Single Numbers:

- **Market Capitalization** = Stock Price \* Total Shares Outstanding

## Visualization Requirements

- Ratios listed under **Trend Graphs** should be visualized using **line charts** for multi-year trends.
- Ratios under **Single Numbers** should be displayed as **point values**.

## Dashboard Implementation Using Streamlit

The system should include a **Streamlit-based dashboard** that allows users to enter the name of a company. The system should:

1. **Map the entered company name** to the closest match in `company_ticker_map.csv`.
2. **Fetch financial data** for the mapped company and compute the required ratios.
3. **Display historical trend graphs** for applicable ratios over the past 5 years.
4. **Allow users to download computed ratio data** as a CSV file.

## Data Sources

The relevant financial data can be pulled directly via **yfinance**

This document serves as the specification for implementing the financial ratio analysis system.

