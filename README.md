# Financial Ratio Analysis System

## Financial Ratios to Compute
The system should compute the following financial ratios, categorized by type. Some ratios require **trend graphs** for historical analysis, while others are best represented as **single numbers** for benchmarking.

### 1. Profitability Ratios
#### Trend Graphs (Past 5 Years, Benchmarked Against Industry Average):
- **Net Profit Margin (%)** = (Net Profit / Revenue) * 100  
- **Operating Profit Margin (%)** = (Operating Profit / Revenue) * 100  
- **Return on Equity (ROE) (%)** = (Net Profit / Shareholders' Equity) * 100  
- **Return on Assets (ROA) (%)** = (Net Profit / Total Assets) * 100  
- **Return on Capital Employed (ROCE) (%)** = (EBIT / Capital Employed) * 100  

#### Single Numbers (Benchmarked Against Both Industry Average & Market Average):
- **Earnings Per Share (EPS) (₹ per share)** = Net Profit / Total Outstanding Shares  

### 2. Liquidity Ratios
#### Trend Graphs (Past 5 Years, Benchmarked Against Industry Average):
- **Current Ratio** = Current Assets / Current Liabilities  
- **Quick Ratio** = (Current Assets - Inventory) / Current Liabilities  

#### Single Numbers (Benchmarked Against Industry Average):
- **Cash Ratio** = Cash & Cash Equivalents / Current Liabilities  

### 3. Solvency Ratios
#### Trend Graphs (Past 5 Years, Benchmarked Against Industry Average):
- **Debt-to-Equity (D/E) Ratio** = Total Debt / Shareholders' Equity  
- **Interest Coverage Ratio** = EBIT / Interest Expense  

#### Single Numbers (Benchmarked Against Industry Average):
- **Debt-to-Asset Ratio** = Total Debt / Total Assets  

### 4. Efficiency Ratios
#### Trend Graphs (Past 5 Years, Benchmarked Against Industry Average):
- **Asset Turnover Ratio** = Revenue / Average Total Assets  
- **Inventory Turnover Ratio** = Cost of Goods Sold / Average Inventory  
- **Receivables Turnover Ratio** = Revenue / Average Accounts Receivable  

#### Single Numbers (Benchmarked Against Industry Average):
- **Days Sales Outstanding (DSO)** = (Accounts Receivable / Revenue) * 365  

### 5. Valuation Ratios
#### Trend Graphs (Past 5 Years, Benchmarked Against Both Industry & Market Average):
- **Price-to-Earnings (P/E) Ratio** = Stock Price / Earnings Per Share  
- **Price-to-Book (P/B) Ratio** = Stock Price / Book Value Per Share  

#### Single Numbers (Benchmarked Against Industry Average):
- **Enterprise Value to EBITDA (EV/EBITDA)** = (Market Cap + Debt - Cash) / EBITDA  

### 6. Market Performance Ratios
#### Trend Graphs (Past 5 Years, Benchmarked Against Market Average):
- **Dividend Yield (%)** = (Dividend Per Share / Stock Price) * 100  
- **Beta (Stock Volatility)** = Measures volatility relative to the market  

#### Single Numbers (Benchmarked Against Market Average):
- **Market Capitalization** = Stock Price * Total Shares Outstanding  

## Benchmarking Requirements
Each ratio must be benchmarked against:
1. **Industry Peers** – Compare against competitors in the same sector.
2. **Market Averages** – Compare against NIFTY 50 or Sensex, where applicable.
3. **Historical Trends** – Compute 5-year trends to detect improvements or declines.

## Visualization Requirements
- Ratios listed under **Trend Graphs** should be visualized using **line charts** for multi-year trends.
- Ratios under **Single Numbers** should be displayed as **point values** with clear benchmarking indicators.

