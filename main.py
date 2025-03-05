"""
Financial Analysis Dashboard

This script creates a comprehensive dashboard for analyzing financial ratios.
It integrates all ratio calculation modules and provides a streamlined interface
for fetching data, calculating ratios, and visualizing results.

Usage:
    streamlit run financial_dashboard.py
"""

import os
import json
import logging
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Import utility modules
from financial_data_utils import fetch_financial_data, save_to_json, load_from_json, create_output_directories
from profitability_ratios import calculate_profitability_ratios, convert_ratios_to_dataframe as convert_profit_ratios
from liquidity_ratios import calculate_liquidity_ratios, convert_ratios_to_dataframe as convert_liquidity_ratios

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def map_company_to_ticker(company_name, mapping_file="company_ticker_map.csv"):
    """
    Map company name to ticker symbol using the mapping file.
    
    Args:
        company_name (str): Company name
        mapping_file (str): Path to mapping CSV file
        
    Returns:
        tuple: (ticker, company_name) or (None, None) if not found
    """
    try:
        df = pd.read_csv(mapping_file)
        
        # Try exact match (case-insensitive)
        exact_matches = df[df["Company Name"].str.lower() == company_name.lower()]
        if not exact_matches.empty:
            match = exact_matches.iloc[0]
            return match["Symbol"], match["Company Name"]
        
        # Try contains match
        contains_matches = df[df["Company Name"].str.contains(company_name, case=False)]
        if not contains_matches.empty:
            match = contains_matches.iloc[0]
            logger.info(f"Found approximate match: {match['Company Name']} ({match['Symbol']})")
            return match["Symbol"], match["Company Name"]
        
        # Try word matching
        words = company_name.lower().split()
        for word in words:
            if len(word) > 3:  # Only use words with more than 3 characters
                word_matches = df[df["Company Name"].str.lower().str.contains(r'\b{}\b'.format(word), regex=True)]
                if not word_matches.empty:
                    match = word_matches.iloc[0]
                    logger.info(f"Found word match on '{word}': {match['Company Name']} ({match['Symbol']})")
                    return match["Symbol"], match["Company Name"]
        
        logger.warning(f"No match found for company name: {company_name}")
        return None, None
    
    except Exception as e:
        logger.error(f"Error mapping company to ticker: {str(e)}")
        return None, None

def analyze_company(ticker, company_name, period="5y", benchmark_tickers=None, output_dir="./output"):
    """
    Analyze financial ratios for a company.
    
    Args:
        ticker (str): Company ticker symbol
        company_name (str): Company name
        period (str): Analysis period (e.g., "5y" for 5 years)
        benchmark_tickers (list): List of benchmark ticker symbols
        output_dir (str): Base output directory
        
    Returns:
        dict: Dictionary with analysis results
    """
    # Create output directories
    directories = create_output_directories(output_dir)
    
    # Fetch and save data
    data_file = os.path.join(directories['json'], f"{ticker}_data.json")
    
    try:
        # Check if data already exists
        if os.path.exists(data_file):
            logger.info(f"Loading existing data for {ticker} from {data_file}")
            data = load_from_json(data_file)
        else:
            logger.info(f"Fetching new data for {ticker}")
            data = fetch_financial_data(ticker, period)
            save_to_json(data