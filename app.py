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
    /* Clean up the dataframe view */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.01);
        border-radius: 16px;
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
        fcf = info.get('freeCashflow', 0)
        fcf_margin = fcf / rev if rev > 0 else 0
        rev_growth = info.get('revenueGrowth', 0)

        return {
            "P/E Ratio": info.get('trailingPE', 0),
            "P/S Ratio": info.get('priceToSalesTrailing12Months', 0),
            "Op Margin %": info.get('operatingMargins', 0) * 100,
            "Net Margin %": net_margin * 100,
            "FCF Margin %": fcf_margin * 100,
            "Current Ratio": info.get('currentRatio', 0),
            "Debt to Equity": info.get('debtToEquity', 0),
            "Asset/Liab Ratio": asset_liab_ratio,
            "Price/Book": info.get('priceToBook', 0),
            "Rev Growth YoY %": rev_growth * 100,
            "Rule of 40 %": (fcf_margin + rev_growth) * 100,
            "FNR Percent": (net_margin + fcf_margin + rev_growth) * 100,
            "ROE %": info.get('returnOnEquity', 0) * 100,
            "ROIC %": roic * 100
        }
    except Exception:
        return None

# 5. UI Logic
tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

if analyze_button or tickers:
    with st.spinner(" "):
        data_dict = {t: get_data(t) for t in tickers if get_data(t)}
        valid_tickers = list(data_dict.keys())
        
        if not valid_tickers:
            st.warning("SYSTEM OFFLINE: INVALID TARGET.")
        elif len(valid_tickers) == 1:
            t = valid_tickers[0]
            d = data_dict[t]
            st.markdown(f"<h1 style='color:#f8fafc;'>{t} <span style='font-size:18px; color:#64748b;'>Core Intelligence Report</span></h1>", unsafe_allow_html=True)
            
            st.write("### 💎 Profitability & Moat")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("FNR %", f"{d['FNR Percent']:.2f}%")
            col2.metric("Rule of 40", f"{d['Rule of 40 %']:.2f}%")
            col3.metric("FCF Margin", f"{d['FCF Margin %']:.2f}%")
            col4.metric("ROIC", f"{d['ROIC %']:.2f}%")

            st.write("### 🛡️ Balance Sheet Health")
            col5, col6, col7, col8 = st.columns(4)
            col5.metric("Asset/Liab", f"{d['Asset/Liab Ratio']:.2f}")
            col6.metric("Debt/Equity", f"{d['Debt to Equity']:.2f}")
            col7.metric("Current Ratio", f"{d['Current Ratio']:.2f}")
            col8.metric("Rev Growth", f"{d['Rev Growth YoY %']:.2f}%")
        else:
            df = pd.DataFrame(data_dict)
            st.markdown("<h2 style='color:#f8fafc;'>Fleet Comparison Matrix</h2>", unsafe_allow
