import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Quantitative Terminal", page_icon="📈", layout="wide")

# 2. Refined Professional Terminal CSS
st.markdown("""
<style>
    /* Deep Slate Theme */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Clean Professional Monospace */
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    }
    
    /* Header & Metric Labels */
    h1, h2, h3, [data-testid="stMetricLabel"] {
        color: #808495 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Metric Values (Electric Blue) */
    [data-testid="stMetricValue"] {
        color: #58A6FF !important;
        font-size: 28px !important;
    }
    
    /* Centered Search Bar Styling */
    .stTextInput input {
        background-color: #161B22 !important;
        color: #C9D1D9 !important;
        border: 1px solid #30363D !important;
        border-radius: 4px;
        text-align: center;
        font-size: 20px;
    }
    
    /* Action Button */
    .stButton>button {
        background-color: #21262D !important;
        color: #58A6FF !important;
        border: 1px solid #30363D !important;
        border-radius: 4px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        border-color: #58A6FF !important;
        background-color: #161B22 !important;
    }

    /* Clean Dividers */
    hr {
        border-top: 1px solid #30363D !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Main Interface
st.markdown("<h2 style='text-align: center;'>QUANTITATIVE_ANALYSIS_TERMINAL</h2>", unsafe_allow_html=True)
st.write("")

# Centered Search
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    tickers_input = st.text_input("", "MSFT, AAPL, NVDA", placeholder="ENTER TICKER SYMBOLS...")
    analyze_button = st.button("RUN SYSTEM SCAN")

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

# 5. UI Logic
tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

if analyze_button or tickers:
    data_dict = {t: get_data(t) for t in tickers if get_data(t)}
    valid_tickers = list(data_dict.keys())
    
    if not valid_tickers:
        st.warning("NO DATA FOUND FOR TARGET TICKERS.")
            
    # SINGLE STOCK VIEW
    elif len(valid_tickers) == 1:
        t = valid_tickers[0]
        d = data_dict[t]
        st.markdown(f"### [ TARGET_PROFILE : {t} ]")
        
        # Grid layout for a clean terminal look
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("---")
            st.metric("FNR %", f"{d['FNR Percent']:.2f}%")
            st.metric("FCF Margin %", f"{d['FCF Margin %']:.2f}%")
            st.metric("Rev Growth %", f"{d['Rev Growth YoY %']:.2f}%")
        with col2:
            st.markdown("---")
            st.metric("Asset/Liab", f"{d['Asset/Liab Ratio']:.2f}")
            st.metric("Debt/Equity", f"{d['Debt to Equity']:.2f}")
            st.metric("Current Ratio", f"{d['Current Ratio']:.2f}")
        with col3:
            st.markdown("---")
            st.metric("P/E Ratio", f"{d['P/E Ratio']:.2f}")
            st.metric("P/S Ratio", f"{d['P/S Ratio']:.2f}")
            st.metric("ROIC %", f"{d['ROIC %']:.2f}%")

    # MULTI STOCK VIEW
    else:
        df = pd.DataFrame(data_dict)
        st.markdown("### [ COMPARISON_MATRIX ]")
        
        # Formatted Display
        display_df = df.apply(lambda x: x.map(lambda y: f"{y:.2f}"))
        max_metrics = ["Op Margin %", "Net Margin %", "FCF Margin %", "Current Ratio", "Asset/Liab Ratio", "Rev Growth YoY %", "Rule of 40 %", "FNR Percent", "ROE %", "ROIC %"]
        min_metrics = ["P/E Ratio", "P/S Ratio", "Debt to Equity", "Price/Book"]

        for metric in df.index:
            row_data = df.loc[metric]
            best_ticker = None
            if metric in max_metrics: best_ticker = row_data.idxmax()
            elif metric in min_metrics: best_ticker = row_data.idxmin()

            if best_ticker and pd.notna(row_data[best_ticker]):
                display_df.at[metric, best_ticker] = f"🏆 {display_df.at[metric, best_ticker]}"
        
        st.dataframe(display_df, use_container_width=True, height=600)
