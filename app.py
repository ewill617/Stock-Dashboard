import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Quantum Terminal", page_icon="🔘", layout="wide")

# 2. Apple-Style Glassmorphism & Smooth Tech CSS
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
    }
    .header-container {
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
    }
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px;
        border-radius: 16px;
        backdrop-filter: blur(5px);
    }
    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
    }
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 30px !important;
        padding: 10px 25px !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 10px 30px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Navigation Header
with st.container():
    st.markdown("<div class='header-container'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        st.markdown("<h3 style='margin-top:10px; color:#f8fafc;'>QUANTUM_DATA</h3>", unsafe_allow_html=True)
    with c2:
        tickers_input = st.text_input("", "MSFT, AAPL, NVDA", label_visibility="collapsed")
    with c3:
        analyze_button = st.button("SYNC DATA", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Data Engine
@st.cache_data(ttl=3600)
def get_data(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        info = t.info
        if 'shortName' not in info: return None

        bs = t.balance_sheet
        is_stmt = t.income_stmt
        
        # Financial Data Points
        total_assets = bs.loc['Total Assets'].iloc[0] if 'Total Assets' in bs.index else 0
        total_liab = bs.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in bs.index else 0
        asset_liab_ratio = total_assets / total_liab if total_liab > 0 else 0
        
        net_income = is_stmt.loc['Net Income'].iloc[0] if 'Net Income' in is_stmt.index else 0
        total_debt = bs.loc['Total Debt'].iloc[0] if 'Total Debt' in bs.index else 0
        equity = bs.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in bs.index else 0
        roic = net_income / (total_debt + equity) if (total_debt + equity) > 0 else 0

        net_margin = info.get('profitMargins', 0)
        rev = info.get('totalRevenue', 1)
