"""
Streamlit Web Application: Indian Stocks Beta Tracker Dashboard
Interactive visualization & analytics for NIFTY 50, Bank Nifty & SENSEX CAPM Beta metrics.
"""

import os
import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Indian Stocks Beta Tracker | CAPM Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern visual design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    .main-header h1 {
        color: #00F2FE;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-size: 2.4rem;
    }

    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 0.3rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8FAFC;
    }

    .metric-sub {
        font-size: 0.8rem;
        color: #38BDF8;
        margin-top: 0.2rem;
    }

    .badge-defensive {
        background-color: #064E3B;
        color: #34D399;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
    }

    .badge-market {
        background-color: #1E3A8A;
        color: #60A5FA;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
    }

    .badge-volatile {
        background-color: #7C2D12;
        color: #FDBA74;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
    }

    /* Style dataframe container */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Path to data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
LATEST_CSV = os.path.join(DATA_DIR, "latest_beta.csv")
HISTORY_CSV = os.path.join(DATA_DIR, "beta_history.csv")

@st.cache_data(ttl=600)
def load_data():
    if not os.path.exists(LATEST_CSV):
        # Generate data if missing
        try:
            from src.beta_calculator import run_pipeline
            run_pipeline(DATA_DIR)
        except Exception as e:
            st.error(f"Error executing data engine: {e}")
            return pd.DataFrame(), pd.DataFrame()

    df_latest = pd.read_csv(LATEST_CSV) if os.path.exists(LATEST_CSV) else pd.DataFrame()
    df_history = pd.read_csv(HISTORY_CSV) if os.path.exists(HISTORY_CSV) else pd.DataFrame()
    return df_latest, df_history

df_latest, df_history = load_data()

# Header Section
st.markdown("""
<div class="main-header">
    <h1>📈 Indian Stocks Beta Tracker</h1>
    <p style="font-size: 1.1rem; opacity: 0.9; margin: 0;">
        Automated CAPM Risk Analysis for <b>NIFTY 50</b>, <b>Bank Nifty</b> & <b>SENSEX 30</b> stocks.
    </p>
</div>
""", unsafe_allow_html=True)

if df_latest.empty:
    st.warning("⚠️ No beta data found. Please run `python src/beta_calculator.py` locally to populate dataset.")
    st.stop()

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")

# Index Filter
index_options = ["All Indices", "NIFTY 50", "Bank Nifty", "SENSEX 30"]
selected_index = st.sidebar.selectbox("Select Benchmark Index", index_options)

# Risk Category Filter
risk_options = ["All Risk Categories", "High Volatility (> 1.2)", "Market-Like (0.8 - 1.2)", "Defensive / Low Beta (< 0.8)", "Inverse Beta (< 0.0)"]
selected_risk = st.sidebar.selectbox("Risk Classification", risk_options)

# Sector Filter
sectors = ["All Sectors"] + sorted(list(df_latest["sector"].dropna().unique()))
selected_sector = st.sidebar.selectbox("Industry Sector", sectors)

# Stock Search Bar
search_query = st.sidebar.text_input("Search Stock Ticker / Name", "").strip().upper()

# Filter Logic
df_filtered = df_latest.copy()

if selected_index != "All Indices":
    df_filtered = df_filtered[df_filtered["indices"].str.contains(selected_index, na=False)]

if selected_risk != "All Risk Categories":
    df_filtered = df_filtered[df_filtered["risk_category"] == selected_risk]

if selected_sector != "All Sectors":
    df_filtered = df_filtered[df_filtered["sector"] == selected_sector]

if search_query:
    df_filtered = df_filtered[
        df_filtered["symbol"].str.contains(search_query, na=False) |
        df_filtered["company"].str.contains(search_query, na=False)
    ]

# Top KPI Summary Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Tracked Stocks</div>
        <div class="metric-value">{len(df_filtered)}</div>
        <div class="metric-sub">Out of {len(df_latest)} universe</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if not df_filtered.empty:
        max_row = df_filtered.loc[df_filtered["beta_nifty"].idxmax()]
        max_sym = max_row['company']
        max_beta = max_row['beta_nifty']
    else:
        max_sym, max_beta = "N/A", 0.0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Most Volatile Stock</div>
        <div class="metric-value" style="color: #F87171;">{max_beta:.2f}</div>
        <div class="metric-sub">{max_sym}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if not df_filtered.empty:
        positive_df = df_filtered[df_filtered["beta_nifty"] > 0]
        if not positive_df.empty:
            min_row = positive_df.loc[positive_df["beta_nifty"].idxmin()]
            min_sym = min_row['company']
            min_beta = min_row['beta_nifty']
        else:
            min_sym, min_beta = "N/A", 0.0
    else:
        min_sym, min_beta = "N/A", 0.0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Most Defensive Gem</div>
        <div class="metric-value" style="color: #34D399;">{min_beta:.2f}</div>
        <div class="metric-sub">{min_sym}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_b = df_filtered["beta_nifty"].mean() if not df_filtered.empty else 1.0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Portfolio Beta</div>
        <div class="metric-value" style="color: #38BDF8;">{avg_b:.2f}</div>
        <div class="metric-sub">Benchmark \(\beta = 1.00\)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Content Tabs
tab_table, tab_scatter, tab_hist, tab_sector, tab_history_chart, tab_info = st.tabs([
    "📋 Interactive Beta Table",
    "🎯 Security Market Line (CAPM Scatter)",
    "📊 Beta Distribution",
    "🏢 Sector Breakdown",
    "📉 Historical Trends",
    "ℹ️ Methodology & Caveats"
])

with tab_table:
    st.subheader("Data Snapshot")
    st.caption("Updated daily after market close (~4:00 PM IST). Target benchmark: **NIFTY 50**.")

    # Formatting display columns
    display_df = df_filtered.copy()
    
    display_df["return_1yr_pct"] = (display_df["return_1yr"] * 100).map("{:+.2f}%".format)
    display_df["volatility_pct"] = (display_df["volatility_annual"] * 100).map("{:.2f}%".format)
    display_df["alpha_pct"] = (display_df["alpha_annual"] * 100).map("{:+.2f}%".format)
    
    columns_to_show = {
        "company": "Company",
        "symbol": "Ticker",
        "sector": "Sector",
        "beta_nifty": "Beta (NIFTY 50)",
        "beta_sensex": "Beta (SENSEX)",
        "beta_banknifty": "Beta (Bank Nifty)",
        "r_squared": "R² Correlation",
        "volatility_pct": "Annual Volatility",
        "return_1yr_pct": "1-Yr Return",
        "risk_category": "Risk Category"
    }
    
    render_df = display_df[list(columns_to_show.keys())].rename(columns=columns_to_show)
    
    st.dataframe(
        render_df,
        column_config={
            "Beta (NIFTY 50)": st.column_config.NumberColumn(format="%.3f"),
            "R² Correlation": st.column_config.NumberColumn(format="%.3f"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Download Button
    csv_bytes = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_bytes,
        file_name=f"beta_metrics_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with tab_scatter:
    st.subheader("Capital Asset Pricing Model (CAPM) Security Market Line")
    st.caption("Plots 1-Year Total Return vs. Beta relative to NIFTY 50. Bubble size represents Annualized Volatility.")

    if not df_filtered.empty:
        fig_sml = px.scatter(
            df_filtered,
            x="beta_nifty",
            y="return_1yr",
            size="volatility_annual",
            color="risk_category",
            hover_name="company",
            hover_data={
                "symbol": True,
                "sector": True,
                "beta_nifty": ":.3f",
                "r_squared": ":.3f",
                "return_1yr": ":.2%",
                "volatility_annual": ":.2%"
            },
            labels={
                "beta_nifty": "Beta (Sensitivity to NIFTY 50)",
                "return_1yr": "1-Year Return",
                "risk_category": "Risk Category",
                "volatility_annual": "Volatility"
            },
            color_discrete_map={
                "High Volatility (> 1.2)": "#EF4444",
                "Market-Like (0.8 - 1.2)": "#3B82F6",
                "Defensive / Low Beta (< 0.8)": "#10B981",
                "Inverse Beta (< 0.0)": "#8B5CF6"
            },
            template="plotly_dark"
        )
        
        # Add Reference Line for Market Beta = 1.0
        fig_sml.add_vline(x=1.0, line_dash="dash", line_color="#94A3B8", annotation_text="Market Beta = 1.0")
        fig_sml.update_layout(height=550, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_sml, use_container_width=True)

with tab_hist:
    st.subheader("Beta Value Distribution")
    if not df_filtered.empty:
        fig_hist = px.histogram(
            df_filtered,
            x="beta_nifty",
            nbins=25,
            color="risk_category",
            title="Frequency Distribution of Stock Betas",
            labels={"beta_nifty": "Beta (NIFTY 50)", "count": "Number of Stocks"},
            template="plotly_dark",
            color_discrete_map={
                "High Volatility (> 1.2)": "#EF4444",
                "Market-Like (0.8 - 1.2)": "#3B82F6",
                "Defensive / Low Beta (< 0.8)": "#10B981",
                "Inverse Beta (< 0.0)": "#8B5CF6"
            }
        )
        fig_hist.update_layout(height=450, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)

with tab_sector:
    st.subheader("Average Beta by Industry Sector")
    if not df_filtered.empty:
        sector_summary = df_filtered.groupby("sector")["beta_nifty"].agg(["mean", "count"]).reset_index()
        sector_summary = sector_summary.sort_values(by="mean", ascending=True)

        fig_sector = px.bar(
            sector_summary,
            x="mean",
            y="sector",
            orientation="h",
            text_auto=".2f",
            title="Sector Volatility Profile (Average Beta)",
            labels={"mean": "Average Beta", "sector": "Industry Sector"},
            color="mean",
            color_continuous_scale="Viridis",
            template="plotly_dark"
        )
        fig_sector.update_layout(height=500, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_sector, use_container_width=True)

with tab_history_chart:
    st.subheader("Historical Beta Timeline")
    if not df_history.empty and "date" in df_history.columns:
        dates_count = df_history["date"].nunique()
        st.info(f"Tracking history across **{dates_count}** daily snapshots.")

        selected_stock = st.selectbox("Select Stock for Historical Trend", sorted(df_history["company"].unique()))
        stock_hist = df_history[df_history["company"] == selected_stock].sort_values("date")

        if not stock_hist.empty:
            fig_trend = px.line(
                stock_hist,
                x="date",
                y="beta_nifty",
                markers=True,
                title=f"Beta Evolution over Time: {selected_stock}",
                labels={"date": "Date", "beta_nifty": "Beta (NIFTY 50)"},
                template="plotly_dark"
            )
            fig_trend.add_hline(y=1.0, line_dash="dash", line_color="yellow", annotation_text="Market Avg (1.0)")
            fig_trend.update_layout(height=450)
            st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Historical tracking will accumulate data daily as the automated workflow runs.")

with tab_info:
    st.subheader("Methodology, Mathematics & Critical Caveats")
    
    st.markdown(r"""
    ### 1. Mathematical Formulation (CAPM Beta)
    Beta (\(\beta\)) measures the systematic risk or volatility of a security in comparison to the broader market index (NIFTY 50).
    
    $$\beta = \frac{\text{Covariance}(R_{\text{stock}}, R_{\text{market}})}{\text{Variance}(R_{\text{market}})}$$

    Linear regression model:
    $$R_{i,t} = \alpha + \beta R_{m,t} + \epsilon_t$$

    - **\(\beta = 1.0\)**: Stock moves in perfect synchronization with the market.
    - **\(\beta > 1.0\)**: High volatility stock (amplifies market swings).
    - **\(\beta < 1.0\)**: Low volatility / Defensive cushion stock.
    - **\(R^2\)**: Proportion of stock return variance explained by index movement.

    ---

    ### 2. Operational Caveats & Disclaimers
    > ⚠️ **yfinance Unofficial Data Feed**: Data is fetched via free, web-scraped Yahoo Finance endpoints (`yfinance`). While highly reliable for personal quantitative projects, it is **not** an institutional-grade direct exchange feed.

    > ⚠️ **CAPM Limitations**: Beta assumes a strict linear relationship and normal return distribution. It does **not** capture non-linear tail risk, black swan events, or sudden liquidity shocks.
    """)

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #64748B; font-size: 0.85rem;'>Automated Indian Stocks Beta Model • Powered by Python, yfinance & Streamlit • Last Refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M IST')}</div>", unsafe_allow_html=True)
