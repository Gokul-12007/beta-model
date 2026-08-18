# 📈 Automated Indian Stocks Beta Tracker & Live Analytics Dashboard

[![Daily Beta Workflow](https://github.com/Gokul-12007/beta-model/actions/workflows/daily_beta.yml/badge.svg)](https://github.com/Gokul-12007/beta-model/actions/workflows/daily_beta.yml)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

An end-to-end quantitative financial tool that automatically calculates **CAPM Beta** (\(\beta\)), **Alpha** (\(\alpha\)), **R² Correlation**, **Annualized Volatility**, and **1-Year Returns** for every stock constituent in **NIFTY 50**, **Bank Nifty**, and **SENSEX 30** every single trading day.

---

## 🌟 Key Features

1. **Live Constituent Scraper**: Dynamically fetches live stock lists from NSE India & BSE official archives with automatic fallback support.
2. **Quantitative Engine**: Performs Ordinary Least Squares (OLS) linear regressions on 1 year of daily returns vs benchmark market indices (`^NSEI`, `^NSEBANK`, `^BSESN`).
3. **Automated GitHub Actions CI/CD**: Runs every weekday at **4:00 PM IST** (10:30 AM UTC) to compute daily metrics and automatically update repository CSV datasets (`latest_beta.csv` and `beta_history.csv`).
4. **Interactive Streamlit Web Application**:
   - Risk Category Segmentation (High Volatility, Market-Like, Defensive, Inverse Beta).
   - Plotly **Security Market Line (CAPM SML)** Scatter Charts.
   - Frequency Distributions & Industry Sector Volatility Heatmaps.
   - Historical stock beta trend timeline visualization.
   - Export CSV capability.

---

## 📐 Quantitative Methodology

### Capital Asset Pricing Model (CAPM)
Beta measures the systemic market risk or volatility of a stock relative to the broader index:

$$\beta = \frac{\text{Cov}(R_i, R_m)}{\text{Var}(R_m)}$$

Where:
- $R_i$: Daily percentage return of the stock $\ln(P_{t} / P_{t-1})$
- $R_m$: Daily percentage return of the benchmark index (NIFTY 50)

$$\text{Linear Model: } R_{i,t} = \alpha + \beta R_{m,t} + \epsilon_t$$

- **Beta ($\beta > 1.2$)**: High sensitivity / aggressive volatility stock.
- **Beta ($0.8 \le \beta \le 1.2$)**: Market-neutral movement.
- **Beta ($\beta < 0.8$)**: Defensive cushion stock during market downturns.
- **R² Score**: Percentage of stock variation explained by benchmark movement.
- **Annualized Volatility**: $\sigma_{\text{daily}} \times \sqrt{252}$

---

## ⚠️ Important Disclaimers & Caveats

- **yfinance Data Feed**: Uses Yahoo Finance public endpoints via `yfinance`. While suitable for personal quantitative projects, it is an unofficial feed and not an institutional direct exchange terminal.
- **CAPM Limitations**: Beta assumes linear risk relationships and normal distributions. It does not account for non-linear tail-risk, structural corporate changes, or sudden liquidity shocks.

---

## 🚀 Quickstart Guide (Local Setup)

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/Gokul-12007/beta-model.git
cd beta-model

# Create virtual environment
python -m venv venv

# Activate on Windows:
.\venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Calculation Engine
```bash
python src/beta_calculator.py
```

### 4. Launch Streamlit Web App
```bash
streamlit run app.py
```

---

## 🌐 GitHub & Streamlit Cloud Hosting Instructions

### Step A: Push Code to GitHub
1. Go to [GitHub.com](https://github.com) and click **New Repository**. Name it `beta-model` and set it to **Public**.
2. Open PowerShell/Terminal in `C:\Beta Model` and run:
```bash
git init
git add .
git commit -m "Initial commit: Indian Stocks Beta Model & Dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/beta-model.git
git push -u origin main
```

### Step B: Deploy Live Dashboard on Streamlit Community Cloud (Free)
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **Create app**.
3. Select your repository: `YOUR_GITHUB_USERNAME/beta-model`.
4. Main file path: `app.py`.
5. Click **Deploy!** Your live shareable dashboard link will be active in seconds.
