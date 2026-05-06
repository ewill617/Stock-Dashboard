import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Terminal Screener", page_icon="💻", layout="wide")

# 2. Inject Matrix CSS Theme
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #050505;
    }
    
    /* Global Font and Text Color */
    html, body, [class*="css"] {
        font-family: 'Courier New', Courier, monospace !important;
        color: #00FF41 !important;
    }
    h1, h2, h3, p, span, div, label {
        color: #00FF41 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* The Search Bar */
    .stTextInput input {
        background-color: #000000 !important;
        color: #00FF41 !important;
        border: 2px solid #00FF41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
        border-radius: 0px;
    }
    
    /* The Execute Button */
    .stButton>button {
        background-color: #000000 !important;
        color: #00FF41 !important;
        border: 2px solid #00FF41 !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
        font-weight: bold;
        font-size: 18px;
        border-radius: 0px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00FF41 !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00FF41;
    }

    /* Metric Numbers */
    [data-testid="stMetricValue"] {
        color: #00FF41 !important;
        text-shadow: 0 0 8px rgba(0, 255, 65, 0.4);
    }
    [data-testid="stMetricLabel"] {
        color: #008F11 !important;
        font-weight: bold;
    }
    
    /* Dataframe Container */
    .stDataFrame {
        border: 1px solid #00FF41;
    }
</style>
""", unsafe_allow_html=True)

# 3. Main Search Interface
st.markdown("<h1 style='text-align: center; text-shadow: 0 0 20px #00FF41; margin-bottom: 0px;'>> SYSTEM_TERMINAL :: Moat_Screener.exe</h1>", unsafe_allow_html=True)
st.write("")

# Center the search bar using columns
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    tickers_input = st.text_input("", "MSFT, AAPL, GOOG", placeholder="ENTER TARGET DESIGNATIONS...")
    analyze_button = st.button(">> EXECUTE_SCAN", use_container_width=True)

st.divider()

# 4. Data Engine
@st.cache_data(ttl=3600)
def get_data(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    info = t.info
    if 'shortName' not in info: return None

    try:
        bs = t.balance_sheet
        is_stmt = t.income_stmt
        total_assets = bs.loc['Total Assets'].iloc[0] if 'Total Assets' in bs.index else 0
        total_liab = bs.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in bs.index else 0
        asset_liab_ratio = total_assets / total_liab if total_liab > 0 else 0
        net_income = is_stmt.loc['Net Income'].iloc[0] if 'Net Income' in is_stmt.index else 0
        total_debt = bs.loc['Total Debt'].iloc[0] if 'Total Debt' in bs.index else 0
        equity = bs.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in bs.index else 0
        roic = net_income / (total_debt + equity) if (total_debt + equity) > 0 else 0
    except:
        asset_liab_ratio = 0; roic = 0

    net_margin = info.get('profitMargins', 0)
    rev = info.get('totalRevenue', 1)
    fcf = info.get('freeCashflow', 0)
    fcf_margin = fcf / rev if rev > 0 else 0
    rev_growth = info.get('revenueGrowth', 0)
    eps = info.get('trailingEps', 0)
    price = info.get('currentPrice', 1)
    earnings_yield = (eps / price) if price > 0 else 0

    return {
        "P/E Ratio": info.get('trailingPE', 0),
        "P/S Ratio": info.get('priceToSalesTrailing12Months', 0),
        "Forward P/E": info.get('forwardPE', 0),
        "Op Margin %": info.get('operatingMargins', 0) * 100,
        "Net Margin %": net_margin * 100,
        "FCF Margin %": fcf_margin * 100,
        "Current Ratio": info.get('currentRatio', 0),
        "Debt to Equity": info.get('debtToEquity', 0),
        "Asset/Liab Ratio": asset_liab_ratio,
        "Price/Book (Value)": info.get('priceToBook', 0),
        "Rev Per Share": info.get('revenuePerShare', 0),
        "EPS": eps,
        "Earnings Yield %": earnings_yield * 100,
        "Rev Growth YoY %": rev_growth * 100,
        "Rule of 40 %": (fcf_margin + rev_growth) * 100,
        "FNR Percent": (net_margin + fcf_margin + rev_growth) * 100,
        "ROE %": info.get('returnOnEquity', 0) * 100,
        "ROA %": info.get('returnOnAssets', 0) * 100,
        "ROIC %": roic * 100
    }

# 5. Execution Logic
tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

if analyze_button or tickers:
    with st.spinner("DECRYPTING FINANCIAL DATABASES..."):
        data_dict = {t: get_data(t) for t in tickers if get_data(t)}
        valid_tickers = list(data_dict.keys())
        
        if not valid_tickers:
            st.error("ERROR: TARGET NOT FOUND IN DATABASE.")
            
        # ==========================================
        # UI MODE 1: SINGLE TIER TEAR SHEET
        # ==========================================
        elif len(valid_tickers) == 1:
            t = valid_tickers[0]
            data = data_dict[t]
            
            st.markdown(f"## > TARGET_ACQUIRED :: **{t}**")
            
            # Row 1: Moat & Profitability
            st.markdown("### `[+] MOAT_AND_PROFITABILITY`")
            m1, m2, m3,
