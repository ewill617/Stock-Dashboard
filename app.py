import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Quantum Terminal", page_icon="🔘", layout="wide")

# 2. Apple-Style Glassmorphism & Smooth Tech CSS
st.markdown("""
<style>
    /* Gradient Background - Smooth Slate to Deep Charcoal */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a, #020617);
    }

    /* Navigation Bar / Header Area */
    .header-container {
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
    }

    /* Typography - Clean Sans-Serif */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Metric Cards - Apple Glass Look */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
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
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Modern Rounded Search Bar */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 30px !important;
        padding: 10px 25px !important;
        transition: all 0.3s ease;
    }

    .stTextInput input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
    }

    /* The "Execute" Button as a Sleek Gradient */
    .stButton>button {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 10px 30px !important;
        font-weight: 600 !important;
        transition: transform 0.2s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(2, 132, 199, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# 3. Floating Navigation Header
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

# 4. Data Engine (Keeping your high-speed logic)
@st.cache_data(ttl=3600)
def get_data(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    info = t.info
    if 'shortName' not in info: return None

    try:
        bs = t.balance_sheet
        is_stmt = t.income_stmt
        total_assets = bs.loc['Total Assets'].iloc[0]
        total_liab = bs.loc['Total Liabilities Net Minority Interest'].iloc[0]
        asset_liab_ratio = total_assets / total_liab
        net_income = is_stmt.loc['Net Income'].iloc[0]
        total_debt = bs.loc['Total Debt'].iloc[0] if 'Total Debt' in bs.index else 0
        equity = bs.loc['Stockholders Equity'].iloc[0]
        roic = net_income / (total_debt + equity)
    except:
        asset_liab_ratio = 0; roic = 0

    return {
        "P/E Ratio": info.get('trailingPE', 0),
        "P/S Ratio": info.get('priceToSalesTrailing12Months', 0),
        "Op Margin %": info.get('operatingMargins', 0) * 100,
        "Net Margin %": info.get('profitMargins', 0) * 100,
        "FCF Margin %": (info.get('freeCashflow', 0) / info.get('totalRevenue', 1)) * 100,
        "Current Ratio": info.get('currentRatio', 0),
        "Debt to Equity": info.get('debtToEquity', 0),
        "Asset/Liab Ratio": asset_liab_ratio,
        "Price/Book": info.get('priceToBook', 0),
        "Rev Growth YoY %": info.get('revenueGrowth', 0) * 100,
        "Rule of 40 %": ((info.get('freeCashflow', 0) / info.get('totalRevenue', 1)) + info.get('revenueGrowth', 0)) * 100,
        "FNR Percent": (
