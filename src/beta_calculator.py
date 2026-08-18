"""
Quantitative Beta Calculator Engine
Calculates CAPM Beta, Annualized Alpha, R-Squared Correlation, Annualized Volatility,
and 1-Year Total Return for NIFTY 50, Bank Nifty, and SENSEX 30 constituents.
"""

import os
import sys
import datetime
import logging
import numpy as np
import pandas as pd
from scipy import stats
import yfinance as yf

# Ensure local imports work whether script is executed directly or imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from index_fetcher import get_all_target_stocks

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BENCHMARKS = {
    "^NSEI": "NIFTY 50",
    "^NSEBANK": "Bank Nifty",
    "^BSESN": "SENSEX 30"
}

def classify_risk(beta: float) -> str:
    if pd.isna(beta):
        return "N/A"
    if beta < 0:
        return "Inverse Beta (< 0.0)"
    elif beta < 0.8:
        return "Defensive / Low Beta (< 0.8)"
    elif beta <= 1.2:
        return "Market-Like (0.8 - 1.2)"
    else:
        return "High Volatility (> 1.2)"

def download_price_data(symbols: list, benchmarks: list, period: str = "1y") -> pd.DataFrame:
    """Downloads daily adjusted closing prices for all stock symbols and benchmark indices."""
    all_tickers = sorted(list(set(symbols + benchmarks)))
    logging.info(f"Downloading historical daily data for {len(all_tickers)} tickers over period '{period}'...")
    
    try:
        data = yf.download(all_tickers, period=period, auto_adjust=True, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            if "Close" in data.columns.levels[0]:
                prices = data["Close"]
            else:
                prices = data.iloc[:, data.columns.get_level_values(0) == "Close"]
        else:
            prices = data
        
        # Clean missing values
        prices = prices.ffill().bfill()
        logging.info(f"Successfully downloaded price matrix shape: {prices.shape}")
        return prices
    except Exception as e:
        logging.error(f"Error downloading price data from yfinance: {e}")
        raise

def calculate_beta_metrics(stock_prices: pd.Series, benchmark_prices: pd.Series) -> dict:
    """
    Computes CAPM Beta, Alpha, R-Squared, and Volatility using Ordinary Least Squares (OLS).
    """
    # Daily percentage returns
    stock_returns = stock_prices.pct_change().dropna()
    bench_returns = benchmark_prices.pct_change().dropna()

    # Align dates
    combined = pd.concat([stock_returns, bench_returns], axis=1, join="inner").dropna()
    combined.columns = ["stock", "benchmark"]

    if len(combined) < 60:  # Need minimum sample size
        return {
            "beta": np.nan, "alpha": np.nan, "r_squared": np.nan,
            "volatility": np.nan, "return_1yr": np.nan
        }

    x = combined["benchmark"].values
    y = combined["stock"].values

    # OLS Regression: y = beta * x + alpha
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    beta = slope
    daily_alpha = intercept
    annual_alpha = (1 + daily_alpha) ** 252 - 1
    r_squared = r_value ** 2
    
    # Annualized Volatility (Standard Deviation of daily returns * sqrt(252))
    annual_volatility = combined["stock"].std() * np.sqrt(252)
    
    # 1-Year Cumulative Total Return
    start_price = stock_prices.iloc[0]
    end_price = stock_prices.iloc[-1]
    return_1yr = ((end_price - start_price) / start_price) if start_price > 0 else np.nan

    return {
        "beta": round(float(beta), 4),
        "alpha": round(float(annual_alpha), 4),
        "r_squared": round(float(r_squared), 4),
        "volatility": round(float(annual_volatility), 4),
        "return_1yr": round(float(return_1yr), 4)
    }

def run_pipeline(output_dir: str = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Runs the full beta calculation pipeline and updates output CSV files."""
    if output_dir is None:
        # Default data directory: project_root/data
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    os.makedirs(output_dir, exist_ok=True)

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    logging.info(f"--- Starting Beta Calculation Pipeline for Date: {today_str} ---")

    # 1. Fetch Target Stocks and Metadata
    stock_dict = get_all_target_stocks()
    stock_symbols = list(stock_dict.keys())
    benchmark_symbols = list(BENCHMARKS.keys())

    # 2. Download Price History
    prices = download_price_data(stock_symbols, benchmark_symbols, period="1y")

    # 3. Benchmark price series
    nifty_prices = prices["^NSEI"] if "^NSEI" in prices else None
    banknifty_prices = prices["^NSEBANK"] if "^NSEBANK" in prices else None
    sensex_prices = prices["^BSESN"] if "^BSESN" in prices else None

    if nifty_prices is None:
        raise ValueError("Critical Benchmark ^NSEI data is missing!")

    results = []

    for sym, meta in stock_dict.items():
        # Handle cross-exchange symbols (e.g. .BO vs .NS in price matrix)
        price_col = sym
        if price_col not in prices.columns:
            alt_sym = sym.replace(".BO", ".NS") if ".BO" in sym else sym.replace(".NS", ".BO")
            if alt_sym in prices.columns:
                price_col = alt_sym

        if price_col not in prices.columns or prices[price_col].isna().all():
            logging.warning(f"Skipping {sym} - Price data unavailable.")
            continue

        stock_p = prices[price_col]

        # Calculate Beta vs NIFTY 50 (Primary Market Benchmark)
        metrics_nifty = calculate_beta_metrics(stock_p, nifty_prices)

        # Calculate Beta vs SENSEX 30
        metrics_sensex = calculate_beta_metrics(stock_p, sensex_prices) if sensex_prices is not None else {"beta": np.nan}

        # Calculate Beta vs Bank Nifty if banking stock
        metrics_banknifty = calculate_beta_metrics(stock_p, banknifty_prices) if banknifty_prices is not None and "Bank Nifty" in meta["indices"] else {"beta": np.nan}

        beta_val = metrics_nifty["beta"]
        risk_cat = classify_risk(beta_val)

        results.append({
            "date": today_str,
            "symbol": sym,
            "company": meta["company"],
            "indices": meta["indices"],
            "sector": meta["sector"],
            "beta_nifty": beta_val,
            "beta_sensex": metrics_sensex["beta"],
            "beta_banknifty": metrics_banknifty["beta"],
            "alpha_annual": metrics_nifty["alpha"],
            "r_squared": metrics_nifty["r_squared"],
            "volatility_annual": metrics_nifty["volatility"],
            "return_1yr": metrics_nifty["return_1yr"],
            "risk_category": risk_cat
        })

    df_latest = pd.DataFrame(results)

    # Save latest_beta.csv
    latest_csv_path = os.path.join(output_dir, "latest_beta.csv")
    df_latest.to_csv(latest_csv_path, index=False)
    logging.info(f"Saved snapshot to: {latest_csv_path} ({len(df_latest)} stocks)")

    # Update beta_history.csv
    history_csv_path = os.path.join(output_dir, "beta_history.csv")
    if os.path.exists(history_csv_path):
        df_history = pd.read_csv(history_csv_path)
        # Remove old records for today if re-running
        df_history = df_history[df_history["date"] != today_str]
        df_history = pd.concat([df_history, df_latest], ignore_index=True)
    else:
        df_history = df_latest.copy()

    df_history.to_csv(history_csv_path, index=False)
    logging.info(f"Updated cumulative history: {history_csv_path} ({len(df_history)} total records)")

    return df_latest, df_history

if __name__ == "__main__":
    run_pipeline()
