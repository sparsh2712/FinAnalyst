def generate_json_report(analysis_results, output_dir="./output"):
    """
    Generate a JSON report from analysis results.
    This is useful for debugging and API integration.
    
    Args:
        analysis_results (dict): Results from financial analysis
        output_dir (str): Output directory for the report
        
    Returns:
        str: Path to the generated JSON file
    """
    logger.info("Generating JSON report")
    
    # Extract company data
    company = analysis_results['company']
    ticker = company['ticker']
    
    # Create report directory
    report_dir = os.path.join(output_dir, 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    # Create report filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(report_dir, f"{ticker}_report_{timestamp}.json")
    
    # Prepare data for JSON serialization
    # Remove non-serializable objects like DataFrames
    json_data = {
        'company': {
            'ticker': company['ticker'],
            'name': company['name']
        },
        'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'ratios': {}
    }
    
    # Add profitability ratios
    if 'profit_df' in company and not company['profit_df'].empty:
        profit_df = company['profit_df']
        json_data['ratios']['profitability'] = profit_df.reset_index().to_dict(orient='records')
    
    # Add liquidity ratios
    if 'liquidity_df' in company and not company['liquidity_df'].empty:
        liquidity_df = company['liquidity_df']
        json_data['ratios']['liquidity'] = liquidity_df.reset_index().to_dict(orient='records')
    
    # Add solvency ratios if available
    if 'solvency_df' in company and not company['solvency_df'].empty:
        solvency_df = company['solvency_df']
        json_data['ratios']['solvency'] = solvency_df.reset_index().to_dict(orient='records')
    
    # Add efficiency ratios if available
    if 'efficiency_df' in company and not company['efficiency_df'].empty:
        efficiency_df = company['efficiency_df']
        json_data['ratios']['efficiency'] = efficiency_df.reset_index().to_dict(orient='records')
    
    # Add benchmark data
    if 'benchmarks' in analysis_results and analysis_results['benchmarks']:
        json_data['benchmarks'] = {}
        for b_ticker, b_data in analysis_results['benchmarks'].items():
            json_data['benchmarks'][b_ticker] = {
                'ratios': {}
            }
            
            # Add benchmark profitability ratios
            if 'profit_df' in b_data and not b_data['profit_df'].empty:
                json_data['benchmarks'][b_ticker]['ratios']['profitability'] = b_data['profit_df'].reset_index().to_dict(orient='records')
            
            # Add benchmark liquidity ratios
            if 'liquidity_df' in b_data and not b_data['liquidity_df'].empty:
                json_data['benchmarks'][b_ticker]['ratios']['liquidity'] = b_data['liquidity_df'].reset_index().to_dict(orient='records')
            
            # Add benchmark solvency ratios if available
            if 'solvency_df' in b_data and not b_data['solvency_df'].empty:
                json_data['benchmarks'][b_ticker]['ratios']['solvency'] = b_data['solvency_df'].reset_index().to_dict(orient='records')
            
            # Add benchmark efficiency ratios if available
            if 'efficiency_df' in b_data and not b_data['efficiency_df'].empty:
                json_data['benchmarks'][b_ticker]['ratios']['efficiency'] = b_data['efficiency_df'].reset_index().to_dict(orient='records')
    
    # Write to file
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, default=str)
    
    logger.info(f"JSON report generated: {report_file}")
    return report_file


if __name__ == "__main__":
    # Test the report generation with sample data
    import argparse
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Generate financial report")
    parser.add_argument("--input", required=True, help="Input JSON file with analysis results")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--format", default="html", choices=["html", "json", "both"], help="Report format")
    
    args = parser.parse_args()
    
    # Load analysis results
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            analysis_results = json.load(f)
        
        # Generate report
        if args.format == "html" or args.format == "both":
            html_report = generate_financial_report(analysis_results, args.output)
            print(f"HTML report generated: {html_report}")
        
        if args.format == "json" or args.format == "both":
            json_report = generate_json_report(analysis_results, args.output)
            print(f"JSON report generated: {json_report}")
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        logger.error(traceback.format_exc())
"""
Financial Report Generator

This script generates a comprehensive financial report for a company,
including all calculated ratios and visualizations.

The report is generated as an HTML file that can be easily shared and viewed.
"""

import os
import json
import logging
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_financial_report(analysis_results, output_dir="./output"):
    """
    
    # Prepare data for the template
    template_data = {
        'company_name': company_name,
        'ticker': ticker,
        'analysis_date': datetime.now().strftime("%Y-%m-%d"),
        'period': "5 years",  # This could be made dynamic
        
        # Profitability ratios
        'profit_trend_ratios': [],
        'profit_chart_paths': {},
        'profit_single_ratios': [],
        'profit_single_values': {},
        'profit_has_benchmarks': bool(benchmarks),
        'profit_benchmark_values': {},
        
        # Liquidity ratios
        'liquidity_trend_ratios': [],
        'liquidity_chart_paths': {},
        'liquidity_single_ratios': [],
        'liquidity_single_values': {},
        'liquidity_has_benchmarks': bool(benchmarks),
        'liquidity_benchmark_values': {},
        
        # Solvency ratios
        'solvency_data_available': not solvency_df.empty,
        'solvency_trend_ratios': [],
        'solvency_chart_paths': {},
        'solvency_single_ratios': [],
        'solvency_single_values': {},
        'solvency_has_benchmarks': bool(benchmarks),
        'solvency_benchmark_values': {},
        
        # Efficiency ratios
        'efficiency_data_available': not efficiency_df.empty,
        'efficiency_trend_ratios': [],
        'efficiency_chart_paths': {},
        'efficiency_single_ratios': [],
        'efficiency_single_values': {},
        'efficiency_has_benchmarks': bool(benchmarks),
        'efficiency_benchmark_values': {},
    }
    
    # Populate profitability data
    if not profit_df.empty:
        profit_trend_ratios = [
            'Net Profit Margin (%)', 
            'Operating Profit Margin (%)', 
            'Return on Equity (%)', 
            'Return on Assets (%)',
            'Return on Capital Employed (%)'
        ]
        
        for ratio in profit_trend_ratios:
            if ratio in profit_df.columns:
                template_data['profit_trend_ratios'].append(ratio)
                img_path = os.path.join(
                    '../', 
                    'profitability', 
                    f"{ratio.replace(' ', '_').replace('(', '').replace(')', '').replace('%', 'Pct')}.png"
                )
                template_data['profit_chart_paths'][ratio] = img_path
        
        if 'EPS (₹ per share)' in profit_df.columns:
            template_data['profit_single_ratios'].append('EPS (₹ per share)')
            template_data['profit_single_values']['EPS (₹ per share)'] = profit_df['EPS (₹ per share)'].iloc[-1]
            
            # Add benchmark values
            if benchmarks:
                template_data['profit_benchmark_values']['EPS (₹ per share)'] = {}
                for b_ticker, b_data in benchmarks.items():
                    if 'profit_df' in b_data and 'EPS (₹ per share)' in b_data['profit_df'].columns:
                        template_data['profit_benchmark_values']['EPS (₹ per share)'][b_ticker] = b_data['profit_df']['EPS (₹ per share)'].iloc[-1]
    
    # Populate liquidity data
    if not liquidity_df.empty:
        liquidity_trend_ratios = ['Current Ratio', 'Quick Ratio']
        
        for ratio in liquidity_trend_ratios:
            if ratio in liquidity_df.columns:
                template_data['liquidity_trend_ratios'].append(ratio)
                img_path = os.path.join(
                    '../', 
                    'liquidity', 
                    f"{ratio.replace(' ', '_')}.png"
                )
                template_data['liquidity_chart_paths'][ratio] = img_path
        
        if 'Cash Ratio' in liquidity_df.columns:
            template_data['liquidity_single_ratios'].append('Cash Ratio')
            template_data['liquidity_single_values']['Cash Ratio'] = liquidity_df['Cash Ratio'].iloc[-1]
            
            # Add benchmark values
            if benchmarks:
                template_data['liquidity_benchmark_values']['Cash Ratio'] = {}
                for b_ticker, b_data in benchmarks.items():
                    if 'liquidity_df' in b_data and 'Cash Ratio' in b_data['liquidity_df'].columns:
                        template_data['liquidity_benchmark_values']['Cash Ratio'][b_ticker] = b_data['liquidity_df']['Cash Ratio'].iloc[-1]
    
    # Populate solvency data if available
    if not solvency_df.empty:
        solvency_trend_ratios = ['Debt-to-Equity Ratio', 'Interest Coverage Ratio']
        
        for ratio in solvency_trend_ratios:
            if ratio in solvency_df.columns:
                template_data['solvency_trend_ratios'].append(ratio)
                img_path = os.path.join(
                    '../', 
                    'solvency', 
                    f"{ratio.replace(' ', '_').replace('-', '_')}.png"
                )
                template_data['solvency_chart_paths'][ratio] = img_path
        
        if 'Debt-to-Asset Ratio' in solvency_df.columns:
            template_data['solvency_single_ratios'].append('Debt-to-Asset Ratio')
            template_data['solvency_single_values']['Debt-to-Asset Ratio'] = solvency_df['Debt-to-Asset Ratio'].iloc[-1]
            
            # Add benchmark values
            if benchmarks:
                template_data['solvency_benchmark_values']['Debt-to-Asset Ratio'] = {}
                for b_ticker, b_data in benchmarks.items():
                    if 'solvency_df' in b_data and 'Debt-to-Asset Ratio' in b_data['solvency_df'].columns:
                        template_data['solvency_benchmark_values']['Debt-to-Asset Ratio'][b_ticker] = b_data['solvency_df']['Debt-to-Asset Ratio'].iloc[-1]
    
    # Populate efficiency data if available
    if not efficiency_df.empty:
        efficiency_trend_ratios = [
            'Asset Turnover Ratio', 
            'Inventory Turnover Ratio', 
            'Receivables Turnover Ratio'
        ]
        
        for ratio in efficiency_trend_ratios:
            if ratio in efficiency_df.columns:
                template_data['efficiency_trend_ratios'].append(ratio)
                img_path = os.path.join(
                    '../', 
                    'efficiency', 
                    f"{ratio.replace(' ', '_')}.png"
                )
                template_data['efficiency_chart_paths'][ratio] = img_path
        
        if 'Days Sales Outstanding' in efficiency_df.columns:
            template_data['efficiency_single_ratios'].append('Days Sales Outstanding')
            template_data['efficiency_single_values']['Days Sales Outstanding'] = efficiency_df['Days Sales Outstanding'].iloc[-1]
            
            # Add benchmark values
            if benchmarks:
                template_data['efficiency_benchmark_values']['Days Sales Outstanding'] = {}
                for b_ticker, b_data in benchmarks.items():
                    if 'efficiency_df' in b_data and 'Days Sales Outstanding' in b_data['efficiency_df'].columns:
                        template_data['efficiency_benchmark_values']['Days Sales Outstanding'][b_ticker] = b_data['efficiency_df']['Days Sales Outstanding'].iloc[-1]
    
    # Render template
    template = Template(html_template)
    report_html = template.render(**template_data)
    
    # Write to file
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_html)
    
    logger.info(f"Financial report generated: {report_file}")
    return report_file

    Generate a comprehensive financial report from analysis results.
    
    Args:
        analysis_results (dict): Results from financial analysis
        output_dir (str): Output directory for the report
        
    Returns:
        str: Path to the generated report file
    """
    logger.info("Generating financial report")
    
    # Extract data
    company = analysis_results['company']
    ticker = company['ticker']
    company_name = company['name']
    data = company['data']
    profit_df = company.get('profit_df', pd.DataFrame())
    liquidity_df = company.get('liquidity_df', pd.DataFrame())
    
    # Try to get solvency and efficiency dataframes if available
    solvency_df = company.get('solvency_df', pd.DataFrame())
    efficiency_df = company.get('efficiency_df', pd.DataFrame())
    
    # Extract benchmark data
    benchmarks = analysis_results.get('benchmarks', {})
    
    # Create report directory
    report_dir = os.path.join(output_dir, 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    # Create report filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(report_dir, f"{ticker}_report_{timestamp}.html")
    
    # Create HTML report template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Analysis Report: {{ company_name }}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
                color: #333;
            }
            h1, h2, h3 {
                color: #2c3e50;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .section {
                margin-top: 30px;
            }
            .chart-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: space-between;
            }
            .chart {
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 10px;
                margin-bottom: 20px;
                background: white;
                flex-basis: calc(50% - 20px);
            }
            .summary {
                background-color: #f8f9fa;
                padding: 15px;
                border-left: 4px solid #4e73df;
                margin-bottom: 20px;
            }
            .ratio-card {
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 15px;
                margin-bottom: 20px;
            }
            .ratio-value {
                font-size: 24px;
                color: #4e73df;
                margin-bottom: 5px;
            }
            .ratio-name {
                font-weight: bold;
                margin-bottom: 10px;
            }
            .trend-up {
                color: #1cc88a;
            }
            .trend-down {
                color: #e74a3b;
            }
            .trend-stable {
                color: #858796;
            }
            .no-data {
                color: #858796;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <h1>Financial Analysis Report: {{ company_name }} ({{ ticker }})</h1>
        <p>Analysis Date: {{ analysis_date }}</p>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <p>This report provides a comprehensive analysis of the financial ratios and performance
            metrics for {{ company_name }}. The analysis includes profitability, liquidity, solvency,
            and efficiency ratios calculated over a {{ period }} time period.</p>
        </div>
        
        <!-- Profitability Ratios -->
        <div class="section">
            <h2>1. Profitability Ratios</h2>
            
            <div class="chart-container">
                {% for ratio in profit_trend_ratios %}
                <div class="chart">
                    <h3>{{ ratio }}</h3>
                    <img src="{{ profit_chart_paths[ratio] }}" alt="{{ ratio }} chart" width="100%">
                </div>
                {% endfor %}
            </div>
            
            {% if 'EPS (₹ per share)' in profit_single_ratios %}
            <div class="ratio-card">
                <div class="ratio-name">Earnings Per Share (EPS)</div>
                <div class="ratio-value">₹{{ profit_single_values['EPS (₹ per share)']|round(2) }}</div>
                
                {% if profit_has_benchmarks %}
                <h4>Benchmark Comparison</h4>
                <table>
                    <tr>
                        <th>Company</th>
                        <th>EPS (₹)</th>
                    </tr>
                    <tr>
                        <td>{{ company_name }}</td>
                        <td>{{ profit_single_values['EPS (₹ per share)']|round(2) }}</td>
                    </tr>
                    {% for name, value in profit_benchmark_values['EPS (₹ per share)'].items() %}
                    <tr>
                        <td>{{ name }}</td>
                        <td>{{ value|round(2) }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% endif %}
            </div>
            {% endif %}
        </div>
        
        <!-- Liquidity Ratios -->
        <div class="section">
            <h2>2. Liquidity Ratios</h2>
            
            <div class="chart-container">
                {% for ratio in liquidity_trend_ratios %}
                <div class="chart">
                    <h3>{{ ratio }}</h3>
                    <img src="{{ liquidity_chart_paths[ratio] }}" alt="{{ ratio }} chart" width="100%">
                </div>
                {% endfor %}
            </div>
            
            {% if 'Cash Ratio' in liquidity_single_ratios %}
            <div class="ratio-card">
                <div class="ratio-name">Cash Ratio</div>
                <div class="ratio-value">{{ liquidity_single_values['Cash Ratio']|round(2) }}</div>
                
                {% if liquidity_has_benchmarks %}
                <h4>Benchmark Comparison</h4>
                <table>
                    <tr>
                        <th>Company</th>
                        <th>Cash Ratio</th>
                    </tr>
                    <tr>
                        <td>{{ company_name }}</td>
                        <td>{{ liquidity_single_values['Cash Ratio']|round(2) }}</td>
                    </tr>
                    {% for name, value in liquidity_benchmark_values['Cash Ratio'].items() %}
                    <tr>
                        <td>{{ name }}</td>
                        <td>{{ value|round(2) }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% endif %}
            </div>
            {% endif %}
        </div>
        
        <!-- Solvency Ratios -->
        {% if solvency_data_available %}
        <div class="section">
            <h2>3. Solvency Ratios</h2>
            
            <div class="chart-container">
                {% for ratio in solvency_trend_ratios %}
                <div class="chart">
                    <h3>{{ ratio }}</h3>
                    <img src="{{ solvency_chart_paths[ratio] }}" alt="{{ ratio }} chart" width="100%">
                </div>
                {% endfor %}
            </div>
            
            {% if 'Debt-to-Asset Ratio' in solvency_single_ratios %}
            <div class="ratio-card">
                <div class="ratio-name">Debt-to-Asset Ratio</div>
                <div class="ratio-value">{{ solvency_single_values['Debt-to-Asset Ratio']|round(2) }}</div>
                
                {% if solvency_has_benchmarks %}
                <h4>Benchmark Comparison</h4>
                <table>
                    <tr>
                        <th>Company</th>
                        <th>Debt-to-Asset Ratio</th>
                    </tr>
                    <tr>
                        <td>{{ company_name }}</td>
                        <td>{{ solvency_single_values['Debt-to-Asset Ratio']|round(2) }}</td>
                    </tr>
                    {% for name, value in solvency_benchmark_values['Debt-to-Asset Ratio'].items() %}
                    <tr>
                        <td>{{ name }}</td>
                        <td>{{ value|round(2) }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% endif %}
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <!-- Efficiency Ratios -->
        {% if efficiency_data_available %}
        <div class="section">
            <h2>4. Efficiency Ratios</h2>
            
            <div class="chart-container">
                {% for ratio in efficiency_trend_ratios %}
                <div class="chart">
                    <h3>{{ ratio }}</h3>
                    <img src="{{ efficiency_chart_paths[ratio] }}" alt="{{ ratio }} chart" width="100%">
                </div>
                {% endfor %}
            </div>
            
            {% if 'Days Sales Outstanding' in efficiency_single_ratios %}
            <div class="ratio-card">
                <div class="ratio-name">Days Sales Outstanding (DSO)</div>
                <div class="ratio-value">{{ efficiency_single_values['Days Sales Outstanding']|round(2) }} days</div>
                
                {% if efficiency_has_benchmarks %}
                <h4>Benchmark Comparison</h4>
                <table>
                    <tr>
                        <th>Company</th>
                        <th>DSO (days)</th>
                    </tr>
                    <tr>
                        <td>{{ company_name }}</td>
                        <td>{{ efficiency_single_values['Days Sales Outstanding']|round(2) }}</td>
                    </tr>
                    {% for name, value in efficiency_benchmark_values['Days Sales Outstanding'].items() %}
                    <tr>
                        <td>{{ name }}</td>
                        <td>{{ value|round(2) }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% endif %}
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="section">
            <h2>Analysis Conclusion</h2>
            <p>This report provides a comprehensive overview of {{ company_name }}'s financial performance
            through various ratio analyses. For a more detailed interpretation of these results, please
            consult with a financial advisor or analyst.</p>
        </div>
        
        <p><small>Generated on {{ analysis_date }} using Financial Ratio Analysis Tool</small></p>
    </body>
    </html>
    """